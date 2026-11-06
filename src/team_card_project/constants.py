# ====================================================================================================
# GET PROJECT FILE LOCATION
# ====================================================================================================

# Imports
import os

def find_project_dir(start_dir: str) -> str:
    """
    Traverse upward until a directory containing 'data' is found.

    :param start_dir: Directory where the search starts
    :return: Project root directory
    """

    project_dir = None
    while project_dir is None:
        potential_data_dir = os.path.join(start_dir, 'data')

        if os.path.exists(potential_data_dir):
            project_dir = start_dir
        else:
            parent = os.path.dirname(start_dir)

            if parent == start_dir:
                raise FileNotFoundError('Could not find "data" folder')

            start_dir = parent
    return project_dir


# Directory of the current file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.environ.get('NHL_CARD_DATA_DIR')

# Root project directory
if DATA_DIR:
    PROJECT_DIR = os.path.dirname(DATA_DIR)
else:
    PROJECT_DIR = find_project_dir(CURRENT_DIR)
    DATA_DIR = os.path.join(PROJECT_DIR, 'data')

# Card assets (fonts and team logos)
ASSETS_DIR = os.path.join(DATA_DIR, 'card_data', 'assets')


# ====================================================================================================
# CARD GENERATION CONSTANTS
# ====================================================================================================

# Date card data was updated on
UPDATE_DATE = 'Sep 1, 2026'

# === NAMING ===
# Symbols to be replaced in team names for the header
SYMBOLS_TO_REPLACE = {
    'é': 'e',
    'É': 'E',
}

# The stat sections of the card: (title, five stats top to bottom, None leaves a slot blank). Each stat is (name shown on the card and its
# card data column, how the value is shown: 'rate' = 2 decimals, 'signed' = 2 decimals with a sign, 'time' = +MM:SS)
TEAM_STAT_SECTIONS = [
    ('Offense', [
        ('Goals For', 'rate'),
        ('xGoals For', 'rate'),
        ('LD Shots For', 'rate'),
        ('MD Shots For', 'rate'),
        ('HD Shots For', 'rate'),
    ]),
    ('Defense', [
        ('Goals Against', 'rate'),
        ('xGoals Against', 'rate'),
        ('LD Shots Against', 'rate'),
        ('MD Shots Against', 'rate'),
        ('HD Shots Against', 'rate'),
    ]),
    ('Special Teams', [
        ('5v4 Goals For', 'rate'),
        ('5v4 xGoals For', 'rate'),
        ('4v5 Goals Against', 'rate'),
        ('4v5 xGoals Against', 'rate'),
        ('Net PIMs', 'time'),
    ]),
]

# Font sizes shared by every card (the largest that fit the longest text)
STAT_FONT_SIZE = 60
TITLE_FONT_SIZE = 75
BRANDING_FONT_SIZE = 38

# Space above and below the outer lines of the Elo and SRS graphs, as a fraction of the distance between those lines
GRAPH_PAD = 0.06

# === FONTS ===
BASIC_FONT_PATH = os.path.join(ASSETS_DIR, 'fonts', 'basic.ttf')
HEADING_FONT_PATH = os.path.join(ASSETS_DIR, 'fonts', 'header.ttf')

# === COLORS ===
# Card color RGB values
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK = (39, 39, 39)
SECTION_LIGHT = (236, 236, 236)
SECTION_DARK = (54, 54, 54)

# Stat bar gradient (low to high), the same red, purple, and blue as the website
STAT_GRADIENT_COLORS = [(255, 99, 99), (210, 110, 210), (99, 99, 255)]
# Share of the bar at each end that stays solid red or blue
STAT_GRADIENT_SOLID_FRACTION = 0.12

