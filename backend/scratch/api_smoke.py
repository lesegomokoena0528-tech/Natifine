"""API smoke test using the Flask test client. Not part of the app."""

import json
import sys
import time

from app.factory import create_app

app = create_app()
client = app.test_client()

FAILS = []


def check(name, cond, extra=""):
    status = "OK " if cond else "FAIL"
    print(f"[{status}] {name} {extra}")
    if not cond:
        FAILS.append(name)


def login(username, password):
    r = client.post("/api/auth/login", json={"username": username, "password": password})
    data = r.get_json()
    return r.status_code, data


def auth(token):
    return {"Authorization": f"Bearer {token}"}


print("=== AUTH ===")
st, data = login("citizen@natifine.co.za", "Citizen@123")
check("citizen login", st == 200 and data["success"], st)
ctoken = data["data"]["access_token"]
cuser = data["data"]["user"]

st, data = login("officer@natifine.gov.za", "Officer@123")
check("officer login", st == 200, st)
otoken = data["data"]["access_token"]

st, data = login("admin@natifine.gov.za", "Admin@123")
check("admin login", st == 200, st)
atoken = data["data"]["access_token"]

st, data = login("citizen@natifine.co.za", "wrong")
check("bad login rejected", st == 401, st)

r = client.get("/api/auth/profile")
check("profile unauthenticated rejected", r.status_code == 401, r.status_code)

r = client.get("/api/auth/profile", headers=auth(ctoken))
check("profile authenticated", r.status_code == 200, r.status_code)

print("\n=== CITIZEN ===")
r = client.get("/api/citizen/dashboard", headers=auth(ctoken))
d = r.get_json()
check("citizen dashboard", r.status_code == 200 and "summary" in d["data"], r.status_code)
print("   summary:", json.dumps(d["data"]["summary"]))

r = client.get("/api/v1/fines/my", headers=auth(ctoken))
d = r.get_json()
check("my fines", r.status_code == 200 and len(d["data"]) >= 3, f"{r.status_code} n={len(d['data'])}")
print("   fines:", [(f["fine_number"], f["status"]) for f in d["data"]])

r = client.get("/api/v1/payments/history", headers=auth(ctoken))
check("payment history", r.status_code == 200, r.status_code)

r = client.get("/api/v1/disputes", headers=auth(ctoken))
d = r.get_json()
check("my disputes", r.status_code == 200 and len(d["data"]) >= 1, f"{r.status_code}")

r = client.get("/api/notifications/me", headers=auth(ctoken))
check("my notifications", r.status_code == 200, r.status_code)

r = client.get("/api/v1/fines", headers=auth(ctoken))
check("citizen blocked from officer fine list (403)", r.status_code == 403, r.status_code)

r = client.get("/api/admin/dashboard", headers=auth(ctoken))
check("citizen blocked from admin (403)", r.status_code == 403, r.status_code)

print("\n=== OFFICER ===")
r = client.get("/api/v1/fines?page=1&size=5", headers=auth(otoken))
d = r.get_json()
check("officer fines list paginated", r.status_code == 200 and "items" in d["data"], r.status_code)

r = client.get("/api/v1/fines/statistics", headers=auth(otoken))
check("fine statistics", r.status_code == 200, r.status_code)

r = client.get("/api/v1/fines/search?keyword=NF-2026", headers=auth(otoken))
check("fine search", r.status_code == 200, r.status_code)

r = client.get("/api/v1/disputes/pending", headers=auth(otoken))
d = r.get_json()
check("pending disputes", r.status_code == 200, r.status_code)
pending = d["data"]

# Register a fresh vehicle, issue a fine to it, then attempt a duplicate.
uniq = int(time.time() * 1000) % 99999999999999
reg = f"SMK{uniq % 1000000}"
vin = f"VIN{uniq:014d}"
r = client.post("/api/vehicles", headers=auth(otoken), json={
    "registration_number": reg,
    "owner_id": cuser["user_id"],
    "make": "Nissan", "model": "Almera", "year": 2015,
    "color": "Black", "vin": vin,
    "engine_number": f"ENG-{reg}", "vehicle_type": "CAR"
})
d = r.get_json()
check("register vehicle", r.status_code == 201 and d["success"], r.status_code)
vid = d["data"]["vehicle_id"]

