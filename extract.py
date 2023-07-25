import pandas as pd
from params import *
from utils import *


def extract():
    """
    Return a dataframe after extracting the indicators, region and code from each country

    """
    indicators_data = getIndicatorsDataframe()

    # extract and save the country codes into a new dataframe
    country_codes_df = getCountryCodes()

    # save the final results
    save_data_to_csv("indicators3.csv", indicators_data)
    save_data_to_csv("country_codes2.csv", country_codes_df)


if __name__ == "__main__":
    extract()
