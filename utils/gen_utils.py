import traceback, sys
import time
import logging
import requests
import psycopg2
import pandas as pd
import configparser
import csv
from datetime import datetime, timedelta
import pytz

#TODO: assert checks if need be
#TODO: memory profiling if need be

# begin global paths
ALPHA_PATH = 'C:\\Users\\coope\\production_abupower\\csvs\\alpha.csv'
BETA_PATH = 'C:\\Users\\coope\\production_abupower\\csvs\\beta.csv'
UNLIMITED_PATH = 'C:\\Users\\coope\\production_abupower\\csvs\\unlimited.csv'
REVISED_PATH = 'C:\\Users\\coope\\production_abupower\\csvs\\revised.csv'
LEGENDS_PATH = 'C:\\Users\\coope\\production_abupower\\csvs\\leg.csv'
ARABIAN_NIGHTS_PATH = 'C:\\Users\\coope\\production_abupower\\csvs\\arn.csv'
DARK_PATH = 'C:\\Users\\coope\\production_abupower\\csvs\\dark.csv'
ANTIQUITIES_PATH = 'C:\\Users\\coope\\production_abupower\\csvs\\atq.csv'
HOMELANDS_PATH = 'C:\\Users\\coope\\production_abupower\\csvs\\home.csv'
FALLEN_EMPIRES_PATH = 'C:\\Users\\coope\\production_abupower\\csvs\\fem.csv'
COLLECTORS_EDITION_PATH = 'C:\\Users\\coope\\production_abupower\\csvs\\ce.csv'
INTERNATIONAL_COLLECTORS_EDITION_PATH = 'C:\\Users\\coope\\production_abupower\\csvs\\ice.csv'

# begin global configs
POWER_CONFIG = {
    'Alpha': 'Power',
    'Beta': 'Power',
    'Unlimited': 'Power',
    'Collectors': 'Power',
}
DUALS_CONFIG = {
    'Alpha': 'Duals',
    'Beta': 'Duals',
    'Unlimited': 'Duals',
    'Revised': 'Duals',
    'Collectors': 'Duals'
}
CONFIG = configparser.ConfigParser()
CONFIG.read('CONFIG.ini')


def database_connection():
    try:
        conn = psycopg2.connect(f"""dbname={CONFIG['myPostgresDB']['dbname']} user={CONFIG['myPostgresDB']['user']} host={CONFIG['myPostgresDB']['host']} password={CONFIG['myPostgresDB']['password']} port={CONFIG['myPostgresDB']['port']}""")
        conn.autocommit = True
        cursor = conn.cursor()
        print('-----------------------------------------------')
        print("Connected to database...")
        print()
        return cursor
    except Exception as e:
        get_trace_and_log(e)
        print("Cannot connect to database...")

def get_trace_and_log(error):
    """(str: error) -> str

    Returns a distinct traceback with the offending line and logs the error with the time and date."""
    logf = open("errors.log", "a")
    trace = traceback.extract_tb(sys.exc_info()[-1], limit=1)[-1][1]
    logging.error(error)
    print(f'Offending line: {trace}')
    logf.write(f'Error: {str(error)}\n'
               f'Asc time: {time.asctime()}\n')

def fetch_data(query):
    """(query: str) -> str

    Takes in a query, connects to the database and returns the result."""
    result = pd.read_sql(
        sql=query,
        con=psycopg2.connect(
            f"""dbname={CONFIG['myPostgresDB']['dbname']} user={CONFIG['myPostgresDB']['user']} host={CONFIG['myPostgresDB']['host']} password={CONFIG['myPostgresDB']['password']} port={CONFIG['myPostgresDB']['port']}""")
    )
    return result

def get_data(value):
    """() -> list

    Returns a list of every card in the requested table. Used to quickly check if contents populated."""
    query = (
        f"""
        SELECT * FROM {value}
        """)
    data = fetch_data(query)
    return data

def get_api_key():
    """() -> api_key

    Reads the `CONFIG.ini` file for the [eBayAPI] indicator, reads in the respective api_key, and returns the value."""
    api_key = CONFIG['eBayAPI']['api_key']
    return api_key

