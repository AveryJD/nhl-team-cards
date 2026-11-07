# ====================================================================================================
# CARD CREATION HELPER FUNCTIONS
# ====================================================================================================

# Imports
import os
import io
import pandas as pd
import numpy as np
import cairosvg
from PIL import Image, ImageChops, ImageDraw, ImageFont
from team_card_project import constants
from team_card_project import data_io

DATA_DIR = constants.DATA_DIR


def get_mode_colors(mode: str = 'light') -> dict:
    """
    Return the colors of a card style: the card background, the section background, the text, the grey of the stat bars, and the faint lines.

    :param mode: A str determining the style of card ('light' or 'dark')
    :return: A dict of RGB colors for 'background', 'section', 'text', 'unqualified_bar', and 'graph_grid'
    """
    if mode == 'light':
        colors = {
            'background': constants.WHITE, 'section': constants.SECTION_LIGHT, 'text': constants.BLACK, 'unqualified_bar': (190, 190, 190),
            'graph_grid': (190, 190, 196),
        }
    else:
        colors = {
            'background': constants.DARK, 'section': constants.SECTION_DARK, 'text': constants.WHITE, 'unqualified_bar': (95, 95, 95),
            'graph_grid': (110, 110, 116),
        }

    return colors


def load_team_logo(team: str, mode: str, width: int) -> Image.Image:
    """
    Load a team's logo resized to a width (keeping its proportions).

    :param team: A str of the team abbreviation ('ABC')
    :param mode: A str determining the style of the logo ('light' or 'dark')
    :param width: An int of the logo's width in pixels
    :return: An RGBA image of the team logo
    """
    with open(os.path.join(constants.ASSETS_DIR, 'team_logos', f'{team}_{mode}.svg'), 'rb') as f:
        svg_bytes = f.read()
    team_logo = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg_bytes))).convert('RGBA')

    logo_height = int(team_logo.height * width / team_logo.width)
    team_logo = team_logo.resize((width, logo_height), Image.Resampling.LANCZOS)

    return team_logo


def get_centered_text_top(font: ImageFont.ImageFont, lines_num: int, line_height: int, section_height: int) -> int:
    """
    Return the y position to draw the first line of a block of text so the block is centered vertically in a section, measured from the top of the
    first line's capital letters to the baseline of the last line.

    :param font: An ImageFont of the text's font
    :param lines_num: An int of how many lines the block has
    :param line_height: An int of the distance between the lines in pixels
    :param section_height: An int of the section's height in pixels
    :return: An int of the y position to draw the first line at
    """
    cap_top, baseline = font.getbbox('H')[1], font.getbbox('H')[3]
    block_height = (lines_num - 1) * line_height + baseline - cap_top
    result = round((section_height - block_height) / 2 - cap_top)
    return result


def get_stat_component_sizes(size: str) -> dict:
    """
    Return the fonts and sizes of a stat component's text and bar for a size of component.

    :param size: A str of the size of the component ('small' or 'large')
    :return: A dict with the names of the 'name_font', 'value_font' and 'percentile_font' (keys of the font cache), the 'bar_height' and 'edge_pad' (the space between the
        bar and the sides of the component), the 'bar_gap' (the space between the bottom of the stat's name and the top of its bar) and the 'percentile_stroke' (the extra stroke
        thickness of the percentile number on the bar), all in pixels
    """
    sizes = {
        'small': {'name_font': 'stat', 'value_font': 'stat', 'percentile_font': 'basic_42', 'bar_height': 46, 'edge_pad': 32, 'bar_gap': 16, 'percentile_stroke': 0.5},
        'large': {'name_font': 'stat', 'value_font': 'stat', 'percentile_font': 'basic_58', 'bar_height': 69, 'edge_pad': 39, 'bar_gap': 16, 'percentile_stroke': 0.5},
    }
    return sizes[size]


