import os
from bs4 import BeautifulSoup
import pandas as pd
from settings.params import *
from pathlib import Path
import random
import re
import requests
import time
import unidecode


def getSoup(url):
    page = requests.get(url)
    return BeautifulSoup(page.content, 'html.parser')


def getCountries():
    countries = []
    pages = []
    contries_soup = getSoup(URLS["bm_url"])
    sections = contries_soup.find_all("section", class_="nav-item")
    for section in sections:
        a_tags = section.find_all("a", attrs={"data-reactid": True})
        countries.extend([country.text for country in a_tags])
        pages.extend([URLS["bm_url"][:-5]+page['href']
                     for page in a_tags if page['href']])
    return countries, pages


def getIndicatorsTitles():
    _, pages = getCountries()
    data = requests.get(url=pages[0],
                        headers={'User-Agent': random.choice(USER_AGENTS_LIST)})
    linked_page_soup = BeautifulSoup(data.content, 'html.parser')
    indicators_titles = []
    for indicator in linked_page_soup.find_all("div", {'class': 'indicator-item__wrapper'}):
        titles = indicator.find_all("div", {'class': 'indicator-item__title'})
        indicators_titles.extend([title.text for title in titles])
    return indicators_titles


def getIndicatorsValues(content):
    indicators_values = []
    for indicator in content:
        values = indicator.find_all(
            "div", {"class": "indicator-item__data-info"})
        empty_value = indicator.find(
            "p", {"class": "indicator-item__data-info-empty"})

        indicators_values.extend([value.text for value in values])

        if empty_value:
            indicators_values.append(empty_value.text)
    return indicators_values


def getCountriesData(page):
    linked_page_response = requests.get(url=page,
                                        headers={
                                            'User-Agent': random.choice(USER_AGENTS_LIST)},
                                        timeout=30)  # add timeout to skip networkConnectionError

    # Parse the linked page's HTML content
    linked_page_soup = BeautifulSoup(linked_page_response.text, "html.parser")
    indicators = linked_page_soup.find_all(
        "div", {'class': 'indicator-item__wrapper'})
    indicators_values = getIndicatorsValues(indicators)
    print(page)
    print(len(indicators_values))
    if len(indicators_values) > 0:
        country_name = unidecode.unidecode(linked_page_soup.find(
            "div", {"class": "cardheader"}).find("h1").text)
        COUNTRIES_DATA[country_name] = indicators_values


# create the indicators dataframe
def getIndicatorsDataframe():
    batch_size = 20
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

        # Increment the current batch counter
        current_batch += batch_size

    # create the Dataframe
    print("Creating dataframe")
    print(indicators_titles_list)
    for country, values in COUNTRIES_DATA.items():
        # Create a dictionary to hold the row data
        row_data = {'Country': country}

        for i, value in enumerate(values):
            title = indicators_titles_list[i] if i < len(
                indicators_titles_list) else ''
            row_data[title] = value

        # Append the row data to the DataFrame
        df = df._append(row_data, ignore_index=True)

    return df


# get countries code and region
def getPageData(page_number):
    url = f"https://api.worldbank.org/v2/fr/country/all?page={page_number}&format=json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erreur lors de la récupération de la page {page_number}")
        return None


def extractCountryCodes(json_content):
    countries = json_content[1]

    country_codes_data = []
    for country in countries:
        country_id = country['id']
        country_name = country['name']
        country_region = country['region']['value']
        country_codes_data.append({
            'id': country_id,
            'name': country_name,
            'region': country_region
        })

    return country_codes_data


def getCountryCodes():
    all_country_codes = []
    for page_num in range(1, 7):
        page_data = getPageData(page_num)
        if page_data:
            country_data = extractCountryCodes(page_data)
            all_country_codes.extend(country_data)

    country_codes_df = pd.DataFrame(all_country_codes)

    return country_codes_df


def save_data_to_csv(name, dataframe):
    dataframe.to_csv(Path(DATA_DIR, name))
    return "Save completed"


