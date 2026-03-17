"""
Streaming Vision-Language Model Demo with CLI Arguments
"""
import base64
import argparse
import sys
from openai import OpenAI


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Stream responses from RKLLM Vision-Language Model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 example_vlm_stream.py
  python3 example_vlm_stream.py --prompt "这是什么东西?" --image-path /path/to/image.jpg
  python3 example_vlm_stream.py --base-url http://localhost:8000/v1
        """
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="这张图片是什么？用中文回答。",
        help="Query prompt (default: 这张图片是什么？用中文回答。)"
    )
    parser.add_argument(
        "--image-path",
        type=str,
        default="/home/cat/llm/rknn-llm/datasets/000000000025.jpg",
        help="Path to image file (default: /home/cat/llm/rknn-llm/datasets/000000000025.jpg)"
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default="http://localhost:8080/v1",
        help="API base URL (default: http://localhost:8080/v1)"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default="none",
        help="API key (default: none)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="rkllm-model",
        help="Model name (default: rkllm-model)"
    )
    return parser.parse_args()


def main():
    """Main function."""
    args = parse_args()

    # Validate image path
    try:
        with open(args.image_path, "rb") as image_file:
            image_data = image_file.read()
            b64_image = base64.b64encode(image_data).decode("utf-8")
            print(f"✓ Loaded image: {args.image_path} ({len(image_data)} bytes)")
    except FileNotFoundError:
        print(f"✗ Error: Image file not found: {args.image_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error reading image: {e}", file=sys.stderr)
        sys.exit(1)

    # Initialize OpenAI client
    client = OpenAI(base_url=args.base_url, api_key=args.api_key)

    print(f"✓ Connected to {args.base_url}")
    print(f"✓ Using model: {args.model}")
    print(f"\n📝 Prompt: {args.prompt}\n")
    print("=" * 70)
    print("📡 Streaming response:\n")

    try:
        # Create streaming request
        stream = client.chat.completions.create(
            model=args.model,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": args.prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
                ]
            }],
            stream=True
        )

        # Process streaming response
        token_count = 0
        for event in stream:
            if event.choices and event.choices[0].delta:
                content = event.choices[0].delta.content
                if content is not None:
                    print(content, end="", flush=True)
                    token_count += 1

        print("\n\n" + "=" * 70)
        print(f"✓ Stream completed ({token_count} tokens received)")

    except Exception as e:
        print(f"\n\n✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()