from pathlib import Path

import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer


# --------------- CONFIG ---------------

BACKEND_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BACKEND_DIR / "models" / "all-MiniLM-L6-v2"
MODEL_PATH = MODEL_DIR / "onnx" / "model.onnx"
TOKENIZER_PATH = MODEL_DIR / "tokenizer.json"

MAX_LENGTH = 256


# --------------- VALIDATION ---------------

if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Embedding model not found: {MODEL_PATH}")

if not TOKENIZER_PATH.exists():
    raise FileNotFoundError(f"Tokenizer not found: {TOKENIZER_PATH}")


# --------------- TOKENIZER ---------------

tokenizer = Tokenizer.from_file(str(TOKENIZER_PATH))
tokenizer.enable_truncation(max_length=MAX_LENGTH)
tokenizer.enable_padding(length=MAX_LENGTH)


# --------------- ONNX SESSION ---------------

session = ort.InferenceSession(
    str(MODEL_PATH),
    providers=["CPUExecutionProvider"],
)

input_names = {
    model_input.name
    for model_input in session.get_inputs()
}


# --------------- POOLING ---------------

def mean_pool(
    token_embeddings: np.ndarray,
    attention_mask: np.ndarray,
) -> np.ndarray:
    mask = attention_mask[:, :, None].astype(np.float32)

    summed = np.sum(
        token_embeddings * mask,
        axis=1,
    )

    counts = np.sum(mask, axis=1)
    counts = np.clip(counts, 1e-9, None)

    return summed / counts


# --------------- NORMALIZATION ---------------

def normalize(embeddings: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(
        embeddings,
        axis=1,
        keepdims=True,
    )

    norms = np.clip(norms, 1e-12, None)

    return embeddings / norms


# --------------- EMBEDDING ---------------

def embed_texts(texts: list[str]) -> np.ndarray:
    encodings = tokenizer.encode_batch(texts)

    input_ids = np.asarray(
        [encoding.ids for encoding in encodings],
        dtype=np.int64,
    )

    attention_mask = np.asarray(
        [encoding.attention_mask for encoding in encodings],
        dtype=np.int64,
    )

    inputs = {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
    }

    if "token_type_ids" in input_names:
        inputs["token_type_ids"] = np.asarray(
            [encoding.type_ids for encoding in encodings],
            dtype=np.int64,
        )

    token_embeddings = session.run(
        None,
        inputs,
    )[0]

    embeddings = mean_pool(
        token_embeddings,
        attention_mask,
    )

    embeddings = normalize(embeddings)

    return embeddings.astype(np.float32)
