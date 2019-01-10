import boto3
import botocore
#creating a bucket (dunno if can create 'sub-buckets')
'''s3 = boto3.resource('s3')
s3.create_bucket(Bucket='newbucketforfootshot')
'''
class Foot_AWS(object):
	def __init__(self, bucket_name = 'newbucketforfootshot'):
		self.s3 = boto3.resource('s3')
		self.s3_client = boto3.client('s3')

		self.bucket_name = bucket_name 

	def upload_file(self, filename):
		self.s3_client.upload_file(filename, self.bucket_name, filename)

	def testeroo(self):
		return 'Sent from AWS Class!!'	

	def download_file(self, file_key):
		try:
			s3.Bucket(self.bucket_name).download_file(file_key, file_key)
		except botocore.exceptions.ClientError as e:
			if e.response['Error']['Code'] == "404":
				print("The object does not exist.")
			else:
				raise
	
	def download_full_bucket(self):
		#todo 			

if __name__ == '__main__':
	print('wena men')

