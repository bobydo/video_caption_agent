"""
Utility functions for subtitle rendering
"""

from PIL import Image, ImageDraw, ImageFont


def create_subtitle_image(text: str, width: int, height: int, 
                         font_size: int, stroke_width: int, 
                         font_path: str) -> Image.Image:
    """
    Create PIL image with Chinese subtitle
    
    Args:
        text: Subtitle text
        width: Image width
        height: Image height
        font_size: Font size in pixels
        stroke_width: Outline thickness
        font_path: Path to font file
    
    Returns:
        PIL Image with subtitle
    """
    # Create transparent image
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Load font
    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception as e:
        print(f"⚠️  Font load error: {e}, using default")
        font = ImageFont.load_default()
    
    # Calculate text position (center)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Draw black outline/shadow
    for adj_x in range(-stroke_width, stroke_width + 1):
        for adj_y in range(-stroke_width, stroke_width + 1):
            if adj_x != 0 or adj_y != 0:
                draw.text((x + adj_x, y + adj_y), text, 
                         font=font, fill='#000000')
    
    # Draw white main text
    draw.text((x, y), text, font=font, fill='#FFFFFF')
    
    return img
