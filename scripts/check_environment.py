import sys


def get_version(package_name, import_name=None):
    if import_name is None:
        import_name = package_name
    try:
        mod = __import__(import_name)
        return getattr(mod, "__version__", "Installed (unknown version)")
    except ImportError:
        return "Not installed"


def check_environment():
    print("FoodFresh AI Environment")
    print("------------------------")
    print(f"Python: {sys.version.split()[0]}")

    # PyTorch
    torch_ver = get_version("torch")
    print(f"PyTorch: {torch_ver}")

    # TorchVision
    tv_ver = get_version("torchvision")
    print(f"TorchVision: {tv_ver}")

    # XGBoost
    xgb_ver = get_version("xgboost")
    print(f"XGBoost: {xgb_ver}")

    # NumPy
    numpy_ver = get_version("numpy")
    print(f"NumPy: {numpy_ver}")

    # Pandas
    pandas_ver = get_version("pandas")
    print(f"Pandas: {pandas_ver}")

    # Scikit-learn
    sklearn_ver = get_version("scikit-learn", "sklearn")
    print(f"Scikit-learn: {sklearn_ver}")

    # FastAPI
    fastapi_ver = get_version("fastapi")
    print(f"FastAPI: {fastapi_ver}")

    # Pillow
    pil_ver = get_version("pillow", "PIL")
    print(f"Pillow: {pil_ver}")

    # CUDA and GPU detection
    cuda_available = False
    gpu_name = "None"
    try:
        import torch

        cuda_available = torch.cuda.is_available()
        if cuda_available:
            gpu_name = torch.cuda.get_device_name(0)
    except Exception as e:
        gpu_name = f"Error detecting GPU: {e}"

    print(f"CUDA available: {'Yes' if cuda_available else 'No'}")
    print(f"GPU: {gpu_name}")


if __name__ == "__main__":
    check_environment()
