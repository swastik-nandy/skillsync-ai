import torch

print("CUDA available:", torch.cuda.is_available())
print("Device count:", torch.cuda.device_count())
print("Device name:", torch.cuda.get_device_name(0))
print("Memory allocated (MB):", round(torch.cuda.memory_allocated(0) / 1024**2, 2))
print("Memory reserved (MB):", round(torch.cuda.memory_reserved(0) / 1024**2, 2))
