import sys
print("Step 0: Starting python script", flush=True)

try:
    print("Step 1: Importing os and sys", flush=True)
    import os
    print("Step 2: Importing math", flush=True)
    import math
    print("Step 3: Importing torch...", flush=True)
    import torch
    print(f"Step 4: Torch imported successfully! Version: {torch.__version__}", flush=True)
    print("Step 5: Checking cuda...", flush=True)
    cuda_avail = torch.cuda.is_available()
    print(f"Step 6: CUDA available: {cuda_avail}", flush=True)
    if cuda_avail:
        print(f"Step 7: GPU: {torch.cuda.get_device_name(0)}", flush=True)
except Exception as e:
    print(f"Error encountered: {e}", flush=True)

print("Step 8: Complete!", flush=True)
