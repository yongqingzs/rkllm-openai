#!/usr/bin/env python3

"""
2D Object Grounding Demo
Detects and locates objects in images using RKLLM Vision-Language Model
"""

import os
import sys
import json
from io import BytesIO
from PIL import Image
import requests

# Import local utilities
from api_key import inference_with_openai_api
from plotting_util import plot_bounding_boxes


def main():
    print("="*70)
    print("🎯 2D Object Grounding Demo - RKLLM Vision-Language Model")
    print("="*70)
    
    # Example 1: Detecting different objects on a dining table
    print("\n📋 Example 1: Detect objects on dining table")
    print("-"*70)
    
    prompt = 'locate every instance that belongs to the following categories: "plate/dish, scallop, wine bottle, tv, bowl, spoon, air conditioner, coconut drink, cup, chopsticks, person". Report bbox coordinates in JSON format.'
    
    img_path = "/home/cat/llm/rkllm-openai/demo/assets/spatial_understanding/dining_table.png"
    
    # Check if image exists
    if not os.path.exists(img_path):
        print(f"✗ Error: Image not found at {img_path}")
        print(f"  Please ensure the image file exists.")
        return False
    
    # Call RKLLM API
    try:
        print(f"\n📸 Processing image: {img_path}")
        model_response = inference_with_openai_api(img_path, prompt)
        print(f"\n✓ Model Response:")
        print("="*70)
        print(model_response)
        print("="*70)
        
        # Try to load and visualize the image with bounding boxes
        try:
            if img_path.startswith(('http://', 'https://')):
                response = requests.get(img_path, timeout=10)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))
            else:
                image = Image.open(img_path)
            
            print(f"\n🖼️  Image loaded: {image.size}")
            image.thumbnail([640, 640], Image.Resampling.LANCZOS)
            
            # Plot bounding boxes
            print(f"\n📊 Plotting results...")
            plot_bounding_boxes(image, model_response)
            print(f"✓ Visualization complete")
            
        except Exception as e:
            print(f"\n⚠️  Warning: Could not visualize results: {e}")
            print(f"  But the model response above is valid.")
        
        return True
        
    except Exception as e:
        print(f"✗ Error during inference: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)