"""
Test Script: Verify OCR with Real Image
"""
import requests
import os

BASE_URL = "http://localhost:8000/api"
IMAGE_PATH = "/Users/anupdangi/.gemini/antigravity/brain/ac5460bc-83d9-43fb-973a-1c363f6a0450/uploaded_image_1765050085478.png"

def test_ocr_real():
    print("=" * 60)
    print("TEST: OCR with LLM Correction")
    print("=" * 60)
    
    if not os.path.exists(IMAGE_PATH):
        print(f"Image not found at {IMAGE_PATH}")
        return

    try:
        with open(IMAGE_PATH, "rb") as f:
            files = {"file": ("test_image.png", f, "image/png")}
            print("Sending image to /api/ocr/extract ...")
            print("(This involves EasyOCR + LLM, might take 10-15s)")
            
            res = requests.post(f"{BASE_URL}/ocr/extract", files=files, timeout=60)
            
            if res.status_code == 200:
                print("✓ Success!")
                print("Response:", res.json())
            else:
                print(f"✗ Failed: {res.status_code}")
                print(res.text)
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_ocr_real()
