import pandas as pd
from settings.params import *
from utils import *


def extract():
    """
    Return a dataframe after extracting the indicators, region and code from each country

    """
    indicators_data = getIndicatorsDataframe()
    save_data_to_csv("indicators.csv", indicators_data)

    # extract and save the country codes into a new dataframe
    country_codes_df = getCountryCodes()
    # save the final results
    save_data_to_csv("country_codes.csv", country_codes_df)


extract()
