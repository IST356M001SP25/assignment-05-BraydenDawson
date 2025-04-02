import os 
import pandas as pd
import boto3
from botocore.exceptions import ClientError

def upload_file(file_name, bucket_name, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: Is a full path to the file to upload e.g. cache/file.csv 
    :param bucket: Bucket to upload to. this should be ist356yournetid
    :param object_name: S3 object name. this should be the file name without the cache/ prefix file.csv
    :return: True if file was uploaded, else False
    """
    # create resource
    s3 = boto3.resource('s3', 
        endpoint_url='https://play.min.io:9000',
        aws_access_key_id='Q3AM3UQ867SPQQA43P2F',
        aws_secret_access_key='zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG',
        aws_session_token=None,
        config=boto3.session.Config(signature_version='s3v4'),
        verify=False
    ).meta.client

    # create bucket if it does not exist
    response = s3.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    if bucket_name not in buckets:
        s3.create_bucket(Bucket=bucket_name)   

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    try:
        response = s3.upload_file(file_name, bucket_name, object_name)
    except ClientError as e:
        print("ERROR",e)
        return False
    return True

if __name__ == '__main__':
    #TODO: Write your load code here (remove pass first)
    sample_transformed_data = pd.DataFrame({
        'City': ['New York', 'Los Angeles', 'Chicago'],
        'State': ['NY', 'CA', 'IL'],
        'normalized_salary': [60000, 50000, 55000],
        'year': [2024, 2024, 2024]
    })
    
    load_transformed_data(sample_transformed_data)