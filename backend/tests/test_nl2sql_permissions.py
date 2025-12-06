"""
Test Script: Verify NL2SQL Permissions
"""
import sys
import os
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api"

def test_permissions():
    print("=" * 60)
    print("TEST: NL2SQL Permissions")
    print("=" * 60)
    
    # 1. Test Client Permission (Should succeed for product query)
    print("\n1. Testing Client Query (Allowed): 'I want to buy apples'")
    try:
        res = requests.post(f"{BASE_URL}/client/query", json={"question": "I want to buy apples"})
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            print("Response:", json.dumps(res.json(), indent=2))
        else:
            print("Error:", res.text)
    except Exception as e:
        print(f"Failed to connect: {e}")

    # 2. Test Client Permission (Should Block/Restrict sensitive query)
    print("\n2. Testing Client Query (Restricted): 'Show total revenue'")
    try:
        res = requests.post(f"{BASE_URL}/client/query", json={"question": "Show total revenue"})
        print(f"Status: {res.status_code}")
        print("Response:", res.text[:200] + "...") # Preview
    except Exception as e:
        print(f"Failed to connect: {e}")

    # 3. Test Admin Permission (Should Allow)
    print("\n3. Testing Admin Query: 'Show total revenue'")
    try:
        res = requests.post(f"{BASE_URL}/admin/query", json={"question": "Show total revenue"})
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            print("Response:", json.dumps(res.json(), indent=2)[:500] + "...")
        else:
            print("Error:", res.text)
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    test_permissions()
