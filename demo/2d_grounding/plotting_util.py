#!apt-get install fonts-source-han-sans-jp # For Source Han Sans (Japanese)

import json
import random
import io
import ast
import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from PIL import ImageColor
import xml.etree.ElementTree as ET

additional_colors = [colorname for (colorname, colorcode) in ImageColor.colormap.items()]


def get_font(size=14):
    """Get a font that supports CJK characters."""
    font_paths = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/System/Library/Fonts/PingFang.ttc",  # macOS
        "C:\\Windows\\Fonts\\msyh.ttc",  # Windows
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size=size)
            except Exception as e:
                print(f"Warning: Could not load font {font_path}: {e}")
    
    # Fall back to default font
    print("Warning: Could not find CJK font, using default font")
    try:
        return ImageFont.load_default()
    except:
        return None


def parse_json(json_output):
    """Parse JSON output, removing markdown formatting."""
    if not json_output:
        return "[]"
    
    # Remove markdown code fence
    if "```json" in json_output:
        json_output = json_output.split("```json")[1]
    if "```" in json_output:
        json_output = json_output.split("```")[0]
    
    return json_output.strip()


def decode_json_points(text: str):
    """Parse coordinate points from text format"""
    try:
        # 清理markdown标记
        text = parse_json(text)
        
        # 解析JSON
        data = json.loads(text)
        points = []
        labels = []
        
        if not isinstance(data, list):
            data = [data]
        
        for item in data:
            if isinstance(item, dict) and "point_2d" in item:
                x, y = item["point_2d"]
                points.append([x, y])
                
                # 获取label，如果没有则使用默认值
                label = item.get("label", f"point_{len(points)}")
                labels.append(label)
        
        return points, labels
        
    except Exception as e:
        print(f"Error parsing points: {e}")
        return [], []
        

def plot_bounding_boxes(im, bounding_boxes):
    """
    Plots bounding boxes on an image with labels, using PIL.

    Args:
        im: PIL Image object
        bounding_boxes: JSON string with bounding boxes
    """
    try:
        # Load the image
        img = im
        width, height = img.size
        print(f"Image size: {width}x{height}")
        
        # Create a drawing object
        draw = ImageDraw.Draw(img)

        # Define a list of colors
        colors = [
            'red', 'green', 'blue', 'yellow', 'orange', 'pink', 'purple', 'brown', 'gray',
            'beige', 'turquoise', 'cyan', 'magenta', 'lime', 'navy', 'maroon', 'teal',
            'olive', 'coral', 'lavender', 'violet', 'gold', 'silver',
        ] + additional_colors

        # Parse JSON
        json_text = parse_json(bounding_boxes)
        
        try:
            json_output = json.loads(json_text)
        except json.JSONDecodeError:
            print(f"Warning: Could not parse JSON, trying ast.literal_eval")
            try:
                json_output = ast.literal_eval(json_text)
            except:
                print(f"Error: Could not parse bounding boxes JSON")
                print(f"Input was: {bounding_boxes[:200]}")
                return

        if not isinstance(json_output, list):
            json_output = [json_output]

        # Get font
        font = get_font(size=14)

        # Iterate over the bounding boxes
        for i, bounding_box in enumerate(json_output):
            if not isinstance(bounding_box, dict):
                continue
                
            # Select a color from the list
            color = colors[i % len(colors)]

            # Get bbox coordinates
            if "bbox_2d" not in bounding_box:
                print(f"Warning: bbox_2d not found in bounding_box {i}")
                continue
            
            bbox = bounding_box["bbox_2d"]
            
            # Handle different coordinate formats
            # Try to determine if coordinates are normalized (0-1) or absolute (0-1000) or pixel values
            if len(bbox) != 4:
                print(f"Warning: Invalid bbox format: {bbox}")
                continue
            
            x1, y1, x2, y2 = bbox
            
            # Auto-detect coordinate scale
            max_coord = max(abs(x1), abs(y1), abs(x2), abs(y2))
            if max_coord <= 1.0:
                # Normalized coordinates (0-1)
                abs_x1, abs_y1 = int(x1 * width), int(y1 * height)
                abs_x2, abs_y2 = int(x2 * width), int(y2 * height)
            elif max_coord <= 100.0:
                # Possibly percentage (0-100)
                abs_x1, abs_y1 = int(x1 / 100 * width), int(y1 / 100 * height)
                abs_x2, abs_y2 = int(x2 / 100 * width), int(y2 / 100 * height)
            else:
                # Pixel coordinates or scaled (0-1000)
                # Check against image dimensions
                if max_coord > max(width, height) * 2:
                    # Probably 0-1000 scale
                    abs_x1, abs_y1 = int(x1 / 1000 * width), int(y1 / 1000 * height)
                    abs_x2, abs_y2 = int(x2 / 1000 * width), int(y2 / 1000 * height)
                else:
                    # Pixel coordinates
                    abs_x1, abs_y1 = int(x1), int(y1)
                    abs_x2, abs_y2 = int(x2), int(y2)

            # Ensure proper ordering
            if abs_x1 > abs_x2:
                abs_x1, abs_x2 = abs_x2, abs_x1
            if abs_y1 > abs_y2:
                abs_y1, abs_y2 = abs_y2, abs_y1

            # Draw the bounding box
            draw.rectangle(
                ((abs_x1, abs_y1), (abs_x2, abs_y2)), 
                outline=color, width=3
            )

            # Draw the label
            label = bounding_box.get("label", f"Object {i+1}")
            if font:
                draw.text((abs_x1 + 8, abs_y1 + 6), label, fill=color, font=font)
            else:
                draw.text((abs_x1 + 8, abs_y1 + 6), label, fill=color)

        # Display the image
        print("✓ Bounding boxes plotted successfully")
        # img.show()
        img.save('result.png')
        
    except Exception as e:
        print(f"Error plotting bounding boxes: {e}")
        import traceback
        traceback.print_exc()


