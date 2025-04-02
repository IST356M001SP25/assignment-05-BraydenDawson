import pandas as pd
import streamlit as st
import pandaslib as pl

# TODO: Write your transformation code here

@st.cache_data
def transform_data(survey_data, cost_of_living_data, states_data):
    # Step 1: Clean and merge the states data to get the state abbreviations
    states_data = states_data.rename(columns={'State Name': 'State'})  # Adjust column names if needed
    survey_data = survey_data.merge(states_data[['State', 'State Abbreviation']], how='inner', on='State')
    
    # Step 2: Merge the survey data with the cost of living data
    # Ensure that the 'City' column is properly aligned (strip any leading/trailing spaces)
    survey_data['City'] = survey_data['City'].str.strip()
    cost_of_living_data['City'] = cost_of_living_data['City'].str.strip()
    
    merged_data = survey_data.merge(cost_of_living_data[['City', 'Cost of Living Index', 'year']], 
                                    how='inner', on=['City', 'year'])
    
    # Step 3: Normalize the salary based on the cost of living index
    # Formula: normalized_salary = (salary * 100) / cost_of_living_index
    merged_data['normalized_salary'] = merged_data['Annual Salary'] * (100 / merged_data['Cost of Living Index'])
    
    # Step 4: Handle missing or incorrect data (if necessary)
    # You can fill missing values or drop rows where critical data is missing
    merged_data = merged_data.dropna(subset=['normalized_salary'])
    
    return merged_data
