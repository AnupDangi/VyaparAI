from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
import numpy as np
import cv2
import easyocr
import re
import io

router = APIRouter()

# Initialize EasyOCR (English language, GPU=False for CPU)
# We initialize it at module level so it loads only once.
print("Initializing EasyOCR... This may take a minute on first run.")
reader = easyocr.Reader(['en'], gpu=False)
print("EasyOCR initialized successfully!")

def preprocess_image(image: Image.Image):
    """Preprocessing for better OCR."""
    img_np = np.array(image)
    
    # Convert to grayscale
    if len(img_np.shape) == 3:
        img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    
    # Upscale
    img_np = cv2.resize(img_np, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    
    # Enhance contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    img_np = clahe.apply(img_np)
    
    return img_np



# ... (Previous imports and EasyOCR init remain) ... 

def extract_products_logic(image: Image.Image):
    """
    Extract product names and quantities using EasyOCR only (No LLM).
    Uses heuristics to parse the text lines.
    """
    processed = preprocess_image(image)

    # 1. Raw Text Extraction (EasyOCR)
    # detail=0 returns a list of strings found
    ocr_result = reader.readtext(processed, detail=0) 
    
    print(f"DEBUG: Raw OCR Result List: {ocr_result}")
    
    if not ocr_result:
        return []

    # 2. Heuristic Parsing
    items = []
    
    for i, line in enumerate(ocr_result, 1):
        line = line.strip()
        if not line:
            continue
            
        # Heuristic: Try to find a number in the line for quantity
        # Patterns: "2 kg Rice", "Rice 2kg", "2 Rice", "Rice 2"
        
        # Check for leading number
        match_leading = re.match(r'^(\d+)\s*(kg|g|l|ml|pack|pc|pcs)?\s+(.+)$', line, re.IGNORECASE)
        # Check for trailing number
        match_trailing = re.search(r'(.+?)\s+(\d+)\s*(kg|g|l|ml|pack|pc|pcs)?$', line, re.IGNORECASE)
        
        quantity = 1
        product_name = line
        
        if match_leading:
            qty_str = match_leading.group(1)
            product_name = match_leading.group(3)
            try:
                quantity = int(qty_str)
            except:
                pass
        elif match_trailing:
            qty_str = match_trailing.group(2)
            product_name = match_trailing.group(1)
            try:
                quantity = int(qty_str)
            except:
                pass
        
        # Clean up product name (remove special chars if any)
        product_name = re.sub(r'[^\w\s]', '', product_name).strip()
        
        if product_name:
            items.append({
                "sn": str(len(items) + 1),
                "product": product_name,
                "quantity": quantity
            })
            
    return items

@router.post("/extract")
async def extract_text(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        items = extract_products_logic(image)
        
        return JSONResponse({
            "items": items,
            "total_items": len(items)
        })
    except Exception as e:
        print(f"OCR Endpoint Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/debug")
async def debug_ocr(file: UploadFile = File(...)):
    """Debug endpoint - shows what EasyOCR detects."""
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        processed = preprocess_image(image)
        ocr_result = reader.readtext(processed)
        
        if not ocr_result:
            return JSONResponse({"message": "NO TEXT DETECTED!"})
        
        detections = []
        for i, item in enumerate(ocr_result, 1):
            bbox = item[0]
            text = item[1]
            conf = item[2]
            
            detections.append({
                "index": i,
                "text": text,
                "x": int(bbox[0][0]),
                "y": int(bbox[0][1]),
                "confidence": f"{conf:.4f}"
            })
        
        return JSONResponse({
            "total_detections": len(detections),
            "message": "EasyOCR detections",
            "detections": detections
        })
    
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=f"OCR Debug error: {str(e)}")
