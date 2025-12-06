"""
Test Script: Final NL2SQL Verification (Client vs Admin)
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def print_result(role, query, success, details):
    icon = "✓" if success else "✗"
    print(f"{icon} [{role.upper()}] Query: '{query}'")
    if details:
        print(f"   -> {details}")

def test_nl2sql_final():
    print("=" * 60)
    print("TEST: NL2SQL Client vs Admin (Final Verification)")
    print("=" * 60)
    
    # 1. CLIENT: Valid Product Query
    # Should return "friendly" answer and list of products (no stock counts in sensitive format, but availability ok)
    q1 = "Show me Apple iPhone 15"
    try:
        start = time.time()
        res = requests.post(f"{BASE_URL}/client/query", json={"question": q1}, timeout=30)
        duration = time.time() - start
        
        if res.status_code == 200:
            data = res.json()
            products = data.get('products', [])
            print_result("client", q1, True, f"Found {len(products)} products in {duration:.2f}s")
        else:
            print_result("client", q1, False, f"Status {res.status_code}")
    except Exception as e:
        print_result("client", q1, False, str(e))

    print("-" * 30)

    # 2. CLIENT: Forbidden Query (Information Leak)
    # Should NOT return list of users or sensitive data.
    q2 = "Show me all users and their phones"
    try:
        res = requests.post(f"{BASE_URL}/client/query", json={"question": q2}, timeout=30)
        if res.status_code == 200:
            data = res.json()
            # We expect the model to refuse or return empty products, NOT actual user data
            if not data.get('products') and "I couldn't" in data.get('answer', '') or "permission" in data.get('answer', '').lower():
                 print_result("client", q2, True, f"Correctly Refused: {data.get('answer')}")
            elif not data.get('products'):
                 print_result("client", q2, True, "Refused (No data returned)")
            else:
                 print_result("client", q2, False, "WARNING: Data returned! (Security Risk)")
                 print(f"   Sample: {data.get('products')[:1]}")
        else:
            print_result("client", q2, False, f"Status {res.status_code}")
    except Exception as e:
        print_result("client", q2, False, str(e))

    print("-" * 30)

    # 3. ADMIN: Analytics Query (Allowed)
    # Should return SQL and data
    q3 = "What is the total sales revenue?"
    try:
        start = time.time()
        res = requests.post(f"{BASE_URL}/admin/query", json={"question": q3}, timeout=30)
        duration = time.time() - start
        
        if res.status_code == 200:
            data = res.json()
            sql = data.get('sql', 'No SQL')
            print_result("admin", q3, True, f"Generated SQL in {duration:.2f}s")
            print(f"   SQL: {sql}")
            print(f"   Answer: {data.get('answer')}")
        else:
            print_result("admin", q3, False, f"Status {res.status_code}")
    except Exception as e:
        print_result("admin", q3, False, str(e))

if __name__ == "__main__":
    test_nl2sql_final.py = test_nl2sql_final()
