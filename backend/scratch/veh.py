import time
from app.factory import create_app

app = create_app()
c = app.test_client()
r = c.post('/api/auth/login', json={'username': 'officer@natifine.gov.za', 'password': 'Officer@123'})
t = r.get_json()['data']['access_token']
h = {'Authorization': f'Bearer {t}'}

payload = {
    'registration_number': 'SMK9%d' % int(time.time() % 10000),
    'owner_id': '793f3981-2e4c-4756-8c93-e4a10937fc51',
    'make': 'Nissan', 'model': 'Almera', 'year': 2015,
    'color': 'Black', 'vin': '1HGCM82633A000000',
    'engine_number': 'ENG-X', 'vehicle_type': 'CAR'
}
print("PAYLOAD:", payload)
print("VIN LEN:", len(payload['vin']))
r = c.post('/api/vehicles', headers=h, json=payload)
print(r.status_code, r.get_json())