r = client.post("/api/v1/fines", headers=auth(otoken), json={
    "vehicle_id": vid,
    "offence_code": "TEST-001",
    "offence": "Smoke test offence",
    "severity": "LOW",
    "amount": "300.00",
    "location": "Test Road"
})
d = r.get_json()
check("issue fine", r.status_code == 201 and d["success"], r.status_code)
fresh_fine = d["data"]
fid = fresh_fine["fine_id"]
print("   fine issued:", fresh_fine["fine_number"])

r = client.post("/api/v1/fines", headers=auth(otoken), json={
    "vehicle_id": vid,
    "offence_code": "TEST-002",
    "offence": "Different active offence",
    "severity": "LOW",
    "amount": "100.00",
    "location": "Test Road"
})
d = r.get_json()
check("different offence allowed", r.status_code == 201, f"{r.status_code} {d.get('message')}")
if d["success"]:
    client.patch(f"/api/v1/fines/{d['data']['fine_id']}/status",
                 headers=auth(otoken), json={"status": "CANCELLED", "reason": "smoke cleanup"})
    r = client.post("/api/v1/fines", headers=auth(otoken), json={
        "vehicle_id": vid,
        "offence_code": "TEST-001",
        "offence": "Duplicate smoke offence",
        "severity": "LOW",
        "amount": "100.00",
        "location": "Test Road"
    })
    d = r.get_json()
    check("duplicate active offence rejected", r.status_code == 400 and not d["success"], f"{r.status_code} {d.get('message')}")

# review the pending dispute - request more information
if pending:
    did = pending[0]["dispute_id"]
    r = client.get(f"/api/v1/disputes/{did}", headers=auth(otoken))
    check("dispute details", r.status_code == 200, r.status_code)
    r = client.patch(f"/api/v1/disputes/{did}/request-information", headers=auth(otoken),
                     json={"message": "Please provide the original notice document."})
    check("request more information", r.status_code == 200, r.get_json())

print("\n=== PAYMENT FLOW ===")
r = client.post("/api/v1/payments", headers=auth(ctoken), json={
    "fine_id": fid, "amount": fresh_fine["amount"],
    "gateway": "INTERNAL", "payment_method": "CARD"
})
d = r.get_json()
check("create payment", r.status_code == 201 and d["success"], r.status_code)
if d["success"]:
    pref = d["data"]["payment_reference"]
    gr = d["data"]["gateway_reference"]
    r2 = client.post("/api/v1/payments/verify", headers=auth(ctoken), json={
        "payment_reference": pref, "gateway_reference": gr
    })
    d2 = r2.get_json()
    check("verify payment", r2.status_code == 200 and d2["success"], r2.status_code)
    if d2["success"]:
        pid = d2["data"]["payment_id"]
        r3 = client.get(f"/api/v1/payments/{pid}/receipt", headers=auth(ctoken))
        check("receipt download", r3.status_code == 200 and r3.headers.get("Content-Type") == "application/pdf", f"{r3.status_code}")
    r4 = client.get("/api/v1/payments/totals", headers=auth(ctoken))
    check("payment totals", r4.status_code == 200, r4.status_code)

print("\n=== ADMIN ===")
r = client.get("/api/admin/dashboard", headers=auth(atoken))
d = r.get_json()
check("admin dashboard", r.status_code == 200 and d["success"], r.status_code)
print("   admin dashboard keys:", list(d.get("data", {}).keys()))

r = client.get("/api/admin/users", headers=auth(atoken))
d = r.get_json()
check("admin users", r.status_code == 200 and len(d["data"]) >= 5, f"{r.status_code}")

r = client.get("/api/admin/statistics", headers=auth(atoken))
check("admin statistics", r.status_code == 200, r.status_code)

r = client.get("/api/v1/payments/statistics", headers=auth(atoken))
check("payment statistics", r.status_code == 200, r.status_code)

r = client.get("/api/admin/audit", headers=auth(atoken))
check("audit logs reachable", r.status_code == 200, r.status_code)

r = client.get("/api/v1/disputes/statistics", headers=auth(atoken))
check("dispute statistics", r.status_code == 200, r.status_code)

print("\n=== FRONTEND STATIC ===")
r = client.get("/")
check("index served", r.status_code == 200, r.status_code)

print("\n==========================================")
if FAILS:
    print(f"{len(FAILS)} FAILURES: {FAILS}")
    sys.exit(1)
print("ALL SMOKE TESTS PASSED")