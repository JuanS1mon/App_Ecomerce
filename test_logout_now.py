import requests

r = requests.post('http://localhost:8000/logout')
print(f'POST /logout Status: {r.status_code}')
print(f'Allow: {r.headers.get("allow", "N/A")}')
print(f'Response: {r.text[:100]}')
