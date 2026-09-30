"""
FoodFresh AI - Hybrid Vision Preprocessing
Image decoding, bounding box cropping, and tensor transformation pipelines.
"""

from io import BytesIO
from typing import Optional, Tuple, Union
from PIL import Image, ImageOps
import torch
import torchvision.transforms as T

from ml.hybrid_vision.schemas import BoundingBox

# Standard ImageNet normalization for PyTorch vision models
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# Preprocessing transforms for standard 224x224 models (ResNet-50 and ResNet-18)
STANDARD_224_TRANSFORMS = T.Compose([
    T.Resize((224, 224)),
    T.ToTensor(),
    T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
])


def load_image_rgb(image_input: Union[bytes, str, Image.Image]) -> Image.Image:
    """
    Load and normalize an image into a clean PIL RGB Image.
    Handles bytes, filepaths, and existing PIL Image objects with EXIF orientation correction.
    """
    if isinstance(image_input, Image.Image):
        image = image_input
    elif isinstance(image_input, (bytes, bytearray)):
        image = Image.open(BytesIO(image_input))
    elif isinstance(image_input, str):
        image = Image.open(image_input)
    else:
        raise ValueError(f"Unsupported image input type: {type(image_input)}")

    # Apply EXIF rotation if present (e.g. from mobile phone cameras)
    image = ImageOps.exif_transpose(image)
    if image.mode != "RGB":
        image = image.convert("RGB")
    return image


def crop_bounding_box(
    image: Image.Image,
    box: BoundingBox,
    margin_ratio: float = 0.08
) -> Image.Image:
    """
    Crop the image around a detected bounding box with an optional proportional margin.
    Clamps coordinates strictly within the image boundaries.
    """
    w, h = image.size
    box_w = box.xmax - box.xmin
    box_h = box.ymax - box.ymin

    dx = int(box_w * margin_ratio)
    dy = int(box_h * margin_ratio)

    xmin = max(0, box.xmin - dx)
    ymin = max(0, box.ymin - dy)
    xmax = min(w, box.xmax + dx)
    ymax = min(h, box.ymax + dy)

    # Ensure valid crop dimension
    if xmax <= xmin or ymax <= ymin:
        return image

    return image.crop((xmin, ymin, xmax, ymax))


def preprocess_for_resnet(image: Image.Image, device: torch.device) -> torch.Tensor:
    """
    Apply standard ResNet normalization (224x224) and return batch tensor on target device.
    """
    tensor = STANDARD_224_TRANSFORMS(image)
    return tensor.unsqueeze(0).to(device)
