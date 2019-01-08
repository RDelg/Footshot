import requests

r = requests.post('http://localhost:8000/api/tests/single', {'ayy': 'lmao'});
print(r.json())