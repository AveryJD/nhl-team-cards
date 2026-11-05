# ====================================================================================================
# CARD CREATION HELPER FUNCTIONS
# ====================================================================================================

# Imports
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from team_card_project import constants

DATA_DIR = constants.DATA_DIR


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


def get_gradient_colors(fractions: np.ndarray) -> np.ndarray:
    """
    Return the colors of the stat bar gradient (red to purple to blue) at places along the bar. The red and blue ends hold their full color for a
    stretch before blending toward purple.

    :param fractions: An array of places along the bar, from 0 (the left end) to 1 (the right end)
    :return: An array of RGB colors, one per place
    """
    red, purple, blue = constants.STAT_GRADIENT_COLORS
    solid = constants.STAT_GRADIENT_SOLID_FRACTION
    colors = np.array([red, red, purple, blue, blue], dtype=float)
    positions = np.array([0, solid, 0.5, 1 - solid, 1])
    result = np.stack([np.interp(fractions, positions, colors[:, channel]) for channel in range(3)], axis=-1)
    return result


def make_gradient_bar(width: int, height: int) -> Image.Image:
    """
    Make a pill shaped bar that goes from red to purple to blue (the colours used on the website).

    :param width: An int of the bar's width in pixels
    :param height: An int of the bar's height in pixels
    :return: An RGBA image of the gradient bar
    """
    gradient = get_gradient_colors(np.linspace(0, 1, width)).astype(np.uint8)
    gradient = np.repeat(gradient[np.newaxis, :, :], height, axis=0)
    bar = Image.fromarray(gradient, 'RGB').convert('RGBA')

    mask = Image.new('L', (width, height), 0)
    ImageDraw.Draw(mask).rounded_rectangle([(0, 0), (width - 1, height - 1)], radius=height // 2, fill=255)
    bar.putalpha(mask)

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
