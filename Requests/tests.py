import requests

r = requests.post('https://djangotesteroni.herokuapp.com/api/tests/single', {'ayy': 'lmao'});
print(r.json())