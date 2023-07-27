
# Mise en place d'un pipeline ETL

Ce projet consiste à mettre en place un pipeline ETL (Extract, Transform, Load) sur les données de la banque mondiale. On s'interressra particulièrement aux données sur les indicateurs de développement.
 


## Prérequis

Avant de lancer le pipeline ETL, assurer vous d'avoir python déjà installé
[Python](https://www.python.org/downloads/) (version 3.11 or higher)





## Installation

- Cloner le projet
```bash
  git clone https://github.com/Aida73/Data-Engineering-Project.git 

```
- Se déplacer dans le répertoire du projet
```bash
    cd data_engineering_project

```

- Installer les dépendances requises
```bash
    pip install -r requirements.txt
```
    
## Structure du projet
```bash
.
├── __pycache__
│   ├── params.cpython-311.pyc
│   └── utils.cpython-311.pyc
├── data
│   ├── CLASS.xlsx
│   ├── country_codes.csv
│   ├── indicators.csv
│   └── word_bank_indicators.csv
├── data_profiling.ipynb
├── download.py
├── extract.py
├── load.py
├── requirements.txt
├── settings
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-311.pyc
│   │   └── params.cpython-311.pyc
│   └── params.py
├── transform.py
└── utils.py
```
## Extract / Extraction

C'est dans cette partie que les données cibles sont récupérées. Pour la collecte, [l'API](https://documents.worldbank.org/en/publication/documents-reports/api) de la banque mondiale à été utilisée. Cela est combiné avec du webScrapping([ici](https://donnees.banquemondiale.org/pays)) pour enrichir et avoir des données en temps réel. 

Pour lancer localement le script de l'extraction:
```bash
    python extract.py
```


## Transform / Transformation

Pour lancer localement la Transformation des données collectées:
```bash
    python transform.py
```

## Load / Chargemrnt

Pour cette partie on utilse AWS pour charger les données dans un bucket S3. POur ce faire assurer vous de mettre dans un fichier `.env` les informations de connexion du bucket:
`AWS_ACCESS_KEY_ID` et `AWS_SECRET_ACCESS_KEY`


## Orchestration

Ce pipeline est orchestré en utilant Apache Airflow
