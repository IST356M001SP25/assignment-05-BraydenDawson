import pandas as pd
import numpy as np
import streamlit as st
import pandaslib as pl

# Read survey data from the provided Google Sheets link
survey_url = "https://docs.google.com/spreadsheets/d/1IPS5dBSGtwYVbjsfbaMCYIWnOuRmJcbequohNxCyGVw/export?resourcekey=&gid=1625408792&format=csv"
survey_data = pd.read_csv(survey_url)

# Extract the year from the Timestamp column using the extract_year_mdy function
survey_data['year'] = survey_data['Timestamp'].apply(pl.extract_year_mdy)

# Save the survey data to a CSV file in the cache directory
survey_data.to_csv('cache/survey_data.csv', index=False)

# Get the unique years present in the survey data
unique_years = survey_data['year'].unique()

# For each year in the survey data
for year in unique_years:
    # Scrape the cost of living data for the corresponding year
    col_url = f"https://www.numbeo.com/cost-of-living/rankings.jsp?title={year}&displayColumn=0"
    col_data = pd.read_html(col_url)
    
    # Extract the correct table (the second one on the page)
    col_data_for_year = col_data[1]
    
    # Add the year column to the cost of living data
    col_data_for_year['year'] = year
    
    # Save the cost of living data for the year to a CSV file in the cache directory
    col_data_for_year.to_csv(f'cache/cost_of_living_{year}.csv', index=False)

# Load the states-to-abbreviation mapping from the Google Sheets link
states_url = "https://docs.google.com/spreadsheets/d/14wvnQygIX1eCVo7H5B7a96W1v5VCg6Q9yeRoESF6epw/export?format=csv"
states_data = pd.read_csv(states_url)

# Save the states data to a CSV file in the cache directory
states_data.to_csv('cache/states_mapping.csv', index=False)
