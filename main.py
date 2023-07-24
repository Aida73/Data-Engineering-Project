import pandas as pd
import os
from utils import *


def extract():
    """
    Return a dataframe after extracting the indicators from each country

    """
    batch_size = 60  # Set batch size and initialize counters
    _, countries_pages = getCountries()
    current_batch = 0
    indicators_titles_list = getIndicatorsTitles()
    total_batches = (len(countries_pages))//batch_size

    # save data to dataframe
    df = pd.DataFrame(columns=['Country'] + indicators_titles_list)


    # Iterate over the sections in batches
    for batch in range(total_batches + 1):
        # Get the current batch of sections
        batch_sections = countries_pages[current_batch:current_batch + batch_size]

        # Iterate over the sections in the current batch
        for page in batch_sections:
            try:
                getCountriesData(page)
            except requests.exceptions.Timeout:
                print(
                    f"Request for {page} timed out. Skipping to the next page.")

        current_batch += batch_size
        # time.sleep(5)

    # create the Dataframe
    for country, values in countries_data.items():
        # Create a dictionary to hold the row data
        row_data = {'Country': country}

        for i, value in enumerate(values):
            title = indicators_titles_list[i] if i < len(
                indicators_titles_list) else ''
            row_data[title] = value

        # Append the row data to the DataFrame
        df = df._append(row_data, ignore_index=True)

    #extract and save the country codes into a ne dataframe
    country_codes_df = getCountryCodes()

    #save the final results
    path1 = os.path.join("data","indicators.csv")
    path2 = os.path.join("data","country_codes.csv")
    df.to_csv(path1, index=False)
    country_codes_df.to_csv(path2, index=False)



def transform(dataframe):
    """
    Perform transformation on the DataFrame.
    """
    pass


def load(dataframe):
    """
    Load the DataFrame into the target destination.
    """
    pass

if __name__ == "__main__":
    extract()
    transform()
    load()