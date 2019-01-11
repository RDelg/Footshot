import requests
data = {
	'rut': '19073061-1',
	'imagenes': 'foldername34/'
}
r = requests.post('http://192.168.1.13:8000/api/tests/record', data);
print(r.json())