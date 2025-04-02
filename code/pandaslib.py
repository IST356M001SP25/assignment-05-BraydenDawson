from datetime import datetime
import re

def clean_currency(item: str) -> float:
    '''
    Remove anything from the item that prevents it from being converted to a float
    '''
    item = re.sub(r'[^\d.]', '', item)  # Remove non-numeric characters except for the decimal point
    if item.count('.') > 1:
        item = item.replace('.', '', item.count('.') - 1)  # Keep only the first decimal point
    
    return float(item)

def extract_year_mdy(timestamp: str) -> int:
    '''
    Use datetime.strptime to parse the date and then extract the year
    '''
    date_obj = datetime.strptime(timestamp, '%m/%d/%Y %H:%M:%S')  # Convert string to datetime object
    return date_obj.year  # Return the year part

def clean_country_usa(item: str) -> str:
    '''
    This function should replace any combination of 'United States of America', 'USA' etc.
    with 'United States'
    '''
    possibilities = [
        'united states of america', 'usa', 'us', 'united states', 'u.s.'
    ]
    item_lower = item.lower()  # Convert to lowercase to handle case-insensitive matching
    if any(variant in item_lower for variant in possibilities):  # Check for any variant in the string
        return 'United States'
    return item  # If no match, return the original item

if __name__ == '__main__':
   #print("Testing clean_currency function:")
    #print(clean_currency("$1,000"))  
    #print(clean_currency("10,000.01"))  
    #print(clean_currency("10,000,000.99"))  
    
    #print("\nTesting extract_year_mdy function:")
    #print(extract_year_mdy("12/31/2021 23:59:59"))  
    #print(extract_year_mdy("2/16/2023 19:14:37"))  
    #print(extract_year_mdy("1/1/2019 12:00:00")) 

    #print("\nTesting clean_country_usa function:")
    #print(clean_country_usa("United States of America"))  
    #print(clean_country_usa("USA"))  
    #print(clean_country_usa("US"))  
    #print(clean_country_usa("U.S."))  
    #print(clean_country_usa("Canada"))  
    pass