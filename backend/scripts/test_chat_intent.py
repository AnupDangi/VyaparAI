import requests
import json

BASE_URL = "http://localhost:8000/api/nl2sql/client/query"

def test_intent():
    print("Testing Chat Intent...")
    
    # Test 1: Greeting
    q1 = "Hi"
    print(f"\nQuery: {q1}")
    res1 = requests.post(BASE_URL, json={"question": q1})
    if res1.status_code == 200:
        data = res1.json()
        print(f"Answer: {data.get('answer')}")
        if not data.get('sql') and "VyaparAI" in data.get('answer', ''):
             print("✅ Greeting Intent: PASS")
        else:
             print(f"❌ Greeting Intent: FAIL (SQL: {data.get('sql')})")
    else:
        print(f"Error {res1.status_code}: {res1.text}")

    # Test 2: Product Query
    q2 = "Show me phones"
    print(f"\nQuery: {q2}")
    res2 = requests.post(BASE_URL, json={"question": q2})
    if res2.status_code == 200:
        data = res2.json()
        print(f"Answer: {data.get('answer')}")
        if data.get('products'):
             print(f"✅ Search Intent: PASS (Found {len(data['products'])} products)")
        else:
             print("❌ Search Intent: FAIL (No products)")

if __name__ == "__main__":
    test_intent()
