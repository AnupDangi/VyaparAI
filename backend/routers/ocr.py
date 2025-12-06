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

def extract_products_logic(image: Image.Image):
    """Extract product names and quantities from table image using EasyOCR."""
    processed = preprocess_image(image)

    # Run EasyOCR - returns list of (bbox, text, confidence)
    ocr_result = reader.readtext(processed)

    if not ocr_result:
        return []

    # Sort by Y position (rows)
    sorted_items = sorted(ocr_result, key=lambda x: x[0][0][1])

    # Group into rows
    rows = []
    current_row = []
    current_y = None
    y_threshold = 60

    for item in sorted_items:
        bbox = item[0]
        y = bbox[0][1]

        if current_y is None:
            current_row.append(item)
            current_y = y
        elif abs(y - current_y) <= y_threshold:
            current_row.append(item)
        else:
            rows.append(current_row)
            current_row = [item]
            current_y = y

    if current_row:
        rows.append(current_row)

    products = []

    for row_items in rows:
        # Sort left to right
        row_items.sort(key=lambda x: x[0][0][0])

        texts = [item[1].strip() for item in row_items]
        combined = " ".join(texts).strip()

        # Skip headers
        lower = combined.lower()
        clean_text = re.sub(r'[^a-z]', '', lower)
        header_keywords = ['product', 'prod', 'nduct', 'quantity', 'qty', 'quan', 'quantty', 
                          'sn', 'serial', 'sno', 'item', 'particular']
        if any(keyword in clean_text for keyword in header_keywords):
            continue

        # Extract quantity
        qty_match = re.search(r"(\d+)", combined)
        quantity = int(qty_match.group(1)) if qty_match else None

        # Fallback: scan cells right-to-left
        if quantity is None:
            for cell in reversed(texts):
                m = re.search(r"(\d+)", cell)
                if m:
                    quantity = int(m.group(1))
                    break

        if quantity is None:
            quantity = 1

        # Clean product name
        product_name = re.sub(r"\d+[a-zA-Z]*", " ", combined)
        product_name = re.sub(r"\b(kg|g|grams|pcs|pack|packs|packet|packets|ltr|litre|litres|ml)\b", " ", product_name, flags=re.IGNORECASE)
        product_name = re.sub(r"\s+", " ", product_name).strip()

        # Fallback for product name
        if (not product_name) and texts:
            for cell in texts:
                if not re.fullmatch(r"\s*\d+\s*[a-zA-Z]*\s*", cell):
                    product_name = cell.strip()
                    break
            if not product_name:
                product_name = texts[0].strip()

        if product_name:
            products.append({
                "product": product_name,
                "quantity": int(quantity)
            })

    # Add SN
    for i, product in enumerate(products, 1):
        product["sn"] = str(i)

    return products

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
        import traceback
        raise HTTPException(status_code=500, detail=f"OCR error: {str(e)}")

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
