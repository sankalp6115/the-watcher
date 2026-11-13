import sys
import subprocess
import os

def ocr(img_path):
    if not os.path.exists(img_path):
        print(f"Error: Image path '{img_path}' does not exist.", file=sys.stderr)
        return ""

    try:
        result = subprocess.run(
            ["tesseract", img_path, "stdout"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"OCR failed for {img_path} (Tesseract error): {e.stderr.strip()}", file=sys.stderr)
        return ""
    except FileNotFoundError:
        print("Error: Tesseract is not installed or not in system PATH.", file=sys.stderr)
        return ""
    except Exception as e:
        print(f"OCR failed for {img_path}: {e}", file=sys.stderr)
        return ""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ocr.py <image_path>")
        sys.exit(1)
        
    target_img = sys.argv[1]
    extracted_text = ocr(target_img)
    print(extracted_text)