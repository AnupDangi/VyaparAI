
import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock, patch
import os

client = TestClient(app)

# --- Fixtures ---

@pytest.fixture
def mock_db_connection():
    with patch("routers.auth.get_db_connection") as mock_conn_auth, \
         patch("routers.products.get_db_connection") as mock_conn_prod:
         
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        # Setup standard mock returns
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None # Default no result
        mock_cursor.fetchall.return_value = []
        
        mock_conn_auth.return_value = mock_conn
        mock_conn_prod.return_value = mock_conn
        
        yield mock_cursor

@pytest.fixture
def mock_cloudinary():
    with patch("cloudinary.uploader.upload") as mock_upload:
        mock_upload.return_value = {"secure_url": "http://res.cloudinary.com/demo/image/upload/sample.jpg"}
        yield mock_upload

# --- Tests ---

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "VyaparAI Backend is running 🚀"}

# 1. Admin Auth Tests
def test_admin_signup_success(mock_db_connection):
    # Setup mock to return no existing admin, then return created admin
    request_data = {
        "adminId": "admin_test",
        "fullName": "Test Admin",
        "email": "test@admin.com",
        "password": "password123",
        "storeName": "Test Store",
        "description": "Test Desc",
        "category": "Retail",
        "address": "123 Test St",
        "phone": "1234567890"
    }
    
    # We mock fetchone sequence: 
    # 1. Check if admin exists (None) 
    # 2. Insert Admin (Return new admin data)
    mock_db_connection.fetchone.side_effect = [
        None, 
        {"id": 1, "admin_id": "admin_test", "name": "Test Admin", "email": "test@admin.com"}
    ]
    
    response = client.post("/admin/signup", json=request_data)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["admin"]["admin_id"] == "admin_test"

def test_admin_signup_duplicate(mock_db_connection):
    # Setup mock to return existing admin
    mock_db_connection.fetchone.return_value = {"id": 1}
    
    request_data = {
        "adminId": "existing_admin",
        "fullName": "Test Admin",
        "email": "test@admin.com",
        "password": "password123",
        "storeName": "Test Store",
        "description": "Desc",
        "category": "Cat",
        "address": "Addr",
        "phone": "123"
    }
    
    response = client.post("/admin/signup", json=request_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_admin_login_success(mock_db_connection):
    # Mock finding admin
    fake_hash = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW" # bcrypt hash for 'secret'
    
    mock_db_connection.fetchone.side_effect = [
        {"id": 1, "name": "Test Admin", "email": "test@admin.com", "password_hash": fake_hash}, # Find by ID
        {"name": "Test Store"} # Fetch store
    ]
    
    # We must patch verify because we can't easily match the hash in the mock without real hashing
    with patch("passlib.context.CryptContext.verify", return_value=True):
        response = client.post("/admin/login", json={"adminId": "admin_test", "password": "secret"})
        
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["admin"]["storeName"] == "Test Store"

# 2. Product Tests
def test_get_products(mock_db_connection):
    mock_db_connection.fetchall.return_value = [
        {"id": 1, "title": "Milk", "price": 50, "stock": 10, "image_url": "http://img.com/1.jpg"}
    ]
    response = client.get("/api/products/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Milk"

def test_create_product(mock_db_connection, mock_cloudinary):
    mock_db_connection.fetchone.return_value = {"id": 1, "title": "New Product", "image_url": "http://res.cloudinary.com/demo/image/upload/sample.jpg"}
    
    # Prepare form data
    data = {
        "title": "New Product",
        "price": "100",
        "stock": "20",
        "category": "Grocery",
        "description": "Fresh"
    }
    files = {"image": ("test.jpg", b"fake content", "image/jpeg")}
    
    response = client.post("/api/products/", data=data, files=files)
    
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["product"]["image_url"] is not None

# 3. Bookings Tests
def test_get_bookings():
    response = client.get("/api/bookings/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# 4. Customers Tests
def test_get_customers():
    response = client.get("/api/customers/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