def get_team_single_season(team: str, season: str) -> pd.Series:
    """
    Return a Series of a team's card data for a single season.

    :param team: A str of the full name of the team ('Location Name')
    :param season: A str representing the season ('YYYY-YYYY')
    :return: A Series containing the team's stats for the given season
    """

    # Load the season's card data
    season_data = data_io.load_card_data_csv(season)

    # Get team row
    team_season = season_data.loc[season_data['Team'] == team].copy()
    if team_season.empty:
        raise ValueError(f"{team} not found in {season} card data.")
    team_season = team_season.iloc[0]

    return team_season


def draw_centered_text(
        draw: ImageDraw.ImageDraw,
        text: str,
        font: ImageFont.ImageFont,
        y_position: int,
        x_center: int = 1000,
        fill: tuple[int, int, int] = (0, 0, 0),
        stroke_width: int = 0,
        stroke_fill: tuple[int, int, int] = None,
    ) -> None:
    """
    Draws text that is centered on a PIL drawing.

    :param draw: A PIL drawing that will have the text centered on it
    :param text: A str of the text to be centered
    :param font: An ImageFont of the text's font
    :param y_position: An int of where the y position will be
    :param x_center: An int of where the center x position is (default is at 1000)
    :param fill: A tuple of rgb values for the color of the text (default is (0,0,0)/black)
    :param stroke_width: An int outline thickness in pixels around the text (default is 0/no outline)
    :param stroke_fill: A tuple of rgb values for the outline color (default is None)
    :return: None
    """

    text_bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
    text_width = text_bbox[2] - text_bbox[0]
    x_position = x_center - (text_width // 2)
    draw.text((x_position, y_position), text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)


def draw_righted_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    y_position: int,
    x_right: int,
    fill: tuple[int, int, int] = (0, 0, 0)
    ) -> None:
    """
    Draws text that right-aligned on a PIL drawing.

    :param draw: A PIL drawing that will have the text right-aligned on it
    :param text: A str of the text to be right-aligned
    :param font: An ImageFont of the text's font
    :param y_position: An int of where the y position will be
    :param x_right: An int of where the right most x position is
    :param fill: A tuple of rgb values for the color of the text (default is (0,0,0)/black)
    :return: None
    """

    text_width = draw.textbbox((0, 0), str(text), font=font)[2]
    x_position = x_right - text_width
    draw.text((x_position, y_position), str(text), font=font, fill=fill)


def get_ordinal(number: int) -> str:
    """
    Return a number with its ordinal suffix (Ex: 1 -> 1st, 22 -> 22nd, 113 -> 113th).

    :param number: An int to add the suffix to
    :return: A str of the number with its suffix
    """
    if 10 <= number % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(number % 10, 'th')

    result = f'{number}{suffix}'
    return result


def get_gradient_colors(fractions: np.ndarray, solid_fraction: float) -> np.ndarray:
    """
    Return the colors of the stat bar gradient (red to purple to blue) at places along the bar. The red and blue ends hold their full color for a
    stretch before blending toward purple.

    :param fractions: An array of places along the bar, from 0 (the left end) to 1 (the right end)
    :param solid_fraction: A float of the share of the bar at each end that stays solid red or blue
    :return: An array of RGB colors, one per place
    """
    red, purple, blue = constants.STAT_GRADIENT_COLORS
    solid = solid_fraction
    colors = np.array([red, red, purple, blue, blue], dtype=float)
    positions = np.array([0, solid, 0.5, 1 - solid, 1])
    result = np.stack([np.interp(fractions, positions, colors[:, channel]) for channel in range(3)], axis=-1)
    return result


