import requests
import json

BASE_URL = "http://localhost:8000/api/nl2sql/client/query"

def test_refusal():
    print("Testing Chat Refusal Persona...")
    
    # Test 1: Code Request
    q1 = "Write a python script to sort a list"
    print(f"\nQuery: {q1}")
    res1 = requests.post(BASE_URL, json={"question": q1})
    if res1.status_code == 200:
        data = res1.json()
        print(f"Answer: {data.get('answer')}")
        if "shopping assistant" in data.get('answer', '').lower() and not data.get('sql'):
             print("✅ Code Refusal: PASS")
        else:
             print(f"❌ Code Refusal: FAIL (Answer: {data.get('answer')})")
    else:
        print(f"Error {res1.status_code}: {res1.text}")

    # Test 2: General Knowledge
    q2 = "Who is the president of USA?"
    print(f"\nQuery: {q2}")
    res2 = requests.post(BASE_URL, json={"question": q2})
    if res2.status_code == 200:
        data = res2.json()
        print(f"Answer: {data.get('answer')}")
        if ("shopping" in data.get('answer', '').lower() or "shop" in data.get('answer', '').lower()) and not data.get('sql'):
             print("✅ General Knowledge Refusal: PASS")
        else:
             print(f"❌ General Knowledge Refusal: FAIL (Answer: {data.get('answer')})")

if __name__ == "__main__":
    test_refusal()
