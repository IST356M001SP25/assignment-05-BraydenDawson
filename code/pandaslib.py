import os
import pandas as pd
from datetime import datetime
import re
import boto3
from botocore.exceptions import ClientError
import streamlit as st

# Transformation Functions
def clean_currency(item: str) -> float:
    '''
    Remove anything from the item that prevents it from being converted to a float
    '''
    return float(str(item).replace('$', '').replace(',', ''))

def extract_year_mdy(timestamp: str) -> int:
    '''
    Use datetime.strptime to parse the date and then extract the year
    '''
    return datetime.strptime(timestamp, '%m/%d/%Y %H:%M:%S').year

def clean_country_usa(item: str) -> str:
    '''
    This function should replace any combination of 'United States of America', 'USA' etc.
    with 'United States'
    '''
    possibilities = [
        'united states of america', 'usa', 'us', 'united states', 'u.s.'
    ]
    if item.strip().lower() in possibilities:
        return 'United States'
    else:
        return item

# Load Data Function
@st.cache_data
def load_data():
    # Load the states, survey, and cost of living data
    states_data = pd.read_csv('https://docs.google.com/spreadsheets/d/14wvnQygIX1eCVo7H5B7a96W1v5VCg6Q9yeRoESF6epw/export?format=csv')
    survey_data = pd.read_csv('https://docs.google.com/spreadsheets/d/1IPS5dBSGtwYVbjsfbaMCYIWnOuRmJcbequohNxCyGVw/export?resourcekey=&gid=1625408792&format=csv')
    cost_of_living_data = pd.read_csv('cache/col_2024.csv')  # Example for the year 2024

    return states_data, survey_data, cost_of_living_data

# Transform Data Function
@st.cache_data
def transform_data(survey_data, cost_of_living_data, states_data):
    # Step 1: Clean and merge the states data to get the state abbreviations
    states_data = states_data.rename(columns={'State Name': 'State'})
    survey_data = survey_data.merge(states_data[['State', 'State Abbreviation']], how='inner', on='State')

    # Step 2: Clean up and engineer columns for merging
    survey_data['_country'] = survey_data['Which country do you work in?'].apply(clean_country_usa)
    survey_data['_full_city'] = survey_data['City'] + ', ' + survey_data['State Abbreviation'] + ', ' + survey_data['_country']

    # Step 3: Merge survey data with the cost of living data
    merged_data = survey_data.merge(cost_of_living_data[['City', 'Cost of Living Index', 'year']], 
                                    how='inner', left_on=['_full_city', 'year'], right_on=['City', 'year'])

    # Step 4: Normalize the annual salary based on the cost of living index
    merged_data['__annual_salary_cleaned'] = merged_data['Annual Salary'].apply(clean_currency)
    merged_data['_annual_salary_adjusted'] = merged_data['__annual_salary_cleaned'] * (100 / merged_data['Cost of Living Index'])

    # Step 5: Create Reports
    report_age = pd.pivot_table(merged_data,
        values='_annual_salary_adjusted',
        index='_full_city',
        columns='Age band (How old are you?)',
        aggfunc='mean',
        fill_value=0
    )
    report_age.to_csv('cache/annual_salary_adjusted_by_location_and_age.csv')

    report_education = pd.pivot_table(merged_data,
        values='_annual_salary_adjusted',
        index='_full_city',
        columns='Highest level of education',
        aggfunc='mean',
        fill_value=0
    )
    report_education.to_csv('cache/annual_salary_adjusted_by_location_and_education.csv')

    # Save the final merged dataset
    merged_data.to_csv('cache/survey_dataset.csv', index=False)

    return merged_data

# Upload to S3 Function
def upload_file(file_name, bucket_name, object_name=None):
    """Upload a file to an S3 bucket"""
    s3 = boto3.resource('s3', 
        endpoint_url='https://play.min.io:9000',
        aws_access_key_id='Q3AM3UQ867SPQQA43P2F',
        aws_secret_access_key='zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG',
        aws_session_token=None,
        config=boto3.session.Config(signature_version='s3v4'),
        verify=False
    ).meta.client

    # Create bucket if it does not exist
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


# Function to load and upload the reports
def load_transformed_data():
    # Load transformed data and save reports to S3
    load_data()

    # Upload the transformed data and reports to the S3 bucket
    files = ['cache/survey_dataset.csv', 'cache/annual_salary_adjusted_by_location_and_age.csv', 'cache/annual_salary_adjusted_by_location_and_education.csv']
    bucket = "ist356mafudge"

    for file in files:
        object_name = file.replace('cache/', '')  # Remove cache/ prefix
        upload_file(file, bucket, object_name)

if __name__ == '__main__':
    load_transformed_data()  # Load and upload the files to S3
