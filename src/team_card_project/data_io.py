# ====================================================================================================
# FUNCTIONS FOR LOADING AND SAVING DIFFERENT FILES
# ====================================================================================================

# Imports
import pandas as pd
from PIL import Image
import os
from team_card_project import constants

DATA_DIR = constants.DATA_DIR
PROJECT_DIR = constants.PROJECT_DIR


def get_prev_season(cur_season: str) -> str:
    """
    Return the str for the previous season from a given season's str.

    :param cur_season: A str of the current season ('YYYY-YYYY')
    :return: A str of the season previous to the current season
    """
    start_year, end_year = map(int, cur_season.split("-"))
    prev_season = f"{start_year - 1}-{end_year - 1}"

    return prev_season


def load_card_data_csv(season: str) -> pd.DataFrame:
    """
    Load the team card data CSV for a given season.

    :param season: A str representing the season ('YYYY-YYYY')
    :return: The DataFrame of the loaded card data
    """

    file_name = f'{season}_team_card_data.csv'
    # Card data lives in data/card_data/team_card_data/ (the layout the stats collection project writes)
    file_path = os.path.join(DATA_DIR, 'card_data', 'team_card_data', file_name)

    card_data_df = pd.read_csv(file_path)
    return card_data_df


def save_card(card: Image, season: str, file_name: str, *subfolders: str) -> None:
    """
    Save a card PNG to the team_cards folder, inside the season's folder (and any further folders given inside it).

    :param card: The card image to save
    :param season: A str representing the season ('YYYY-YYYY')
    :param file_name: Name of the card to save
    :param subfolders: Any folders inside the season folder to save to
    :return: None
    """
    save_dir = os.path.join(PROJECT_DIR, 'team_cards', season, *subfolders)
    os.makedirs(save_dir, exist_ok=True)

    save_path = os.path.join(save_dir, file_name)

    card.save(save_path, 'PNG')
    print(f"Saved {file_name}")
