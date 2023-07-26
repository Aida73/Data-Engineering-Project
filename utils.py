from bs4 import BeautifulSoup
import pandas as pd
from params import *
from pathlib import Path
import random
import re
import requests
import time


def getSoup(url):
    page = requests.get(url)
    return BeautifulSoup(page.content, 'html.parser')


def getCountryName(url):
    regex_pattern = r"/pays/(\w+)"
    matches = re.findall(regex_pattern, url)
    if matches:
        country_name = matches[0]
        return country_name
    return None


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
    time.sleep(5)
    indicators = linked_page_soup.find_all(
        "div", {'class': 'indicator-item__wrapper'})
    indicators_values = getIndicatorsValues(indicators)
    print(page)
    print(len(indicators_values))
    if len(indicators_values) > 0:
        country_name = getCountryName(page)
        COUNTRIES_DATA[country_name] = indicators_values


# create the indicators dataframe
def getIndicatorsDataframe():
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
    for country, values in COUNTRIES_DATA.items():
        print("Creating dataframe")
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
    return "Save compled"
