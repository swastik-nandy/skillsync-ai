from pathlib import Path

from huggingface_hub import snapshot_download


MODEL_REPO = "sentence-transformers/all-MiniLM-L6-v2"

BACKEND_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BACKEND_DIR / "models" / "all-MiniLM-L6-v2"

REQUIRED_FILES = [
    "onnx/model.onnx",
    "tokenizer.json",
    "tokenizer_config.json",
    "special_tokens_map.json",
    "vocab.txt",
    "config.json",
]


def main() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Downloading {MODEL_REPO}...")
    print(f"Destination: {MODEL_DIR}")

    snapshot_download(
        repo_id=MODEL_REPO,
        local_dir=MODEL_DIR,
        allow_patterns=REQUIRED_FILES,
    )

    print("Model downloaded successfully.")


if __name__ == "__main__":
    main()