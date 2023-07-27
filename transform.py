import os
import pandas as pd
from settings.params import *
from utils import *

def transform():

    cleaned_dataframes = transform_datasets()

    final_dataset = merge_datasets(cleaned_dataframes)

    save_data_to_csv(FINAL_DATASET_NAME, final_dataset)


transform()