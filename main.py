import requests

from bs4 import BeautifulSoup

import pandas as pd

# URL of the gas prices webpage

PRICE_URL = 'https://calculator.aa.co.za/calculators-toolscol-1/fuel-pricing'

# Function that retrieves data

def get_prices():

    """

    Get Price Data from AA Website.

    :return: List of records

    """

    fuel_price_data = []

    

    # Get HTML content from the webpage

    response = requests.get(PRICE_URL)

    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the location elements and get their values

    location_elements = soup.select('#edit-location > div > input')

    locations = [location.get('value') for location in location_elements]

    # Find the fuel type elements and get their values

    fuel_elements = soup.select('#edit-fuel-type > option')

    fuel_types = [fuel_.get('value') for fuel_ in fuel_elements]

    # Find the year elements and get their values

    year_elements = soup.select('#edit-year > option')

    years = [year.get('value') for year in year_elements]

    # Iterate over each combination of parameters and retrieve data

    for location in locations:

        for fuel in fuel_types:

            for year in years:

                # Set the query parameters and send a POST request

                data = {

                    'location': location,

                    'fuel_type': fuel,

                    'year': year,

                    'op': 'Get Fuel Price'

                }

                response = requests.post(PRICE_URL, data=data)

                print(f"Getting Data for {location}:{fuel}:{year}.")

                soup = BeautifulSoup(response.content, 'html.parser')

                # Find the rows of the table and extract data

                rows = soup.select('table > tbody > tr')

                for row in rows:

                    cells = row.select('td')

                    fuel_price_data.append([

                        cells[0].text.strip(),  # Price

                        cells[1].text.strip(),  # Date

                        location,

                        fuel,

                        year

                    ])

    return fuel_price_data

# Function that wrangles data

def wrangle_data(data):

    """

    Wrangle/Transform Data from Price Data.

    :param data: List of records

    :return: Wrangled dataframe

    """

    fuel_df = pd.DataFrame(data, columns=['Price', 'Date', 'Location', 'Fuel Type', 'Year'])

    remap = {

        "Location": {

            "coast": "Coastal",

            "reef": "Inland"

        },

        "Fuel Type": {

            "unleaded_93": "Petrol Unleaded 93",

            "unleaded_95": "Petrol Unleaded 95",

            "lrp": "Petrol LRP",

            "old": "Diesel 500ppm",

            "new": "Diesel 50ppm"

        }

    }

    fuel_df.replace(remap, inplace=True)

    fuel_df.to_csv('fuel_prices.csv', index=False)

if __name__ == '__main__':

    fuel_price_data = get_prices()

    wrangle_data(fuel_price_data)