def make_percentile_bar(
        width: int, height: int, fraction: float, track_color: tuple, label: str = None, label_font: ImageFont.ImageFont = None, label_stroke: int = 0,
        *, solid_fraction: float, min_fill: float, end_hold: float, label_gap: float,
) -> Image.Image:
    """
    Make a pill shaped percentile bar: a grey track filled from the left with the red to purple to blue gradient up to the percentile, with the percentile
    written in white at the end of the fill. The smallest fill (0) is a small rounded lens, and the end of the fill holds its percentile's color for a stretch.
    A bar with no percentile is all grey with N/A in the middle.

    :param width: An int of the bar's width in pixels
    :param height: An int of the bar's height in pixels
    :param fraction: A float of the percentile from 0 to 1 (None for no percentile)
    :param track_color: An RGB tuple of the color of the unfilled part of the bar
    :param label: A str of the percentile to write at the end of the fill
    :param label_font: The font of the label
    :param label_stroke: An int of the extra stroke thickness of the label in pixels
    :param solid_fraction: A float of the share of the bar at each end of the gradient that stays solid red or blue
    :param min_fill: A float of the smallest fill of the bar (0 percentile) as a share of the bar's height
    :param end_hold: A float of how far the end of the fill holds its percentile's color, as a share of the bar's height
    :param label_gap: A float of the space between the percentile number and the end of the fill, as a share of the bar's height
    :return: An RGBA image of the percentile bar
    """
    track = Image.new('L', (width, height), 0)
    ImageDraw.Draw(track).rounded_rectangle([(0, 0), (width - 1, height - 1)], radius=height // 2, fill=255)
    bar = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    bar.paste(Image.new('RGBA', (width, height), track_color + (255,)), (0, 0), track)

    if fraction is None:
        label_xy, label_anchor, label = (width / 2, height / 2), 'mm', 'N/A'
    else:
        # The fill is a pill. One narrower than the bar is tall is a lens: the bar's rounded left end overlapped with a mirrored rounded right end
        min_fill_width = round(min_fill * height)
        fill_width = round(min_fill_width + fraction * (width - min_fill_width))
        if fill_width >= height:
            mask = Image.new('L', (fill_width, height), 0)
            ImageDraw.Draw(mask).rounded_rectangle([(0, 0), (fill_width - 1, height - 1)], radius=height // 2, fill=255)
        else:
            left_end = Image.new('L', (height, height), 0)
            ImageDraw.Draw(left_end).ellipse([(0, 0), (height - 1, height - 1)], fill=255)
            right_end = Image.new('L', (height, height), 0)
            ImageDraw.Draw(right_end).ellipse([(fill_width - height, 0), (fill_width - 1, height - 1)], fill=255)
            mask = ImageChops.multiply(left_end, right_end).crop((0, 0, fill_width, height))

        # The gradient is stretched so it reaches the percentile's color a stretch before the end of the fill, which holds that color
        hold = min(end_hold * height, 0.35 * fill_width)
        fractions = np.minimum(np.arange(fill_width) / max(fill_width - hold, 1), 1) * fraction
        fill = np.repeat(get_gradient_colors(fractions, solid_fraction).astype(np.uint8)[np.newaxis, :, :], height, axis=0)
        bar.paste(Image.fromarray(fill, 'RGB').convert('RGBA'), (0, 0), mask)
        label_xy, label_anchor = (fill_width - label_gap * height, height / 2), 'rm'

    if label:
        ImageDraw.Draw(bar).text(
            label_xy, label, font=label_font, fill=constants.WHITE + (255,), anchor=label_anchor, stroke_width=label_stroke, stroke_fill=constants.WHITE + (255,),
        )

    return bar


def paste_rounded(
        card: Image.Image,
        section: Image.Image,
        position: tuple[int, int],
        radius: int,
        corners: tuple[bool, bool, bool, bool] = (True, True, True, True),
    ) -> None:
    """
    Paste a section onto the card with rounded corners (any corner can be left square).

    :param card: The card image the section is pasted onto
    :param section: The section image to paste
    :param position: A tuple of the (x, y) position of the section's top left corner
    :param radius: An int of the corner radius in pixels
    :param corners: A tuple of whether the top left, top right, bottom right, and bottom left corners are rounded (default is all of them)
    :return: None
    """
    scale = 4
    mask = Image.new('L', (section.width * scale, section.height * scale), 0)
    ImageDraw.Draw(mask).rounded_rectangle([(0, 0), (mask.width - 1, mask.height - 1)], radius=radius * scale, fill=255, corners=corners)
    mask = mask.resize(section.size, Image.Resampling.BOX)

    card.paste(section, position, mask)


def draw_line_chart(
        card_image: Image.Image,
        x: int,
        y: int,
        width: int,
        height: int,
        x_values: list,
        y_values: list,
        x_range: tuple[float, float],
        y_range: tuple[float, float],
        y_ticks: list,
        line_color: tuple[int, int, int],
        grid_color: tuple[int, int, int],
        line_width: int,
        dot_radius: int = 0,
        last_dot_radius: int = 0,
        invert_y: bool = False,
    ) -> tuple[callable, callable]:
    """
    Draw a line chart with a faint line at each y tick. A y value of None leaves a gap in the line.

    :param card_image: The image the chart is drawn onto
    :param x: An int of the chart's left edge
    :param y: An int of the chart's top edge
    :param width: An int of the chart's width in pixels
    :param height: An int of the chart's height in pixels
    :param x_values: A list of the x value of each point
    :param y_values: A list of the y value of each point (None for no point)
    :param x_range: A tuple of the x values at the left and right edges of the chart
    :param y_range: A tuple of the y values at the bottom and top edges of the chart
    :param y_ticks: A list of the y values to draw a faint line at
    :param line_color: A tuple of rgb values for the line and dots
    :param grid_color: A tuple of rgb values for the faint lines
    :param line_width: An int of the line's width in pixels
    :param dot_radius: An int of the radius of the dot at every point (default is no dots)
    :param last_dot_radius: An int of the radius of the dot at the last point (default is none)
    :param invert_y: Whether the lowest y value is at the top of the chart (Ex: for ranks)
    :return: A tuple of functions that give the x and y position on the card image for an x and a y value
    """
    scale = 4
    layer = Image.new('RGBA', (width * scale, height * scale), (0, 0, 0, 0))
    layer_draw = ImageDraw.Draw(layer)

    y_low, y_high = y_range
    x_low, x_high = x_range
    to_x = lambda value: (value - x_low) / (x_high - x_low) * width
    if invert_y:
        to_y = lambda value: (value - y_low) / (y_high - y_low) * height
    else:
        to_y = lambda value: height - (value - y_low) / (y_high - y_low) * height

    for tick in y_ticks:
        layer_draw.line([(0, to_y(tick) * scale), (width * scale, to_y(tick) * scale)], fill=grid_color + (255,), width=int(2 * scale))

    points = [(to_x(x_value), to_y(y_value)) if y_value is not None and not pd.isna(y_value) else None for x_value, y_value in zip(x_values, y_values)]
    for point, next_point in zip(points, points[1:]):
        if point is not None and next_point is not None:
            layer_draw.line([(point[0] * scale, point[1] * scale), (next_point[0] * scale, next_point[1] * scale)], fill=line_color + (255,), width=int(line_width * scale))
    # Round the ends of the line with dots the width of the line
    for point in points:
        if point is not None:
            radius = dot_radius if dot_radius else line_width / 2
            layer_draw.ellipse([(point[0] - radius) * scale, (point[1] - radius) * scale, (point[0] + radius) * scale, (point[1] + radius) * scale], fill=line_color + (255,))
    last_point = next((point for point in reversed(points) if point is not None), None)
    if last_dot_radius and last_point is not None:
        layer_draw.ellipse(
            [(last_point[0] - last_dot_radius) * scale, (last_point[1] - last_dot_radius) * scale,
             (last_point[0] + last_dot_radius) * scale, (last_point[1] + last_dot_radius) * scale], fill=line_color + (255,),
        )

    layer = layer.resize((width, height), Image.Resampling.BOX)
    card_image.paste(layer, (x, y), layer)

    card_x = lambda value: x + to_x(value)
    card_y = lambda value: y + to_y(value)
    return card_x, card_y
