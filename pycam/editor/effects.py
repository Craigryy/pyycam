from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import numpy as np

def apply_effect(image, effect_name, intensity=50):
    """
    Apply the specified effect to the given image.

    Args:
        image: PIL Image object
        effect_name: String name of the effect to apply
        intensity: Integer from 0-100 representing the strength of the effect

    Returns:
        PIL Image with the effect applied
    """
    # Normalize intensity to a 0-1 range
    intensity_factor = intensity / 100.0

    # Make a copy to avoid modifying the original
    img = image.copy()

    # Convert to RGB if in another mode
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Apply the selected effect
    if effect_name == 'grayscale':
        return ImageOps.grayscale(img).convert('RGB')

    elif effect_name == 'sepia':
        return apply_sepia(img)

    elif effect_name == 'blur':
        # Adjust blur radius based on intensity
        radius = 1 + (intensity_factor * 5)
        return img.filter(ImageFilter.GaussianBlur(radius=radius))

    elif effect_name == 'sharpen':
        enhancer = ImageEnhance.Sharpness(img)
        # Map intensity to a suitable range (1 is original, >1 is sharper)
        sharpness_factor = 1 + (intensity_factor * 2)
        return enhancer.enhance(sharpness_factor)

    elif effect_name == 'brightness':
        enhancer = ImageEnhance.Brightness(img)
        # Map intensity to a suitable range
        brightness_factor = 0.5 + intensity_factor
        return enhancer.enhance(brightness_factor)

    elif effect_name == 'contrast':
        enhancer = ImageEnhance.Contrast(img)
        # Map intensity to a suitable range
        contrast_factor = 0.5 + intensity_factor
        return enhancer.enhance(contrast_factor)

    elif effect_name == 'invert':
        return ImageOps.invert(img)

    elif effect_name == 'edge_enhance':
        return img.filter(ImageFilter.EDGE_ENHANCE)

    elif effect_name == 'emboss':
        return img.filter(ImageFilter.EMBOSS)

    elif effect_name == 'contour':
        return img.filter(ImageFilter.CONTOUR)

    # Add more effects as needed

    # Default: return the original image
    return img

def apply_sepia(image):
    """Apply a sepia tone effect to the image."""
    # Convert to numpy array for easier pixel manipulation
    img_array = np.array(image)

    # Sepia tone matrix transformation
    sepia_matrix = [
        [0.393, 0.769, 0.189],
        [0.349, 0.686, 0.168],
        [0.272, 0.534, 0.131]
    ]

    # Apply the transformation
    sepia_array = np.dot(img_array, sepia_matrix).clip(0, 255).astype(np.uint8)

    # Convert back to PIL Image
    return Image.fromarray(sepia_array)
