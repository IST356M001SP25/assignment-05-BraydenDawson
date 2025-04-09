import pandas as pd
import streamlit as st
import pandaslib as pl

@st.cache_data
def transform_data(survey_data, cost_of_living_data, states_data):
    # Step 1: Clean and merge the states data to get the state abbreviations
    states_data = states_data.rename(columns={'State Name': 'State'})  # Adjust column names if needed
    survey_data = survey_data.merge(states_data[['State', 'State Abbreviation']], how='inner', on='State')
    
    # Step 2: Clean up and engineer columns for merging
    # Clean 'Which country do you work in?' using the clean_country_usa function
    survey_data['_country'] = survey_data['Which country do you work in?'].apply(pl.clean_country_usa)
    
    # Merge the state names with the state codes (assuming 'State' column contains full state names)
    survey_data = survey_data.merge(states_data[['State', 'State Abbreviation']], how='inner', on='State')
    
    # Engineer the new _full_city column
    survey_data['_full_city'] = survey_data['City'] + ', ' + survey_data['State Abbreviation'] + ', ' + survey_data['_country']
    
    # Step 3: Merge survey data with cost of living data (match on year and _full_city)
    cost_of_living_data['City'] = cost_of_living_data['City'].str.strip()  # Clean up city names
    survey_data['City'] = survey_data['City'].str.strip()
    
    # Merge the survey and cost of living data on year and _full_city
    merged_data = survey_data.merge(cost_of_living_data[['City', 'Cost of Living Index', 'year']], 
                                    how='inner', left_on=['_full_city', 'year'], right_on=['City', 'year'])
    
    # Step 4: Normalize the annual salary based on cost of living index
    merged_data['__annual_salary_cleaned'] = merged_data['Annual Salary'].apply(pl.clean_currency)
    
    # Calculate the adjusted salary based on cost of living index
    merged_data['_annual_salary_adjusted'] = merged_data['__annual_salary_cleaned'] * (100 / merged_data['Cost of Living Index'])
    
    # Step 5: Create reports (Pivot Tables)
    # Report 1: Salary adjusted by city and age band
    report_age = pd.pivot_table(
        merged_data,
        values='_annual_salary_adjusted',
        index='_full_city',
        columns='Age band (How old are you?)',
        aggfunc='mean',
        fill_value=0
    )
    report_age.to_csv('cache/annual_salary_adjusted_by_location_and_age.csv')
    
    # Report 2: Salary adjusted by city and highest level of education
    report_education = pd.pivot_table(
        merged_data,
        values='_annual_salary_adjusted',
        index='_full_city',
        columns='Highest level of education',
        aggfunc='mean',
        fill_value=0
    )
    report_education.to_csv('cache/annual_salary_adjusted_by_location_and_education.csv')
    
    # Save the full dataset with adjusted salaries to the cache
    merged_data.to_csv('cache/survey_dataset.csv', index=False)
    
    return merged_data

