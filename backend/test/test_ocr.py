
import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock, patch
import os

client = TestClient(app)

# Note: We are testing the real OCR logic here, so we won't mock easyocr's reader entirely,
# but we need to ensure the DB and Cloudinary mocks are still in place so we don't crash 
# on app startup dependencies or side effects.

@pytest.fixture
def mock_db_connection():
    with patch("routers.auth.get_db_connection") as mock_conn_auth, \
         patch("routers.products.get_db_connection") as mock_conn_prod:
         
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn_auth.return_value = mock_conn
        mock_conn_prod.return_value = mock_conn
        yield mock_cursor

@pytest.fixture
def mock_cloudinary():
    with patch("cloudinary.uploader.upload") as mock_upload:
        mock_upload.return_value = {"secure_url": "http://mock.url"}
        yield mock_upload

def test_ocr_extract_endpoint(mock_db_connection, mock_cloudinary):
    # Ensure test image exists
    img_path = "test.jpg"
    if not os.path.exists(img_path):
        pytest.skip(f"Test image not found at {img_path}")

    with open(img_path, "rb") as f:
        response = client.post(
            "/api/ocr/extract",
            files={"file": ("test.jpg", f, "image/jpeg")}
        )
    
    # Assertions
    assert response.status_code == 200, f"Failed with status {response.status_code}: {response.text}"
    data = response.json()
    assert "items" in data
    assert "total_items" in data
    assert isinstance(data["items"], list)
    
    # Check if any items were actually detected 
    # (Since we are using a real image 'test2.jpg', we expect some text if it's a good image)
    # If the image is empty or bad, this might be 0, but the call itself succeeded.
    print(f"Detected items: {data['items']}")

def test_ocr_debug_endpoint(mock_db_connection, mock_cloudinary):
    img_path = "test.jpg"
    if not os.path.exists(img_path):
        pytest.skip(f"Test image not found at {img_path}")

    with open(img_path, "rb") as f:
        response = client.post(
            "/api/ocr/debug",
            files={"file": ("test.jpg", f, "image/jpeg")}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "detections" in data
    assert "total_detections" in data