def plot_points(im, text):
    """Plot point markers on image."""
    try:
        img = im
        width, height = img.size
        draw = ImageDraw.Draw(img)
        colors = [
            'red', 'green', 'blue', 'yellow', 'orange', 'pink', 'purple', 'brown', 'gray',
            'beige', 'turquoise', 'cyan', 'magenta', 'lime', 'navy', 'maroon', 'teal',
            'olive', 'coral', 'lavender', 'violet', 'gold', 'silver',
        ] + additional_colors

        points, descriptions = decode_json_points(text)
        print("Parsed points: ", points)
        print("Parsed descriptions: ", descriptions)
        
        if not points:
            img.show()
            return

        font = get_font(size=14)

        for i, point in enumerate(points):
            color = colors[i % len(colors)]
            abs_x = int(point[0]) if point[0] > 10 else int(point[0] * width)
            abs_y = int(point[1]) if point[1] > 10 else int(point[1] * height)
            radius = 5
            draw.ellipse([(abs_x - radius, abs_y - radius), (abs_x + radius, abs_y + radius)], fill=color)
            
            if font:
                draw.text((abs_x - 20, abs_y + 6), descriptions[i], fill=color, font=font)
            else:
                draw.text((abs_x - 20, abs_y + 6), descriptions[i], fill=color)
        
        # img.show()
        img.save('result.png') 
    except Exception as e:
        print(f"Error plotting points: {e}")
        import traceback
        traceback.print_exc()


def plot_points_json(im, text):
    """Plot points from JSON format."""
    try:
        img = im
        width, height = img.size
        draw = ImageDraw.Draw(img)
        colors = [
            'red', 'green', 'blue', 'yellow', 'orange', 'pink', 'purple', 'brown', 'gray',
            'beige', 'turquoise', 'cyan', 'magenta', 'lime', 'navy', 'maroon', 'teal',
            'olive', 'coral', 'lavender', 'violet', 'gold', 'silver',
        ] + additional_colors
        font = get_font(size=14)

        text = parse_json(text)
        data = json.loads(text)
        
        for item in data:
            point_2d = item['point_2d']
            label = item['label']
            x = int(point_2d[0]) if point_2d[0] > 10 else int(point_2d[0] * width)
            y = int(point_2d[1]) if point_2d[1] > 10 else int(point_2d[1] * height)
            radius = 5
            draw.ellipse([(x - radius, y - radius), (x + radius, y + radius)], fill=colors[0])
            
            if font:
                draw.text((x + 2*radius, y + 2*radius), label, fill=colors[0], font=font)
            else:
                draw.text((x + 2*radius, y + 2*radius), label, fill=colors[0])
        
        img.show()
    except Exception as e:
        print(f"Error plotting point JSON: {e}")
        import traceback
        traceback.print_exc()