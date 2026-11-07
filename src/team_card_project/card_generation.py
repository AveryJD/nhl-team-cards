# ====================================================================================================
# FUNCTIONS FOR TEAM CARD CREATION
# ====================================================================================================

# Imports
import os
import ast
import io
import pandas as pd
import cairosvg
from PIL import Image, ImageDraw, ImageFont
from team_card_project import card_utils as ch
from team_card_project import constants
from team_card_project import data_io


DATA_DIR = constants.DATA_DIR

# Load and cache fonts
BASIC_FONT_PATH = constants.BASIC_FONT_PATH
HEADING_FONT_PATH = constants.HEADING_FONT_PATH

FONT_CACHE = {
    'basic_34': ImageFont.truetype(BASIC_FONT_PATH, 34),
    'basic_42': ImageFont.truetype(BASIC_FONT_PATH, 42),
    'basic_46': ImageFont.truetype(BASIC_FONT_PATH, 46),
    'basic_50': ImageFont.truetype(BASIC_FONT_PATH, 50),
    'stat': ImageFont.truetype(BASIC_FONT_PATH, 60),
    'title': ImageFont.truetype(HEADING_FONT_PATH, 76),
    'branding': ImageFont.truetype(BASIC_FONT_PATH, 41),
    'name': ImageFont.truetype(HEADING_FONT_PATH, 108),
    'header': ImageFont.truetype(BASIC_FONT_PATH, 60),
}