# Team primary color RBG values
PRIMARY_COLORS = {
    'ANA': (252, 76, 2),    'ARI': (140, 38, 51),   'BOS': (252, 181, 20),
    'BUF': (0, 48, 135),    'CGY': (210, 0, 28),    'CAR': (206, 17, 38),
    'CHI': (207, 10, 44),   'COL': (111, 38, 61),   'CBJ': (0, 38, 84),
    'DAL': (0, 104, 71),    'DET': (206, 17, 38),   'EDM': (252, 76, 0),
    'FLA': (200, 16, 46),   'LAK': (162,170,173),   'MIN': (2, 73, 48),
    'MTL': (175, 30, 45),   'NSH': (255, 184, 28),  'NJD': (206, 17, 38),
    'NYI': (244, 125, 48),  'NYR': (0, 56, 168),    'OTT': (218, 26, 50),
    'PHI': (247, 73, 2),    'PIT': (252, 181, 20),  'SJS': (0, 109, 117),
    'SEA': (153, 217, 217), 'STL': (0, 47, 135),    'TBL': (0, 40, 104),
    'TOR': (0, 32, 91),     'VAN': (0, 32, 91),     'UTA': (105, 179, 231),
    'VGK': (185, 151, 91),  'WSH': (4, 30, 66),     'WPG': (4, 30, 66),
    'ATL': (4, 30, 66),     'PHX': (140, 38, 51)
}

# Team secondary colors RGB values
SECONDARY_COLORS = {
    'ANA': (185, 151, 91),  'ARI': (21,71,52),      'BOS': (17, 17, 17),
    'BUF': (255, 184, 28),  'CGY': (250, 175, 25),  'CAR': (0, 0, 0),
    'CHI': (0, 0, 0),       'COL': (35, 97, 146),   'CBJ': (206,17,38),
    'DAL': (143, 143, 140), 'DET': (0, 0, 0),       'EDM': (4, 30, 66),
    'FLA': (4,30,66),       'LAK': (17, 17, 17),    'MIN': (175, 35, 36),
    'MTL': (25, 33, 104),   'NSH': (4,30,66),       'NJD': (0, 0, 0),
    'NYI': (0,83,155),      'NYR': (206,17,38),     'OTT': (0, 0, 0),
    'PHI': (0, 0, 0),       'PIT': (0, 0, 0),       'SJS': (0, 0, 0),
    'SEA': (0, 22, 40),     'STL': (252, 181, 20),  'TBL': (0, 0, 0),
    'TOR': (0, 0, 0),       'VAN': (0, 132, 61),    'UTA': (0, 0, 0),
    'VGK': (51,63,72),      'WSH': (200, 16, 46),   'WPG': (172,22,44),
    'ATL': (184, 97, 37),   'PHX': (21,71,52)
}



# ====================================================================================================
# TEAMS, DIVISIONS, AND NUMBER OF GAMES PER SEASON
# ====================================================================================================

# Games per season
SEASON_GAMES = {
    '2026-2027': 84,    # Current season (max games any team has played)
    '2025-2026': 82,
    '2024-2025': 82,
    '2023-2024': 82,
    '2022-2023': 82,
    '2021-2022': 82,
    '2020-2021': 56,    # Shortened due to COVID
    '2019-2020': 71,    # Season paused due to COVID
    '2018-2019': 82,
    '2017-2018': 82,
    '2016-2017': 82,
    '2015-2016': 82,
    '2014-2015': 82,
    '2013-2014': 82,
    '2012-2013': 48,    # Shortened due to lockout
    '2011-2012': 82,
    '2010-2011': 82,
    '2009-2010': 82,
    '2008-2009': 82,
    '2007-2008': 82
}

# Teams per season
SEASON_TEAM_NUM = {
    '2026-2027': 32,
    '2025-2026': 32,
    '2024-2025': 32,
    '2023-2024': 32,
    '2022-2023': 32,
    '2021-2022': 32,    # Seattle Kraken Added
    '2020-2021': 31,
    '2019-2020': 31,
    '2018-2019': 31,
    '2017-2018': 31,    # Vegas Golden Knights Added
    '2016-2017': 30,
    '2015-2016': 30,
    '2014-2015': 30,
    '2013-2014': 30,
    '2012-2013': 30,
    '2011-2012': 30,
    '2010-2011': 30,
    '2009-2010': 30,
    '2008-2009': 30,
    '2007-2008': 30
}
