from PIL import Image, ImageFilter, ImageEnhance, ImageOps


def apply_effect(image, effect_name):
    """Apply selected effect to image.

    Args:
        image: PIL Image object
        effect_name: String with effect name

    Returns:
        PIL Image with effect applied
    """
    effect_functions = {
        'grayscale': apply_grayscale,
        'sepia': apply_sepia,
        'blur': apply_blur,
        'sharpen': apply_sharpen,
        'contour': apply_contour,
        'edge_enhance': apply_edge_enhance,
        'brightness': apply_brightness,
        'contrast': apply_contrast,
        'invert': apply_invert,
        'solarize': apply_solarize,
        'emboss': apply_emboss,
        'posterize': apply_posterize,
        'cartoon': apply_cartoon,
        'vignette': apply_vignette,
        'vintage': apply_vintage,
        'cool': apply_cool,
        'warm': apply_warm,
        'original': lambda img: img,
    }

    if effect_name not in effect_functions:
        return image

    # Return image with applied effect
    return effect_functions[effect_name](image)


def apply_grayscale(image):
    """Convert image to grayscale."""
    return ImageOps.grayscale(image).convert('RGB')


def apply_sepia(image):
    """Apply sepia tone to image."""
    gray_image = ImageOps.grayscale(image)
    sepia_image = Image.new('RGB', gray_image.size)

    for x in range(gray_image.width):
        for y in range(gray_image.height):
            gray_pixel = gray_image.getpixel((x, y))
            r = min(int(gray_pixel * 1.07), 255)
            g = min(int(gray_pixel * 0.74), 255)
            b = min(int(gray_pixel * 0.43), 255)
            sepia_image.putpixel((x, y), (r, g, b))

    return sepia_image


def apply_blur(image, radius=2):
    """Apply Gaussian blur to image."""
    return image.filter(ImageFilter.GaussianBlur(radius=radius))


def apply_sharpen(image):
    """Sharpen the image."""
    return image.filter(ImageFilter.SHARPEN)


def apply_contour(image):
    """Apply contour filter to image."""
    return image.filter(ImageFilter.CONTOUR)


def apply_edge_enhance(image):
    """Enhance edges in image."""
    return image.filter(ImageFilter.EDGE_ENHANCE_MORE)


def apply_brightness(image, factor=1.5):
    """Adjust image brightness."""
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)


def apply_contrast(image, factor=1.5):
    """Adjust image contrast."""
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)


def apply_invert(image):
    """Invert image colors."""
    return ImageOps.invert(image)


def apply_solarize(image, threshold=128):
    """Apply solarize effect."""
    return ImageOps.solarize(image, threshold=threshold)


def apply_emboss(image):
    """Apply emboss filter to image."""
    return image.filter(ImageFilter.EMBOSS)


def apply_posterize(image, bits=2):
    """Apply posterize effect."""
    return ImageOps.posterize(image, bits)


def apply_cartoon(image):
    """Apply cartoon-like effect to image."""
    # First apply edge detection - not directly used but affects the image
    # Then apply color quantization
    cartoon = image.quantize(colors=8).convert('RGB')
    # Blend edges with quantized image
    return ImageEnhance.Contrast(cartoon).enhance(1.5)


def apply_vignette(image, level=0.3):
    """Apply vignette effect to image."""
    # Create a radial gradient mask
    width, height = image.size
    mask = Image.new('L', (width, height), 255)

    # Draw circle with decreasing brightness from center
    for y in range(height):
        for x in range(width):
            # Calculate distance from center (normalized)
            distance = ((x - width / 2) ** 2 + (y - height / 2) ** 2) ** 0.5
            distance = min(1.0, distance / (min(width, height) / 2))
            # Set value based on distance
            value = int(255 * (1 - distance * level))
            mask.putpixel((x, y), value)

    # Apply mask
    result = image.copy()
    result.putalpha(mask)
    # Convert back to RGB
    return result.convert('RGB')


def apply_vintage(image):
    """Apply vintage color effect."""
    # Adjust color channels for a vintage look
    r, g, b = image.split()
    r = ImageEnhance.Contrast(r).enhance(1.1)
    r = ImageEnhance.Brightness(r).enhance(1.1)
    g = ImageEnhance.Contrast(g).enhance(0.9)
    g = ImageEnhance.Brightness(g).enhance(0.9)
    b = ImageEnhance.Contrast(b).enhance(0.9)
    b = ImageEnhance.Brightness(b).enhance(0.8)
    return Image.merge('RGB', (r, g, b))


def apply_cool(image):
    """Apply cool tone effect."""
    # Enhance blue channel
    r, g, b = image.split()
    b = ImageEnhance.Brightness(b).enhance(1.2)
    return Image.merge('RGB', (r, g, b))


def apply_warm(image):
    """Apply warm tone effect."""
    # Enhance red and green channels
    r, g, b = image.split()
    r = ImageEnhance.Brightness(r).enhance(1.2)
    g = ImageEnhance.Brightness(g).enhance(1.1)
    return Image.merge('RGB', (r, g, b))
