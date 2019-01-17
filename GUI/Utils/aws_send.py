import boto3
import botocore
import os
#creating a bucket (dunno if can create 'sub-buckets')
'''s3 = boto3.resource('s3')
s3.create_bucket(Bucket='newbucketforfootshot')
'''
class Foot_AWS(object):
	def __init__(self, bucket_name = 'newbucketforfootshot'):
		try:
			self.s3 = boto3.resource('s3')
			self.s3_client = boto3.client('s3')
			self.connected = True
		except Exception as e:
			print('Error')
			self.connected = False
		finally:		
			self.bucket_name = bucket_name 

	def upload_file(self, filename):
		try:
			self.s3_client.upload_file(filename, self.bucket_name, filename)
			return True
		except self.s3_client.meta.client.exceptions.EndpointConnectionError as e:
			print("Error...")
			return False	

	def testeroo(self):
		return 'Sent from AWS Class!!'

	def list_files(self):
		bucket = self.s3.Bucket(self.bucket_name)
		for item in bucket.objects.all():
			print(item)		

	def download_file(self, file_key):
		try:
			self.s3.Bucket(self.bucket_name).download_file(file_key, file_key)
		except botocore.exceptions.ClientError as e:
			if e.response['Error']['Code'] == "404":
				print("The object does not exist.")
			else:
				raise

	def download_folder(self, folder_name):
		bucket = self.s3.Bucket(self.bucket_name)
		file_list = bucket.objects.filter(Prefix=folder_name)
		try:
			os.mkdir(folder_name)
		except OSError:
			print("The folder already exists")	
		
		for item in file_list:
			self.download_file(item.key)


if __name__ == '__main__':
	aws = Foot_AWS()
	aws.list_files()
	