# EasyOCR Table Extraction - Setup Instructions

## Quick Start

### 1. Create Virtual Environment
```bash
python -m venv venv_easy
```

### 2. Activate Virtual Environment
**Windows:**
```bash
.\venv_easy\Scripts\activate
```

**Linux/Mac:**
```bash
source venv_easy/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Service
```bash
python ocr_service_easy.py
```

Server will start on `http://localhost:8001`

**Note:** On first run, EasyOCR will download AI models (~100MB). This takes 2-5 minutes and happens only once.

## API Usage

### Extract Products from Image
```bash
curl -X POST -F "file=@test.jpg" http://localhost:8001/extract
```

### Debug (See All OCR Detections)
```bash
curl -X POST -F "file=@test.jpg" http://localhost:8001/debug
```

## Response Format

```json
{
  "items": [
    {"sn": "1", "product": "Rice", "quantity": 1},
    {"sn": "2", "product": "Toothpaste", "quantity": 2},
    {"sn": "3", "product": "Chocolate", "quantity": 3}
  ],
  "total_items": 3
}
```

## Features

✅ Handwritten text recognition
✅ Handwritten number detection
✅ Auto-incrementing serial numbers
✅ Header row filtering
✅ Product name and quantity extraction

## System Requirements

- Python 3.8+
- 2GB RAM minimum
- Internet connection (first run only, for model download)

## Troubleshooting

**Models downloading slowly?**
- First run downloads ~100MB of AI models
- Wait 2-5 minutes, it's a one-time process

**Import errors?**
- Make sure virtual environment is activated
- Run: `pip install -r requirements.txt` again

**Server won't start?**
- Check if port 8001 is available
- Try changing port in `ocr_service_easy.py` (line 193)