def get_search_words():
    """() -> list

    Returns a static list with pre-defined search words. Used for searching active & completed products."""
    words = ['Alpha Black Lotus', 'Alpha Mox Sapphire', 'Alpha Mox Jet', 'Alpha Mox Pearl', 'Alpha Mox Ruby', 'Alpha Mox Emerald', 'Alpha Timetwister', 'Alpha Ancestral Recall', 'Alpha Time Walk',
                'Beta Black Lotus MTG', 'Beta Mox Sapphire', 'Beta Mox Jet', 'Beta Mox Pearl', 'Beta Mox Ruby', 'Beta Mox Emerald', 'Beta Timetwister', 'Beta Ancestral Recall', 'Beta Time Walk',
                'Unlimited Black Lotus MTG', 'Unlimited Mox Sapphire', 'Unlimited Mox Jet', 'Unlimited Mox Pearl', 'Unlimited Mox Ruby', 'Unlimited Mox Emerald', 'Unlimited Timetwister', 'Unlimited Ancestral Recall', 'Unlimited Time Walk',
                'Alpha Tundra MTG', 'Alpha Underground Sea MTG', 'Alpha Badlands MTG', 'Alpha Taiga MTG', 'Alpha Savannah MTG', 'Alpha Scrubland MTG', 'Alpha Volcanic Island MTG', 'Alpha Bayou MTG', 'Alpha Plateau MTG', 'Alpha Tropical Island MTG',
                'Beta Tundra MTG', 'Beta Underground Sea MTG', 'Beta Badlands MTG', 'Beta Taiga MTG', 'Beta Savannah MTG', 'Beta Scrubland MTG', 'Beta Volcanic Island MTG', 'Beta Bayou MTG', 'Beta Plateau MTG', 'Beta Tropical Island MTG',
                'Unlimited Tundra MTG', 'Unlimited Underground Sea MTG', 'Unlimited Badlands MTG', 'Unlimited Taiga MTG', 'Unlimited Savannah MTG', 'Unlimited Scrubland MTG', 'Unlimited Volcanic Island MTG', 'Unlimited Bayou MTG', 'Unlimited Plateau MTG', 'Unlimited Tropical Island MTG',
                'Revised Tundra MTG', 'Revised Underground Sea MTG', 'Revised Badlands MTG', 'Revised Taiga MTG', 'Revised Savannah MTG', 'Revised Scrubland MTG', 'Revised Volcanic Island MTG', 'Revised Bayou MTG', 'Revised Plateau MTG', 'Revised Tropical Island MTG',
                'Alpha Time Vault MTG', 'Beta Time Vault MTG', 'Unlimited Time Vault MTG', "Collectors Time Vault MTG", "International Collectors Time Vault MTG",
                "Collectors Black Lotus MTG", "Collectors Mox Sapphire", "Collectors Mox Jet", "Collectors Mox Pearl", "Collectors Mox Ruby", "Collectors Mox Emerald", "Collectors Timetwister", "Collectors Ancestral Recall", "Collectors Time Walk",
                "International Collectors Black Lotus MTG", "International Collectors Mox Sapphire", "International Collectors Mox Jet", "International Collectors Mox Pearl", "International Collectors Mox Ruby", "International Collectors Mox Emerald", "International Collectors Timetwister", "International Collectors Ancestral Recall", "International Collectors Time Walk",
                "Collectors Tundra MTG", "Collectors Underground Sea MTG", "Collectors Badlands MTG", "Collectors Taiga MTG", "Collectors Savannah MTG", "Collectors Scrubland MTG", "Collectors Volcanic Island MTG", "Collectors Bayou MTG", "Collectors Plateau MTG", "Collectors Tropical Island MTG",
                "International Collectors Tundra MTG", "International Collectors Underground Sea MTG", "International Collectors Badlands MTG", "International Collectors Taiga MTG", "International Collectors Savannah MTG", "International Collectors Scrubland MTG", "International Collectors Volcanic Island MTG", "International Collectors Bayou MTG", "International Collectors Plateau MTG", "International Collectors Tropical Island MTG"]
    return words

def get_test_search_words():
    """() -> list

    Returns a list of selected search words we can test against"""
    words = ['Unlimited Black Lotus MTG', 'Revised Tropical Island MTG', 'Beta Badlands MTG']
    return words

def csv_reader(csv_path):
    """(path: str, list: list) -> list

    Takes in a designated path to the desired .csv and appends the rows to a global list."""
    setList = []
    with open(csv_path, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            setList.append(row[0])
        return setList

def get_timezones(period_length):
    CST = pytz.timezone('US/Central')
    OLDEST_DATE = (datetime.now(CST) + timedelta(days=1)) - timedelta(days=period_length)
    return OLDEST_DATE
