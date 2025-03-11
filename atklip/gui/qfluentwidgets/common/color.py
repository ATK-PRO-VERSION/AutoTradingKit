# coding: utf-8
import colorsys
from enum import Enum
from functools import lru_cache
from typing import Union

from PySide6.QtGui import QColor


class FluentThemeColor(Enum):
    """ Fluent theme color

    Refer to: https://www.figma.com/file/iM7EPX8Jn37zjeSezb43cF
    """
    YELLOW_GOLD = "#FFB900"
    GOLD = "#FF8C00"
    ORANGE_BRIGHT = "#F7630C"
    ORANGE_DARK = "#CA5010"
    RUST = "#DA3B01"
    PALE_RUST = "#EF6950"
    BRICK_RED = "#D13438"
    MOD_RED = "#FF4343"
    PALE_RED = "#E74856"
    RED = "#E81123"
    ROSE_BRIGHT = "#EA005E"
    ROSE = "#C30052"
    PLUM_LIGHT = "#E3008C"
    PLUM = "#BF0077"
    ORCHID_LIGHT = "#BF0077"
    ORCHID = "#9A0089"
    DEFAULT_BLUE = "#0078D7"
    NAVY_BLUE = "#0063B1"
    PURPLE_SHADOW = "#8E8CD8"
    PURPLE_SHADOW_DARK = "#6B69D6"
    IRIS_PASTEL = "#8764B8"
    IRIS_SPRING = "#744DA9"
    VIOLET_RED_LIGHT = "#B146C2"
    VIOLET_RED = "#881798"
    COOL_BLUE_BRIGHT = "#0099BC"
    COOL_BLUR = "#2D7D9A"
    SEAFOAM = "#00B7C3"
    SEAFOAM_TEAL = "#038387"
    MINT_LIGHT = "#00B294"
    MINT_DARK = "#018574"
    TURF_GREEN = "#00CC6A"
    SPORT_GREEN = "#10893E"
    GRAY = "#7A7574"
    GRAY_BROWN = "#5D5A58"
    STEAL_BLUE = "#68768A"
    METAL_BLUE = "#515C6B"
    PALE_MOSS = "#567C73"
    MOSS = "#486860"
    MEADOW_GREEN = "#498205"
    GREEN = "#107C10"
    OVERCAST = "#767676"
    STORM = "#4C4A48"
    BLUE_GRAY = "#69797E"
    GRAY_DARK = "#4A5459"
    LIDDY_GREEN = "#647C64"
    SAGE = "#525E54"
    CAMOUFLAGE_DESERT = "#847545"
    CAMOUFLAGE = "#7E735F"

    def color(self):
        return QColor(self.value)


# Color Utility
@lru_cache(maxsize=128) 
def hsv2rgb(h_or_color: Union[tuple, int], s: int = 0, v: int = 0, a: int = None) -> tuple:
    """Convert hsv color to rgb color.

    :param h_or_color: The 'hue' value or a color tuple.
    :param s: The 'saturation' value.
    :param v: The 'value' value.
    :param a: The 'alpha' value.
    :return: The converted rgb tuple color.
    """

    if type(h_or_color).__name__ == "tuple":
        if len(h_or_color) == 4:
            h, s, v, a = h_or_color
        else:
            h, s, v = h_or_color
    else: h = h_or_color
    r, g, b = colorsys.hsv_to_rgb(h / 100.0, s / 100.0, v / 100.0)
    if a is not None: return r * 255, g * 255, b * 255, a
    return r * 255, g * 255, b * 255

@lru_cache(maxsize=128) 
def rgb2hsv(r_or_color: Union[tuple, int], g: int = 0, b: int = 0, a: int = None) -> tuple:
    """Convert rgb color to hsv color.

    :param r_or_color: The 'red' value or a color tuple.
    :param g: The 'green' value.
    :param b: The 'blue' value.
    :param a: The 'alpha' value.
    :return: The converted hsv tuple color.
    """

    if type(r_or_color).__name__ == "tuple":
        if len(r_or_color) == 4:
            r, g, b, a = r_or_color
        else:
            r, g, b = r_or_color
    else: r = r_or_color
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    if a is not None: return h * 100, s * 100, v * 100, a
    return h * 100, s * 100, v * 100

@lru_cache(maxsize=128) 
def hex2rgb(hex: str) -> tuple:
    """Convert hex color to rgb color.

    :param hex: The hexadecimal string ("xxxxxx").
    :return: The converted rgb tuple color.
    """

    if len(hex) < 6: hex += "0"*(6-len(hex))
    elif len(hex) > 6: hex = hex[0:6]
    rgb = tuple(int(hex[i:i+2], 16) for i in (0,2,4))
    return rgb

@lru_cache(maxsize=128) 
def rgb2hex(r_or_color: Union[tuple, int], g: int = 0, b: int = 0, a: int = 0) -> str:
    """Convert rgb color to hex color.

    :param r_or_color: The 'red' value or a color tuple.
    :param g: The 'green' value.
    :param b: The 'blue' value.
    :param a: The 'alpha' value.
    :return: The converted hexadecimal color.
    """

    if type(r_or_color).__name__ == "tuple": r, g, b = r_or_color[:3]
    else: r = r_or_color
    hex = '%02x%02x%02x' % (int(r), int(g), int(b))
    return hex

@lru_cache(maxsize=128) 
def hex2hsv(hex: str) -> tuple:
    """Convert hex color to hsv color.

    :param hex: The hexadecimal string ("xxxxxx").
    :return: The converted hsv tuple color.
    """

    return rgb2hsv(hex2rgb(hex))

@lru_cache(maxsize=128) 
def hsv2hex(h_or_color: Union[tuple, int], s: int = 0, v: int = 0, a: int = 0) -> str:
    """Convert hsv color to hex color.

    :param h_or_color: The 'hue' value or a color tuple.
    :param s: The 'saturation' value.
    :param v: The 'value' value.
    :param a: The 'alpha' value.
    :return: The converted hexadecimal color.
    """

    if type(h_or_color).__name__ == "tuple": h, s, v = h_or_color[:3]
    else: h = h_or_color
    return rgb2hex(hsv2rgb(h, s, v))


