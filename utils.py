from bs4 import BeautifulSoup
import random
import re
import requests
import pandas as pd


# Declare all needed variables here
bm_url = "https://donnees.banquemondiale.org/pays"
countries_data = {}
# change randomly header for skipping scrappers limitations
user_agents_list = [
    'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
]


def getSoup(url):
    page = requests.get(url=bm_url)
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
    contries_soup = getSoup(bm_url)
    sections = contries_soup.find_all("section", class_="nav-item")
    for section in sections:
        a_tags = section.find_all("a", attrs={"data-reactid": True})
        countries.extend([country.text for country in a_tags])
        pages.extend([bm_url[:-5]+page['href']
                     for page in a_tags if page['href']])
    return countries, pages


def getIndicatorsTitles():
    _, pages = getCountries()
    data = requests.get(url=pages[0],
                        headers={'User-Agent': random.choice(user_agents_list)})
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
                                            'User-Agent': random.choice(user_agents_list)},
                                        timeout=30)  # add timeout to skip networkConnectionError

    # Parse the linked page's HTML content
    linked_page_soup = BeautifulSoup(linked_page_response.text, "html.parser")
    indicators = linked_page_soup.find_all(
        "div", {'class': 'indicator-item__wrapper'})
    indicators_values = getIndicatorsValues(indicators)
    print(page)
    print(len(indicators_values))
    if len(indicators_values) > 0:
        country_name = getCountryName(page)
        countries_data[country_name] = indicators_values


def getPageData(page_number):
    url = f"https://api.worldbank.org/v2/country/all?page={page_number}&format=json"
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


def getCountryCodes() :
    all_country_codes = []
    for page_num in range(1, 7):
        page_data = getPageData(page_num)
        if page_data:
            country_data = extractCountryCodes(page_data)
            all_country_codes.extend(country_data)
    
    country_codes_df = pd.DataFrame(all_country_codes)

    return country_codes_df