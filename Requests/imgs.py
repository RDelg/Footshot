import requests
import base64

def send_image(image_dir):
	with open(image_dir, 'rb') as bin_img:
		something = base64.b64encode(bin_img.read()) 
		files = {'media': something}
		print(files)
		requests.post('http://192.168.1.13:8000/api/tests/upload', files)


if __name__ == "__main__":
	resp = send_image('./khajit_no_understand.jpg')
	print(resp.json())