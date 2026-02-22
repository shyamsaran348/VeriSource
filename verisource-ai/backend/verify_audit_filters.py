
import requests

BASE = "http://localhost:8000"

def get_token():
    # Login as admin
    r = requests.post(f"{BASE}/auth/login", data={"username": "p7_admin", "password": "adm123"})
    if r.status_code == 200:
        return r.json()["access_token"]
    return None

def test_filters():
    token = get_token()
    if not token:
        print("Failed to get admin token. Make sure server is up and p7_admin exists.")
        return

    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Test All Logs
    r = requests.get(f"{BASE}/audit/logs", headers=headers)
    all_count = len(r.json())
    print(f"Total logs: {all_count}")

    # 2. Test Policy Filter
    r = requests.get(f"{BASE}/audit/logs", headers=headers, params={"mode": "policy"})
    policy_count = len(r.json())
    print(f"Policy logs: {policy_count}")

    # 3. Test Approved Filter
    r = requests.get(f"{BASE}/audit/logs", headers=headers, params={"decision": "approved"})
    approved_logs = r.json()
    print(f"Approved logs: {len(approved_logs)}")
    if approved_logs:
        print(f"Sample decisions (Approved filter): {set(l['decision'] for l in approved_logs)}")

    # 4. Test Refused Filter
    r = requests.get(f"{BASE}/audit/logs", headers=headers, params={"decision": "refused"})
    refused_logs = r.json()
    print(f"Refused logs: {len(refused_logs)}")
    if refused_logs:
        print(f"Sample decisions (Refused filter): {set(l['decision'] for l in refused_logs)}")

if __name__ == "__main__":
    test_filters()
