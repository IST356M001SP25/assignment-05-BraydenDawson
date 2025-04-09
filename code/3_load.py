import os 
import pandas as pd
import boto3
from botocore.exceptions import ClientError

def upload_file(file_name, bucket_name, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: Full path to the file to upload (e.g., cache/file.csv) 
    :param bucket_name: Bucket to upload to (this should be your S3 bucket name)
    :param object_name: S3 object name (this should be the file name without the cache/ prefix, e.g., file.csv)
    :return: True if file was uploaded, else False
    """
    s3 = boto3.resource('s3', 
        endpoint_url='https://play.min.io:9000',
        aws_access_key_id='Q3AM3UQ867SPQQA43P2F',
        aws_secret_access_key='zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG',
        aws_session_token=None,
        config=boto3.session.Config(signature_version='s3v4'),
        verify=False
    ).meta.client

    # Create the bucket if it does not exist
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
        print(f"ERROR: {e}")
        return False
    return True


# Function to load and upload the reports and transformed data
def load_transformed_data():
    # Assuming 'transformed_data' is the dataframe after transformation
    # Here is an example transformed dataset. You should replace this with your actual transformed data.
    transformed_data = pd.read_csv('cache/survey_dataset.csv')  # Load the transformed dataset (from the cache)

    # Report 1: Save and upload the annual salary adjusted by location and age
    report_age = pd.read_csv('cache/annual_salary_adjusted_by_location_and_age.csv')
    upload_file('cache/annual_salary_adjusted_by_location_and_age.csv', 'ist356mafudge', 'annual_salary_adjusted_by_location_and_age.csv')

    # Report 2: Save and upload the annual salary adjusted by location and education
    report_education = pd.read_csv('cache/annual_salary_adjusted_by_location_and_education.csv')
    upload_file('cache/annual_salary_adjusted_by_location_and_education.csv', 'ist356mafudge', 'annual_salary_adjusted_by_location_and_education.csv')

    # Final transformed dataset (survey data combined with cost of living adjustments)
    transformed_data.to_csv('cache/survey_dataset.csv', index=False)
    upload_file('cache/survey_dataset.csv', 'ist356mafudge', 'survey_dataset.csv')


if __name__ == '__main__':
    # Call the load function to upload the reports to S3
    load_transformed_data()