def make_header_section(team_row: pd.Series, mode: str = 'light') -> Image:
    """
    Creates the header section of a team card as a PIL Image. The header includes a team colored banner with the team's name and season, the team logo,
    and the team's standings and season stats (per game).

    :param team_row: A Series containing team data
    :param mode: A str determining the style of card ('light' or 'dark')
    :return: An Image of the header section
    """

    # Get basic team information
    team_name = team_row['Team']
    team_abbrev = team_row['Team Abbreviation']
    season = team_row['Season']

    # Get color variables
    colors = ch.get_mode_colors(mode)
    section_color = colors['section']
    text_color = colors['text']
    primary_team_color = constants.PRIMARY_COLORS.get(team_abbrev)
    header_text_color = constants.WHITE
    header_shadow_color = constants.SECONDARY_COLORS.get(team_abbrev)

    # Get standings variables
    record = f"{int(team_row['Wins'])}-{int(team_row['Losses'])}-{int(team_row['Overtime/Shootout Losses'])}"
    points = str(int(team_row['Points']))
    point_percent = f"{float(team_row['Point %']):.3f}"
    division_rank = ch.get_ordinal(int(team_row['Division Rank']))
    league_rank = ch.get_ordinal(int(team_row['League Rank']))
    standings_rows = [
        ('Record:', record), ('Points:', points), ('Point %:', point_percent), ('Division Rank:', division_rank), ('League Rank:', league_rank),
    ]

    # Get season stats variables (per game, all situations) and the 5v5 expected goal share from the card's 5v5 rates
    games_played = int(team_row['Games Played'])
    xgoals_for, goals_for = float(team_row['Season xGoals For']), int(team_row['Season Goals For'])
    xgoals_against, goals_against = float(team_row['Season xGoals Against']), int(team_row['Season Goals Against'])
    xgf_5v5, xga_5v5 = float(team_row['xGoals For']), float(team_row['xGoals Against'])
    season_stats_rows = [
        ('GF/GP:', f'{goals_for / games_played:.2f}'),
        ('GA/GP:', f'{goals_against / games_played:.2f}'),
        ('xGF/GP:', f'{xgoals_for / games_played:.2f}'),
        ('xGA/GP:', f'{xgoals_against / games_played:.2f}'),
        ('5v5 xGF%:', f'{xgf_5v5 / (xgf_5v5 + xga_5v5):.1%}'),
    ]

    # Create header section
    header_section_width = 1880
    header_section_height = 535
    header_section = Image.new("RGB", (header_section_width, header_section_height), color=section_color)

    # Create draw object
    draw = ImageDraw.Draw(header_section)

    # Load fonts
    basic_font = FONT_CACHE['header']
    heading_font = FONT_CACHE['name']
    subheading_font = FONT_CACHE['title']

    # The header has the logo on the left, then the standings and the season stats
    third_width = header_section_width / 3
    # The x position of the center of each column of header text (the logo is centered in the first third of the header)
    third_centers = [313, 940, 1567]
    banner_height = 110
    body_height = header_section_height - banner_height

    # Crop the logo and scale it to fit the first third
    logo_margin = 24
    team_logo = ch.load_team_logo(team_abbrev, mode, 1600)
    team_logo = team_logo.crop(team_logo.getchannel('A').point(lambda value: 255 if value > 8 else 0).getbbox())
    logo_scale = min((third_width - 80) / team_logo.width, (body_height - 2 * logo_margin) / team_logo.height)
    team_logo = team_logo.resize((round(team_logo.width * logo_scale), round(team_logo.height * logo_scale)), Image.Resampling.LANCZOS)
    logo_y = banner_height + (body_height - team_logo.height) // 2
    header_section.paste(team_logo, (third_centers[0] - team_logo.width // 2, logo_y), team_logo)

    # Draw banner (the name's capital letters, with their 4 pixel drop shadow, are centered in it)
    draw.rectangle([(0, 0), (header_section_width, banner_height)], fill=primary_team_color)
    name_cap_top, name_cap_bottom = heading_font.getbbox('H')[1], heading_font.getbbox('H')[3]
    name_y = round((banner_height - (name_cap_bottom - name_cap_top) - 4) / 2) - name_cap_top
    # Draw team name and season drop shadow
    draw.text(xy=(36, name_y + 4), text=team_name, font=heading_font, fill=header_shadow_color)
    ch.draw_righted_text(draw, season, heading_font, name_y + 4, header_section_width - 44, fill=header_shadow_color)
    # Draw team name and season text
    draw.text(xy=(40, name_y), text=team_name, font=heading_font, fill=header_text_color)
    ch.draw_righted_text(draw, season, heading_font, name_y, header_section_width - 40, fill=header_text_color)

    # Row y positions
    row_pitch = 62
    title_to_first_row = 80
    title_cap_top = subheading_font.getbbox('H')[1]
    last_row_baseline = basic_font.getmetrics()[0]
    content_height = (title_to_first_row + 4 * row_pitch + last_row_baseline) - title_cap_top
    edge_space = (body_height - content_height) // 2
    title_y = banner_height + edge_space - title_cap_top
    row_ys = [title_y + title_to_first_row + row_num * row_pitch for row_num in range(5)]

    # Draw standings and season stats (labels and values both left aligned, centered as a block)
    label_gap = 26
    # Width in pixels of the widest value in the standings and season stats rows across all card data
    standings_value_width = 151
    season_stats_value_width = 104
    for title, rows, center_x, value_width in [
        ('Standings', standings_rows, third_centers[1], standings_value_width),
        ('Season Stats', season_stats_rows, third_centers[2], season_stats_value_width),
    ]:
        ch.draw_centered_text(draw, title, subheading_font, title_y, x_center=center_x, fill=text_color)

        # Every card puts its labels and values in the same place, centered for the widest values in the data
        label_width = max(basic_font.getlength(label) for label, _ in rows)
        label_left = center_x - (label_width + label_gap + value_width) / 2
        value_x = label_left + label_width + label_gap
        for row_y, (label, value) in zip(row_ys, rows):
            draw.text(xy=(label_left, row_y), text=label, font=basic_font, fill=text_color)
            draw.text(xy=(value_x, row_y), text=value, font=basic_font, fill=text_color)

    return header_section


def make_stat_component(name: str, value: str, percentile: int, width: int, height: int, mode: str = 'light', size: str = 'small') -> Image:
    """
    Creates a stat component: the stat name and value above a bar filled with a gradient up to the percentile (written on the bar). A stat with no percentile
    gets a grey bar marked N/A, and a stat with no value shows N/A as its value.

    :param name: A str of the stat's name
    :param value: A str of the stat's value (None if it has none)
    :param percentile: An int of the percentile of the stat (None if it has none)
    :param width: An int of the component's width in pixels
    :param height: An int of the component's height in pixels
    :param mode: A str determining the style of card ('light' or 'dark')
    :param size: A str of the size of the component's text and bar ('small' or 'large')
    :return: An Image of the stat component
    """

    # Get color variables
    colors = ch.get_mode_colors(mode)
    section_color = colors['section']
    text_color = colors['text']

    # Get size variables
    sizes = ch.get_stat_component_sizes(size)
    name_font = FONT_CACHE[sizes['name_font']]
    value_font = FONT_CACHE[sizes['value_font']]
    percentile_font = FONT_CACHE[sizes['percentile_font']]
    bar_height = sizes['bar_height']
    edge_pad = sizes['edge_pad']
    bar_gap = sizes['bar_gap']
    percentile_stroke = sizes['percentile_stroke']
    percentile_str = None if percentile is None else str(percentile)
    fraction = None if percentile is None else percentile / 100

    # Create stat component
    stat_component = Image.new("RGB", (width, height), color=section_color)

    # Get row y positions
    name_top = name_font.getbbox('H')[1]
    bar_y = name_font.getbbox('H')[3] - name_top + bar_gap
    name_baseline_y = name_font.getmetrics()[0] - name_top

    # Draw the bar at a larger size so its edges are smooth (the percentile is drawn at the larger size too, so its stroke can be a fraction of a pixel)
    scale = 4
    shapes = Image.new('RGBA', (width * scale, height * scale), (0, 0, 0, 0))
    bar_left, bar_right = edge_pad, width - edge_pad
    percentile_font_large = ImageFont.truetype(BASIC_FONT_PATH, percentile_font.size * scale)
    # The design of the stat bar: the share of the gradient at each end that stays solid red or blue, the smallest fill (0 percentile) as a share of the bar's height,
    # how far the end of the fill holds its percentile's color (a share of the bar's height), and the space between the percentile number and the end of the fill (a share of the bar's height)
    solid_fraction, min_fill, end_hold, label_gap = 0.12, 0.8, 1.2, 0.2
    bar = ch.make_percentile_bar(
        (bar_right - bar_left) * scale, bar_height * scale, fraction, colors['unqualified_bar'], percentile_str, percentile_font_large,
        round(percentile_stroke * scale),
        solid_fraction=solid_fraction, min_fill=min_fill, end_hold=end_hold, label_gap=label_gap,
    )
    shapes.paste(bar, (bar_left * scale, bar_y * scale), bar)
    # Scale back down (BOX avoids the halo LANCZOS leaves)
    shapes = shapes.resize((width, height), Image.Resampling.BOX)
    stat_component.paste(shapes, (0, 0), shapes)

    # Create draw object
    draw = ImageDraw.Draw(stat_component)

    # Draw the stat's name (lined up with the bar's left edge)
    name_left_offset = draw.textbbox((0, 0), name, font=name_font)[0]
    draw.text(xy=(bar_left - name_left_offset, -name_top), text=name, font=name_font, fill=text_color)

    # Draw the value beside the stat name (on its baseline, ending at the right end of the bar)
    draw.text(xy=(bar_right, name_baseline_y), text=value or 'N/A', font=value_font, fill=text_color, anchor='rs')

    return stat_component


def make_elo_section(team_row: pd.Series, mode: str = 'light', width: int = 925, height: int = 730) -> Image:
    """
    Creates the Elo section of a team card as a PIL Image: a graph of the team's Elo rating through the season.

    :param team_row: A Series containing team data
    :param mode: A str determining the style of card ('light' or 'dark')
    :param width: An int of the section's width in pixels
    :param height: An int of the section's height in pixels
    :return: An Image of the Elo section
    """

    # Get color variables
    colors = ch.get_mode_colors(mode)
    text_color = colors['text']
    grid_color = colors['graph_grid']

    # Create Elo section
    elo_section = Image.new("RGB", (width, height), color=colors['section'])

    # Create draw object
    draw = ImageDraw.Draw(elo_section)
    title_font = FONT_CACHE['title']
    number_font = FONT_CACHE['basic_34']
    label_font = FONT_CACHE['basic_46']

    # The left side of the graph holds the numbers of its lines
    number_width = round(draw.textlength('1700', font=number_font)) + 12
    plot_top = 135
    plot_height = height - plot_top - 105
    label_y = plot_top + plot_height + 28

    # Draw the Elo rating graph: the rating after each game, with lines every 100 points
    elo_history = ast.literal_eval(team_row['Elo History'])
    season_games = team_row['Season Games']
    # Space above and below the outer lines of the graph, as a fraction of the distance between those lines
    graph_pad = 0.06
    elo_low = min(1300, int(min(elo_history) // 100 * 100))
    elo_high = max(1700, int(-(-max(elo_history) // 100) * 100))
    elo_ticks = list(range(elo_low, elo_high + 1, 100))
    elo_left = 40 + number_width
    elo_width = width - 40 - 40 - number_width
    ch.draw_centered_text(draw, 'Elo Rating Per Game', title_font, 24, x_center=width // 2, fill=text_color)
    elo_x, elo_y = ch.draw_line_chart(
        elo_section, elo_left, plot_top, elo_width, plot_height, list(range(len(elo_history))), elo_history,
        x_range=(-1, season_games + 1), y_range=(elo_low - graph_pad * (elo_high - elo_low), elo_high + graph_pad * (elo_high - elo_low)), y_ticks=elo_ticks,
        line_color=text_color, grid_color=grid_color, line_width=5,
    )
    for tick in elo_ticks:
        draw.text((elo_left - 12, elo_y(tick)), str(tick), font=number_font, fill=grid_color, anchor='rm')
    for game in [0, int(season_games * 0.25), int(season_games * 0.5), int(season_games * 0.75), season_games]:
        draw.text((elo_x(game), label_y), str(game), font=label_font, fill=text_color, anchor='mt')

    return elo_section


def make_srs_section(team_row: pd.Series, mode: str = 'light', width: int = 925, height: int = 730) -> Image:
    """
    Creates the SRS section of a team card as a PIL Image: a graph of the team's SRS rank each of the last five seasons.

    :param team_row: A Series containing team data
    :param mode: A str determining the style of card ('light' or 'dark')
    :param width: An int of the section's width in pixels
    :param height: An int of the section's height in pixels
    :return: An Image of the SRS section
    """

    season = team_row['Season']

    # Get color variables
    colors = ch.get_mode_colors(mode)
    text_color = colors['text']
    grid_color = colors['graph_grid']

    # Create SRS section
    srs_section = Image.new("RGB", (width, height), color=colors['section'])

    # Create draw object
    draw = ImageDraw.Draw(srs_section)
    title_font = FONT_CACHE['title']
    number_font = FONT_CACHE['basic_34']
    label_font = FONT_CACHE['basic_46']

    # The left side of the graph holds the numbers of its lines
    number_width = round(draw.textlength('1700', font=number_font)) + 12
    plot_top = 135
    plot_height = height - plot_top - 105
    label_y = plot_top + plot_height + 28

    # Draw the SRS rank graph (1st is at the top)
    srs_history = ast.literal_eval(team_row['SRS Rank History'])[-5:]
    seasons = [season]
    for _ in range(len(srs_history) - 1):
        seasons.append(data_io.get_prev_season(seasons[-1]))
    seasons.reverse()
    # Space above and below the outer lines of the graph, as a fraction of the distance between those lines
    graph_pad = 0.06
    total_teams = int(team_row['Season Teams'])
    srs_ticks = [1, 8, 16, 24, total_teams]
    srs_left = 40 + number_width
    srs_width = width - 40 - 40 - number_width
    ch.draw_centered_text(draw, 'SRS Ranking Per Season', title_font, 24, x_center=width // 2, fill=text_color)
    srs_x, srs_y = ch.draw_line_chart(
        srs_section, srs_left, plot_top, srs_width, plot_height, list(range(len(srs_history))), srs_history,
        x_range=(-0.5, len(srs_history) - 0.5), y_range=(1 - graph_pad * (total_teams - 1), total_teams + graph_pad * (total_teams - 1)), y_ticks=srs_ticks,
        line_color=text_color, grid_color=grid_color, line_width=6, dot_radius=14, invert_y=True,
    )
    for tick in srs_ticks:
        draw.text((srs_left - 12, srs_y(tick)), str(tick), font=number_font, fill=grid_color, anchor='rm')
    for season_num, graph_season in enumerate(seasons):
        draw.text((srs_x(season_num), label_y), f'{graph_season[2:4]}-{graph_season[7:9]}', font=label_font, fill=text_color, anchor='mt')

    return srs_section


def make_stat_group_section(team_row: pd.Series, title: str, stats: list, width: int, height: int, mode: str = 'light', component_pitch: float = None) -> Image:
    """
    Creates a section of a team card that holds a title and a column of stat components (Ex: the offense stats).

    :param team_row: A Series containing team data
    :param title: A str of the section's title
    :param stats: A list of the stats to show, from top to bottom, each (card data column, how its value is shown, and optionally the name to show)
    :param width: An int of the section's width in pixels
    :param height: An int of the section's height in pixels
    :param mode: A str determining the style of card ('light' or 'dark')
    :param component_pitch: A float of the distance between stat components' tops (default spreads them evenly down the section)
    :return: An Image of the stat group section
    """

    # Get color variables
    colors = ch.get_mode_colors(mode)

    # Create stat group section
    group_section = Image.new("RGB", (width, height), color=colors['section'])

    # Create draw object
    draw = ImageDraw.Draw(group_section)

    # Draw title
    ch.draw_centered_text(draw, text=title, font=FONT_CACHE['title'], y_position=14, x_center=width // 2, fill=colors['text'])

    # Draw stat components, spread evenly down the section unless a pitch is given
    component_height, top_padding, bottom_padding = 130, 112, 22
    if component_pitch is None:
        component_pitch = (height - top_padding - bottom_padding - component_height) / (len(stats) - 1)
    for component_num, (column, kind, *label) in enumerate(stats):
        rate = float(team_row[column])
        value = f'{rate:.1f}%' if kind == 'percent' else f'{rate:.2f}'
        percentile = int(team_row[f'{column} Percentile'])
        component = make_stat_component(label[0] if label else column, value, percentile, width - 80, component_height, mode, size='small')
        group_section.paste(component, (40, top_padding + round(component_num * component_pitch)))

    return group_section


def make_branding_section(mode: str = 'light') -> Image:
    """
    Creates the branding section Image for a team card. The branding section contains the data notes on the left (wrapping before they reach the website and
    socials), my website and socials stacked to the left of the logo, and the logo on the right.

    :param mode: A str determining the style of card ('light' or 'dark')
    :return: An Image of branding section
    """

    # Get color variables
    colors = ch.get_mode_colors(mode)
    section_color = colors['section']
    text_color = colors['text']

    # Get the updated date
    update_date = constants.UPDATE_DATE

    # Create branding section
    branding_section_width = 1880
    branding_section_height = 125
    branding_section = Image.new("RGB", (branding_section_width, branding_section_height), color=section_color)

    # Create draw image
    draw = ImageDraw.Draw(branding_section)

    # Add logo (the logo's knocked out areas are the section's color)
    with open(os.path.join(constants.ASSETS_DIR, 'images', 'analyticswithavery_logo.svg'), 'r') as f:
        svg_text = f.read()
    svg_text = svg_text.replace('<rect width="1000" height="1000" fill="#272727"/>', '')
    svg_text = svg_text.replace('#272727', '#{:02x}{:02x}{:02x}'.format(*section_color))
    logo = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg_text.encode(), output_width=1000, output_height=1000))).convert('RGBA')
    logo = logo.crop(logo.getbbox())
    logo_height = 98
    logo = logo.resize((int(logo.width * logo_height / logo.height), logo_height), Image.Resampling.LANCZOS)
    # The logo is on the right side
    logo_x = branding_section_width - 30 - logo.width
    branding_section.paste(logo, (logo_x, (branding_section_height - logo_height) // 2), logo)

    # Get the font and the line height
    basic_font = FONT_CACHE['branding']
    line_height = round(FONT_CACHE['branding'].size * 1.1)
    text_left = 40

    # Website and socials text, to the left of the logo
    contact_lines = ['Website: analyticswithavery.com', 'Socials: @analyticswavery']
    contact_width = max(draw.textlength(line, font=basic_font) for line in contact_lines)
    contact_x = logo_x - 40 - contact_width
    contact_top = ch.get_centered_text_top(basic_font, 2, line_height, branding_section_height)
    for line_num, line in enumerate(contact_lines):
        draw.text(xy=(contact_x, contact_top + line_num * line_height), text=line, font=basic_font, fill=text_color)

    # Data notes text (wraps before the website and socials)
    data_notes = (
        'Data is adjusted to a per 60 minute rate for 5v5 stats and a per 2 minute rate for special team stats. '
        'Percentiles compare all teams in the league. '
        f'All data and images from the NHL. Updated {update_date}.'
    )
    text_max_width = contact_x - 40 - text_left
    lines = ['']
    for word in data_notes.split(' '):
        candidate = f'{lines[-1]} {word}'.strip()
        if draw.textlength(candidate, font=basic_font) <= text_max_width or not lines[-1]:
            lines[-1] = candidate
        else:
            lines.append(word)
    data_top = ch.get_centered_text_top(basic_font, len(lines), line_height, branding_section_height)
    for line_num, line in enumerate(lines):
        draw.text(xy=(text_left, data_top + line_num * line_height), text=line, font=basic_font, fill=text_color)

    return branding_section


def make_team_card(team: str, season: str, mode: str = 'light', save: bool = True) -> Image:
    """
    Create a full team card image for a given team and season.

    The card has a header section, an Elo section and an SRS section side by side (the team's Elo rating and SRS rank), four stat sections (5v5 offense, 5v5
    defense, and the 5v4 offense and 4v5 defense stacked in one column), and a branding section.

    :param team: Full team name
    :param season: Season string ('YYYY-YYYY')
    :param mode: Card style ('light' or 'dark')
    :param save: Whether to save the generated card as a PNG
    :return: PIL Image containing the completed team card
    """

    # Get the team's card data for the given season
    team_row = ch.get_team_single_season(team, season)

    team_abbrev = team_row['Team Abbreviation']

    # Get color variables
    colors = ch.get_mode_colors(mode)

    # Create team card
    card_width = 2000
    card_height = 2500
    team_card = Image.new('RGB', (card_width, card_height), color=colors['background'])

    # Spacing between sections and the section corner radius
    spacing = 30
    margin = spacing * 2
    radius = 38

    # Add header section (only the very top and bottom corners of the card's sections are rounded)
    header_section = make_header_section(team_row, mode)
    header_y = margin
    ch.paste_rounded(team_card, header_section, (margin, header_y), radius, corners=(True, True, False, False))

    # Add the Elo and SRS sections side by side (shorter than the stat sections)
    graph_section_height = 730
    stat_section_height = 900
    graph_y = header_y + header_section.height + spacing
    graphs_width = card_width - 2 * margin
    elo_width = (graphs_width - spacing) // 2 + (graphs_width - spacing) % 2
    srs_width = (graphs_width - spacing) // 2
    elo_section = make_elo_section(team_row, mode, elo_width, graph_section_height)
    ch.paste_rounded(team_card, elo_section, (margin, graph_y), radius, corners=(False, False, False, False))
    srs_section = make_srs_section(team_row, mode, srs_width, graph_section_height)
    ch.paste_rounded(team_card, srs_section, (margin + elo_width + spacing, graph_y), radius, corners=(False, False, False, False))

    # Add the three columns of stat group sections side by side (a column with more than one section stacks them)
    groups_y = graph_y + graph_section_height + spacing
    groups_width = card_width - 2 * margin
    group_x = margin
    component_pitch = (stat_section_height - 112 - 22 - 130) / (max(len(stats) for column in constants.TEAM_STAT_COLUMNS for _, stats in column) - 1)
    for column_num, column in enumerate(constants.TEAM_STAT_COLUMNS):
        # Split the width evenly (any leftover pixels go to the first columns)
        width = (groups_width - 2 * spacing) // 3 + (1 if column_num < (groups_width - 2 * spacing) % 3 else 0)
        # Stacked sections keep the same component pitch as the tallest column, so their stat components line up across the card; the sections'
        # heights fit their components (the first section takes any leftover height)
        section_heights = [112 + (len(stats) - 1) * component_pitch + 130 + 22 for _, stats in column]
        section_heights[0] += stat_section_height - sum(section_heights) - (len(column) - 1) * spacing
        section_y = groups_y
        for (title, stats), section_height in zip(column, section_heights):
            group_section = make_stat_group_section(team_row, title, stats, width, round(section_height), mode, component_pitch)
            ch.paste_rounded(team_card, group_section, (group_x, round(section_y)), radius, corners=(False, False, False, False))
            section_y += section_height + spacing
        group_x += width + spacing

    # Add branding section
    branding_section = make_branding_section(mode)
    branding_y = groups_y + stat_section_height + spacing
    ch.paste_rounded(team_card, branding_section, (margin, branding_y), radius, corners=(False, False, True, True))

    # Save team card
    team_card = team_card.convert('RGB')
    file_name = f'{season}_{team_abbrev}_{mode}.png'
    if save:
        data_io.save_card(team_card, season, file_name)

    print(f'========== {team} card ({mode}) created for the {season} season! ==========')

    return team_card
