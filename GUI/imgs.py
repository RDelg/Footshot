import requests

def send_image(image_dir):
	files = {'media': open(image_dir, 'rb')}
	requests.post('http://192.168.1.13/api/tests/upload', files = files)


if __name__ == "__main__":
	send_image('./sanik.jpg')