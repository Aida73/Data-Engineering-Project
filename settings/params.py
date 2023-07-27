from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# home_diectory
HOME_DIR = Path.cwd()

# data
DATA_DIR = Path(HOME_DIR, "data")

# report
REPORT_DIR = Path(HOME_DIR, "reports")

# urls to scrape

URLS = {
    'bm_url': 'https://donnees.banquemondiale.org/pays'
}

# change randomly header for skipping scrappers limitations
USER_AGENTS_LIST = [
    'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
]
# will stock all the data about the indicators
COUNTRIES_DATA = dict()

# S3
CREDENTIALS = {
    'aws_access_key_id': os.environ.get('AWS_ACCESS_KEY_ID'),
    'aws_secret_access_key': os.environ.get('AWS_SECRET_ACCESS_KEY')
}

BUCKET_NAME = 'worldbankdatabucket'


FILTERS_PARAMS = {
    "MIN_COMPLETION_RATE": 0.5,
    "NAN_TRESHOLD": 80,
    "FEATURES": {
        'id': 'code_pays',
        'country': 'pays',
        'region': 'region',
        'population, total': 'population_totale',
        'migration nette': 'migration_nette',
        'croissance du pib (% annuel)': 'croissance_annuelle_PIB',
        'chomage, total (% de la population) (estimation modelisee oit)': 'pourcentage_total_population_chomage',
        'inflation, prix a la consommation (% annuel)': 'inflation_prix_annuel_consommation',
        "acces a l'electricite (% de la population)": "acces_electricite(%population)",
        'indice du capital humain (echelle comprise entre 0 et 1)': 'indi_capital_humain(indice entre 0 et 1)',
        'income group': 'niveau de vie'
    },
    "FEATURES_STR": {
        'country',
        "id",
        'region',
        'income group'
    },
    "INCOME_MAPPING": {
        'Low income': 'faible',
        'Lower middle income': 'moyen',
        'Upper middle income': '>moyenne',
        'High income': 'eleve'
    }
}

FINAL_DATASET_NAME = "word_bank_indicators.csv"
