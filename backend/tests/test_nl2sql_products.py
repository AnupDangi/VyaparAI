"""
Test Script: Verify NL2SQL for Specific Products
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_products_nl2sql():
    print("=" * 60)
    print("TEST: NL2SQL Specific Products")
    print("=" * 60)
    
    questions = [
        "Show me Apple iPhone 15",
        "What is the price of Samsung Galaxy S24?",
        "Do you have Sony Headphones?",
        "List all Electronics products"
    ]
    
    for q in questions:
        print(f"\nQuery: '{q}'")
        try:
            res = requests.post(f"{BASE_URL}/client/query", json={"question": q}, timeout=30)
            if res.status_code == 200:
                data = res.json()
                print("✓ Success")
                # print(json.dumps(data, indent=2)) 
                # Just show the rows count or names to be concise
                if 'data' in data and data['data']:
                    print(f"  -> Found {len(data['data'])} rows.")
                    for row in data['data'][:3]: # Show first 3 matches
                        print(f"     - {row}")
                else:
                    print("  -> No results found.")
            else:
                print(f"✗ Failed: {res.status_code} - {res.text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_products_nl2sql()