def load_datasets():
    list_dataframe = {}
    for filename in os.listdir(DATA_DIR):
        df_name = f"df_{filename.split('.')[0]}"
        if filename.split('.')[-1] == 'csv':
            list_dataframe[df_name] = pd.read_csv(
                Path(DATA_DIR, filename), sep=',', index_col=[0])
        elif (filename.split('.')[-1] == 'xlsx') or (filename.split('.')[-1] == 'xls'):
            list_dataframe[df_name] = pd.read_excel(Path(DATA_DIR, filename))
        print(filename)
    return list_dataframe


def clean_and_convert(value):
    if isinstance(value, str):
        value = value.replace(',', '.')
        value = ''.join(filter(lambda x: x.isdigit()
                        or x in ['-', '.', ''], value))
    return float(value)


def find_columns_conditions(df):
    total_rows = df.shape[0]

    colToDel = [col for col in df.columns if (
        df[col].isnull().sum() / total_rows) > FILTERS_PARAMS['NAN_TRESHOLD']]

    constant_cols = [col for col in df.columns if df[col].nunique() == 1]

    min_completion_cols = [col for col in df.columns if (
        df[col].count() / total_rows) < FILTERS_PARAMS['MIN_COMPLETION_RATE']]

    return colToDel+constant_cols+min_completion_cols


def transform_datasets():
    datasets = load_datasets()
    cleaned_datasets = {}

    # Clean and transform 'df_indicators' DataFrame
    if 'df_indicators' in datasets:
        indicators = datasets['df_indicators']
        indicators.replace("No data available", float('nan'), inplace=True)
        indicators.columns = indicators.columns.str.lower()
        cols_to_convert = indicators.columns.difference(['country'])
        pd.options.display.float_format = '{:.2f}'.format
        indicators[cols_to_convert] = indicators[cols_to_convert].applymap(
            clean_and_convert)
        indicators['country'] = indicators['country'].str.strip()
        cols_to_del = find_columns_conditions(indicators)
        indicators.drop(columns=cols_to_del, axis=1, inplace=True)
        indicators = indicators.fillna(indicators.median(numeric_only=True))
        indicators.drop_duplicates(inplace=True)
        cleaned_datasets["indicators"] = indicators

    # Clean and transform 'df_country_codes' DataFrame
    if 'df_country_codes' in datasets:
        country_codes = datasets['df_country_codes']
        country_codes = country_codes.dropna(subset=['name'])
        # country_codes["name"] = country_codes["name"].str.lower()
        # country_codes["region"] = country_codes["region"].str.lower()
        country_codes = country_codes.applymap(unidecode.unidecode)
        country_codes.drop_duplicates(inplace=True)
        cleaned_datasets["country_codes"] = country_codes

    # Clean and transform 'df_CLASS' DataFrame
    if 'df_CLASS' in datasets:
        income = datasets['df_CLASS']
        income = income[['Code', 'Region', 'Income group']]
        income.columns = income.columns.str.lower()
        income = income.dropna(subset=['region'])
        mode_value = income['income group'].mode().iloc[0]
        income['income group'] = income['income group'].fillna(mode_value)
        income.drop_duplicates(inplace=True)
        cleaned_datasets["income"] = income

    return cleaned_datasets


def merge_datasets(cleaned_datasets):
    if all(key in cleaned_datasets for key in ['indicators', 'country_codes', 'income']):
        indicators = cleaned_datasets['indicators']
        country_codes = cleaned_datasets['country_codes']
        income = cleaned_datasets['income']
        print(country_codes['name'])
        print(indicators['country'])

        merged_df_1 = pd.merge(left=country_codes, right=indicators,
                               left_on='name', right_on='country', how='left')
        print(merged_df_1.head())
        final_dataset = pd.merge(left=merged_df_1, right=income[[
                                 'code', 'income group']], left_on='id', right_on='code', how='left')
        final_dataset.columns = [unidecode.unidecode(
            col) for col in final_dataset.columns]
        final_dataset = final_dataset[FILTERS_PARAMS['FEATURES'].keys()]
        final_dataset.rename(columns=FILTERS_PARAMS['FEATURES'], inplace=True)
        final_dataset.replace(
            {"niveau de vie": FILTERS_PARAMS['INCOME_MAPPING']}, inplace=True)

        final_dataset.dropna(inplace=True)
        final_dataset.index.name = 'id'
        return final_dataset
    return None
