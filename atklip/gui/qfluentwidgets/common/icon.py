# coding:utf-8
from enum import Enum
from typing import Union
import os,re
from PySide6.QtXml import QDomDocument
from PySide6.QtCore import QRectF, Qt, QFile, QObject, QRect
from PySide6.QtGui import QIcon, QIconEngine, QColor, QPixmap, QImage, QPainter, QAction
from PySide6.QtSvg import QSvgRenderer
from functools import lru_cache
from .config import isDarkTheme, Theme
from .overload import singledispatchmethod
from typing import Optional, Dict
import xml.etree.ElementTree as ET

@lru_cache(maxsize=128) 
def get_real_path(path_icon = "atklip/gui/qfluentwidgets/_rc/images/crypto"):
    path_icon_build = f"_internal/{path_icon}"
    if os.path.exists(path_icon):
        return path_icon
    else:
        return path_icon_build

@lru_cache(maxsize=128) 
def check_icon_exist(_icon:str):
    icon_path = f"{get_real_path()}/{_icon.lower()}.svg"
    if os.path.exists(icon_path):
        return True
    else:
        return False


"https://s3-symbol-logo.tradingview.com/provider/binance.svg"
"https://s3-symbol-logo.tradingview.com/crypto/XTVCETH.svg"
@lru_cache(maxsize=128) 
def change_svg_color(value:str, new_color):
    _ion_path = "atklip/gui/qfluentwidgets/_rc/images/icons"
    path = f'{get_real_path(_ion_path)}/{value.lower()}_white.svg'
    new_path = f'{get_real_path(_ion_path)}/{value.lower()}_tradingview.svg'
    if os.path.exists(new_path):
        return new_path
    file = open(path,"r")
    text = file.read()
    file.close()
    file = open(new_path,'w')
    new_text = text.replace("rgb(255,255,255)",new_color).replace("rgb(0,0,0)",new_color).replace("white",new_color).replace("rgb(247,245,245)",new_color) 
    file.write(new_text)
    file.close()
    return new_path

@lru_cache(maxsize=128) 
def change_svg(value:str):
    path = f'atklip/gui/qfluentwidgets/_rc/images/icons/{value}'
    new_path = f'atklip/gui/qfluentwidgets/_rc/images/icons/{value.lower()}'
    # if os.path.exists(new_path):
    #     return new_path
    file = open(path,"r",encoding="utf-8")
    text = file.read()
    file.close()
    os.remove(path)
    file = open(new_path,'w',encoding="utf-8")
    #new_text = text.replace("rgb(255,255,255)",new_color).replace("rgb(0,0,0)",new_color).replace("white",new_color).replace("rgb(247,245,245)",new_color) 
    file.write(text)
    file.close()
    
    return new_path

@lru_cache(maxsize=128) 
def svg_to_pixmap(self, svg_filename: str, width: int, height: int, color: QColor) -> QPixmap:
    renderer = QSvgRenderer(svg_filename)
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)  # this is the destination, and only its alpha is used!
    painter.setCompositionMode(
        painter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), color)
    painter.end()
    return pixmap

@lru_cache(maxsize=128) 
def getIconColor(theme=Theme.AUTO, reverse=False):
    """ get the color of icon based on theme """
    if not reverse:
        lc, dc = "black", "white"
    else:
        lc, dc = "white", "black"

    if theme == Theme.AUTO:
        color = dc if isDarkTheme() else lc
    else:
        color = dc if theme == Theme.DARK else lc

    return color

def drawSvgIcon(icon, painter, rect):
    """ draw svg icon

    Parameters
    ----------
    icon: str | bytes | QByteArray
        the path or code of svg icon

    painter: QPainter
        painter

    rect: QRect | QRectF
        the rect to render icon
    """
    renderer = QSvgRenderer(icon)
    renderer.render(painter, QRectF(rect))

def paireSVG(
    svg_content: str,
    target_id: Optional[str] = "path1",
    attributes: Optional[Dict[str, str]] = None,
    verbose: bool = True
) -> str:
    """
    Chỉnh sửa thuộc tính của phần tử SVG theo ID và trả về SVG đã sửa đổi.

    Parameters
    ----------
    svg_content : str
        Nội dung SVG đầu vào dạng chuỗi
    target_id : str, optional
        ID của phần tử path cần chỉnh sửa (mặc định: "path1")
    attributes : dict, optional
        Dictionary chứa các thuộc tính cần thay đổi (ví dụ: {'fill': '#FF0000'})
    verbose : bool, optional
        Hiển thị thông tin debug (mặc định: False)

    Returns
    -------
    str
        Nội dung SVG đã chỉnh sửa dạng chuỗi UTF-8
    """
    # Khởi tạo giá trị mặc định cho attributes
    if attributes is None:
        attributes = {'fill': '#FF0000'}  # Giá trị mặc định nếu không cung cấp

    try:
        # Parse SVG và xử lý namespace
        namespaces = {'svg': 'http://www.w3.org/2000/svg'}
        root = ET.fromstring(svg_content)
        
        # Tìm phần tử target theo ID
        xpath_query = f'.//svg:path[@id="{target_id}"]'
        target_element = root.find(xpath_query, namespaces)

        if target_element is not None:
            # Cập nhật attributes
            for attr, value in attributes.items():
                target_element.set(attr, value)
                if verbose:
                    print(f"Đã cập nhật {attr} thành {value} cho {target_id}")
        else:
            if verbose:
                print(f"Không tìm thấy phần tử với ID '{target_id}'")

        # Xuất kết quả với định dạng đúng
        return ET.tostring(root, encoding='utf-8', method='xml').decode()

    except ET.ParseError as e:
        print(f"Lỗi parse SVG: {str(e)}")
        return svg_content  # Trả về nguyên bản nếu có lỗi
    except Exception as e:
        print(f"Lỗi không xác định: {str(e)}")
        return svg_content

@lru_cache(maxsize=128) 
def writeSvg(iconPath: str, indexes=None, **attributes):
    """ write svg with specified attributes

    Parameters
    ----------
    iconPath: str
        svg icon path

    indexes: List[int]
        the path to be filled

    **attributes:
        the attributes of path

    Returns
    -------
    svg: str
        svg code
    """
    if not iconPath.lower().endswith('.svg'):
        return ""
    f = QFile(iconPath)
    f.open(QFile.ReadOnly)
    return paireSVG(svg_content=f.readAll().toStdString(),attributes=attributes)
    

def drawIcon(icon, painter, rect, state=QIcon.Off, **attributes):
    """ draw icon

    Parameters
    ----------
    icon: str | QIcon | FluentIconBaseBase
        the icon to be drawn

    painter: QPainter
        painter

    rect: QRect | QRectF
        the rect to render icon

    **attribute:
        the attribute of svg icon
    """
    if isinstance(icon, FluentIconBase):
        icon.render(painter, rect, **attributes)
    elif isinstance(icon, Icon):
        icon.fluentIcon.render(painter, rect, **attributes)
    else:
        icon = QIcon(icon)
        icon.paint(painter, QRectF(rect).toRect(), Qt.AlignCenter, state=state)

@lru_cache(maxsize=128) 
def get_exchange_icon(exchange):
        if exchange == "coinbaseexchange":
            return EchangeIcon.COINBASE_PRO.path(), "Coinbase Exchange", "SPOT & FUTURES"
        if exchange == "coinbase":
            return EchangeIcon.COINBASE_PRO.path(), "Coinbase Advanced", "SPOT & FUTURES"
        elif exchange == "okx":
            return EchangeIcon.OKEX.path(), "OKX", "SPOT & FUTURES"
        elif exchange == "huobi":
            return EchangeIcon.HUOBI.path(), "HuoBi", "SPOT & FUTURES"
        # elif exchange == "hitbtc":
        #     return  EI.HITBTC.path(), "HitBtc", "SPOT & FUTURES"
        elif exchange == "gate":
            return  EchangeIcon.GATE.path(), "Gate", "SPOT & FUTURES"
        elif exchange == "deribit":
            return  EchangeIcon.DERIBIT.path(), "Deribit", "SPOT & FUTURES"
        elif exchange == "coinex":
            return  EchangeIcon.COINEX.path(), "CoinEx", "SPOT & FUTURES"
        elif exchange == "kraken":
            return  EchangeIcon.KRAKEN_SPOT.path(), "Kraken", "SPOT"
        elif exchange == "krakenfutures":
            return  EchangeIcon.KRAKEN_FUTURES.path(), "Kraken", "FUTURES"
        elif exchange == "kucoin":
            return  EchangeIcon.KUCOIN.path(), "Kucoin", "SPOT"
        elif exchange == "kucoinfutures":
            return  EchangeIcon.KUCOIN_FUTURES.path(), "Kucoin", "FUTURES"
        elif exchange == "mexc":
            return  EchangeIcon.MEXC.path(), "MEXC", "SPOT & FUTURES"
        elif exchange == "binance":
            return  EchangeIcon.BINANCE_ICON.path(), "Binance", "SPOT"
        elif exchange == "binanceusdm":
            return  EchangeIcon.BINANCE_ICON.path(), "Binance Perpetual", "FUTURES"
        elif exchange == "binancecoinm":
            return  EchangeIcon.BINANCE_ICON.path(), "Binance Coin", "FUTURES"
        elif exchange == "bybit":
            return  EchangeIcon.BYBIT.path(), "ByBit", "SPOT & FUTURES"
        # elif exchange == "bitvavo":
        #     return  EI.BITVAVO.path(), "Bitvavo", "SPOT & FUTURES"
        elif exchange == "bittrex":
            return  EchangeIcon.BITTREX.path(), "Bittrex", "SPOT & FUTURES"
        elif exchange == "bitmex":
            return  EchangeIcon.BITMEX.path(), "BitMex", "SPOT & FUTURES"
        elif exchange == "bitmart":
            return  EchangeIcon.BITMART.path(), "BitMart", "SPOT & FUTURES"
        elif exchange == "bitget":
            return  EchangeIcon.BITGET.path(), "BitGet", "SPOT & FUTURES"
        elif exchange == "bitfinex2":
            return  EchangeIcon.BITFINEX2.path(), "BitFinex", "SPOT & FUTURES"
        elif exchange == "bingx":
            return  EchangeIcon.BINGX.path(), "BingX", "SPOT & FUTURES"
        return EchangeIcon.BINANCE_ICON.path(), "Binance Perpetual", "FUTURES"

@lru_cache(maxsize=128) 
def get_symbol_icon(symbol:str):
        _symbol = symbol.lower()
        re_symbol = re.findall(r'(.*?)/', _symbol)
        return re_symbol[0]

class FluentIconEngine(QIconEngine):
    """ Fluent icon engine """

    def __init__(self, icon, reverse=False):
        """
        Parameters
        ----------
        icon: QICon | Icon | FluentIconBase
            the icon to be drawn

        reverse: bool
            whether to reverse the theme of icon
        """
        super().__init__()
        self.icon = icon
        self.isThemeReversed = reverse
    def paint(self, painter, rect, mode, state):
        painter.save()

        if mode == QIcon.Disabled:
            painter.setOpacity(0.5)
        elif mode == QIcon.Selected:
            painter.setOpacity(0.7)

        # change icon color according to the theme
        icon = self.icon

        if not self.isThemeReversed:
            theme = Theme.AUTO
        else:
            theme = Theme.LIGHT if isDarkTheme() else Theme.DARK

        if isinstance(self.icon, Icon):
            icon = self.icon.fluentIcon.icon(theme)
        elif isinstance(self.icon, FluentIconBase):
            icon = self.icon.icon(theme)

        if rect.x() == 19:
            rect = rect.adjusted(-1, 0, 0, 0)

        icon.paint(painter, rect, Qt.AlignCenter, QIcon.Normal, state)
        painter.restore()


class SvgIconEngine(QIconEngine):
    """ Svg icon engine """

    def __init__(self, svg: str):
        super().__init__()
        self.svg = svg

    def paint(self, painter, rect, mode, state):
        drawSvgIcon(self.svg.encode(), painter, rect)

    def clone(self) -> QIconEngine:
        return SvgIconEngine(self.svg)

    def pixmap(self, size, mode, state):
        image = QImage(size, QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        pixmap = QPixmap.fromImage(image, Qt.NoFormatConversion)

        painter = QPainter(pixmap)
        rect = QRect(0, 0, size.width(), size.height())
        self.paint(painter, rect, mode, state)
        return pixmap


class FluentIconBase:
    """ Fluent icon base class """

    def path(self, theme=Theme.AUTO) -> str:
        """ get the path of icon

        Parameters
        ----------
        theme: Theme
            the theme of icon
            * `Theme.Light`: black icon
            * `Theme.DARK`: white icon
            * `Theme.AUTO`: icon color depends on `config.theme`
        """
        raise NotImplementedError

    def icon(self, theme=Theme.AUTO, color: QColor = None) -> QIcon:
        """ create a fluent icon

        Parameters
        ----------
        theme: Theme
            the theme of icon
            * `Theme.Light`: black icon
            * `Theme.DARK`: white icon
            * `Theme.AUTO`: icon color depends on `qconfig.theme`

        color: QColor | Qt.GlobalColor | str
            icon color, only applicable to svg icon
        """
        path = self.path(theme)

        if not (path.endswith('.svg') and color):
            return QIcon(self.path(theme))

        color = QColor(color).name()
        return QIcon(SvgIconEngine(writeSvg(path, fill=color)))
    
    def colored(self, lightColor: QColor, darkColor: QColor) -> "ColoredFluentIcon":
        """ create a colored fluent icon
        Parameters
        ----------
        lightColor: str | QColor | Qt.GlobalColor
            icon color in light mode
        darkColor: str | QColor | Qt.GlobalColor
            icon color in dark mode
        """
        return ColoredFluentIcon(self, lightColor, darkColor)
    def qicon(self, reverse=False) -> QIcon:
        """ convert to QIcon, the theme of icon will be updated synchronously with app

        Parameters
        ----------
        reverse: bool
            whether to reverse the theme of icon
        """
        return QIcon(FluentIconEngine(self, reverse))

    def render(self, painter, rect, theme=Theme.AUTO, indexes=None, **attributes):
        """ draw svg icon

        Parameters
        ----------
        painter: QPainter
            painter

        rect: QRect | QRectF
            the rect to render icon

        theme: Theme
            the theme of icon
            * `Theme.Light`: black icon
            * `Theme.DARK`: white icon
            * `Theme.AUTO`: icon color depends on `config.theme`

        indexes: List[int]
            the svg path to be modified

        **attributes:
            the attributes of modified path
        """
        icon = self.path(theme)

        if icon.endswith('.svg'):
            if attributes:
                icon = writeSvg(icon, indexes, **attributes).encode()

            drawSvgIcon(icon, painter, rect)
        else:
            icon = QIcon(icon)
            rect = QRectF(rect).toRect()
            painter.drawPixmap(rect, icon.pixmap(QRectF(rect).toRect().size()))

@lru_cache(maxsize=128) 
def toQIcon(icon: Union[QIcon, FluentIconBase, str]) -> QIcon:
    """ convet `icon` to `QIcon` """
    if isinstance(icon, str):
        return QIcon(icon)
    if isinstance(icon, FluentIconBase):
        return icon.icon()
    return icon

class CurrencyIcon(FluentIconBase, Enum):
    """ Currency icon """
    USD = "usd"
    VND = "vnd"
    def path(self, theme=Theme.AUTO):
        return f':/qfluentwidgets/images/crypto/{self.value}.svg'

class CryptoIcon(FluentIconBase, Enum):
    """ Crypto icon """
    BTC = "btc"
    ETH = "eth"

    def path(self, theme=Theme.AUTO):
        return f':/qfluentwidgets/images/crypto/{self.value}.svg'
    @staticmethod
    def crypto_url(symbol):
        return f':/qfluentwidgets/images/crypto/{symbol}.svg'
    @staticmethod
    def render(painter, rect, symbol:str, indexes=None, **attributes):
        if symbol.endswith("svg"):
            icon = symbol
        else:
            icon = CryptoIcon.crypto_url(symbol)
        if icon.endswith('.svg'):
            if attributes:
                icon = writeSvg(icon, indexes, **attributes).encode()
            drawSvgIcon(icon, painter, rect)
        else:
            icon = QIcon(icon)
            rect = QRectF(rect).toRect()
            painter.drawPixmap(rect, icon.pixmap(QRectF(rect).toRect().size()))
    

class EchangeIcon(FluentIconBase, Enum):
    """ Echange icon """
    FAVORITE = "favorite"
    COINBASE_PRO = 'coinbase'
    OKEX = "okex"  #có futures
    HUOBI = "huobi"
    HITBTC = "hitbtc"
    # GATE = "gate"
    DERIBIT = "deribit"
    COINEX = "coinex"   #có futures
    KRAKEN_SPOT = "kraken"  # Kraken Spot
    KRAKEN_FUTURES = "kraken"  #có futures
    KUCOIN = 'kucoin'
    KUCOIN_FUTURES = 'kucoin'   #có futures
    MEXC = "mexc"
    BINANCE_ICON = 'binance'
    BINANCE_TEXT = 'binance'
    # BYBIT_USDT_PERPETUAL = ''
    BYBIT = 'bybit'  #có futures
    BITVAVO = "bitvavo"
    BITTREX = "bittrex"
    BITMEX = 'bitmex'
    BITMART = "bitmart"
    BITGET = "bitget"  #có futures
    BITFINEX2 = "bitfinex"
    BINGX = "bingx"
    # WOO = "woo"

    def path(self, theme=Theme.AUTO):
        return f':/qfluentwidgets/images/exchange/{self.value}.svg'
    @staticmethod
    def exchange_url(exchange):
        return f':/qfluentwidgets/images/exchange/{exchange}.svg'

    @staticmethod
    def render(painter, rect, exchange:str, indexes=None, **attributes):
        if exchange.endswith("svg"):
            icon = exchange
        else:
            icon = EchangeIcon.exchange_url(exchange)
        if icon.endswith('.svg'):
            if attributes:
                icon = writeSvg(icon, indexes, **attributes).encode()
            drawSvgIcon(icon, painter, rect)
        else:
            icon = QIcon(icon)
            rect = QRectF(rect).toRect()
            painter.drawPixmap(rect, icon.pixmap(QRectF(rect).toRect().size()))
    
class ColoredFluentIcon(FluentIconBase):
    """ Colored fluent icon """

    def __init__(self, icon: FluentIconBase, lightColor, darkColor):
        """
        Parameters
        ----------
        icon: FluentIconBase
            the icon to be colored
        lightColor: str | QColor | Qt.GlobalColor
            icon color in light mode
        darkColor: str | QColor | Qt.GlobalColor
            icon color in dark mode
        """
        super().__init__()
        self.fluentIcon = icon
        self.lightColor = QColor(lightColor)
        self.darkColor = QColor(darkColor)

    def path(self, theme=Theme.AUTO) -> str:
        return self.fluentIcon.path(theme)

    def render(self, painter, rect, theme=Theme.AUTO, indexes=None, **attributes):
        icon = self.path(theme)

        if not icon.endswith('.svg'):
            return self.fluentIcon.render(painter, rect, theme, indexes, attributes)

        if theme == Theme.AUTO:
            color = self.darkColor if isDarkTheme() else self.lightColor
        else:
            color = self.darkColor if theme == Theme.DARK else self.lightColor

        attributes.update(fill=color.name())
        icon = writeSvg(icon, indexes, **attributes).encode()
        drawSvgIcon(icon, painter, rect)

class FluentIcon(FluentIconBase, Enum):
    """ Fluent icon """

    UP = "Up"
    ADD = "Add"
    BUS = "Bus"
    CAR = "Car"
    CUT = "Cut"
    IOT = "IOT"
    PIN = "Pin"
    TAG = "Tag"
    VPN = "VPN"
    CAFE = "Cafe"
    CHAT = "Chat"
    COPY = "Copy"
    CODE = "Code"
    DOWN = "Down"
    EDIT = "Edit"
    FLAG = "Flag"
    FONT = "Font"
    GAME = "Game"
    HIDE = "Hide"
    INFO = "Info"
    LEAF = "Leaf"
    LINK = "Link"
    MAIL = "Mail"
    MENU = "Menu"
    MUTE = "Mute"
    MORE = "More"
    MOVE = "Move"
    PLAY = "Play"
    SAVE = "Save"
    SEND = "Send"
    SYNC = "Sync"
    STAR = "star"
    UNIT = "Unit"
    VIEW = "View"
    WIFI = "Wifi"
    ALBUM = "Album"
    BROOM = "Broom"
    CLOSE = "Close"
    CLOUD = "Cloud"
    EMBED = "Embed"
    GLOBE = "Globe"
    HEART = "Heart"
    LABEL = "Label"
    MEDIA = "Media"
    MOVIE = "Movie"
    MUSIC = "Music"
    ROBOT = "Robot"
    PAUSE = "Pause"
    PASTE = "Paste"
    PHOTO = "Photo"
    PHONE = "Phone"
    PRINT = "Print"
    SHARE = "Share"
    TILES = "Tiles"
    TRENDLINE = "trendline"
    RAY = "ray"
    HORIZONTAL_RAY = "horizontal_ray"
    INFOR_LINE = "infor_line"  # for line chart
    EXTENTED_LINE = "extented_line"
    TREND_ANGLE = "trend_angle"  # for area chart
    HORIZONTAL_LINE = "horizontal_line"
    VERTICAL_LINE = "vertical_line"
    CROSS_LINE = "cross_line"
    PARALLEL_CHANEL = "parallel_chanel"
    REGRESSION_TREND = "regression_trend"
    FLAT_TOP_BOTTOM = "flat_top_bottom"
    DISJOINT_CHANEL = "disjoint_chanel"
    PITCHFORK = "pitchfork"
    SCHIFF_PITCHFORK = "schiff_pitchfork"
    MODIFY_SCHIFF_PITCHFORK = "modify_schiff_pitchfork"
    INSIDE_PITCHFORK = "inside_pitchfork"
    LONG_POSITION = "long_position"
    SHORT_POSITION = "short_position"
    POSITION = "position"
    FORECAST = "forecast"
    BAR_PATTERN = "bar_pattern"
    SHOST_FEED = "ghost_feed"
    PROJECT = "project"
    ANCHORED_VWAP = "anchored_vwap"
    FIX_RANGE_VOLUME = "fix_range_volume"
    ANHCHORED_VOLUME = "anchored_volume"
    STRATEGY = "strategy"
    PRICE_RANGE = "price_range"
    DATE_RANGE = "date_range"
    DATE_PRICE_RANGE = "date_price_range"
    FIB_RETRACEMENT = "fib_retracement"
    FIB_TREND_BASE = "fib_trend_base"
    FIB_CHANEL = "fib_chanel"
    FIB_TIMEZONE = "fib_timezone"
    FIB_SPEED_RESISTANCE = "fib_speed_resistance"
    FIB_TRENDBASE_TIME = "fib_trendbase_time"
    FIB_CIRCLE = "fib_circle"
    FIB_SPIRAL = "fib_spiral"
    FIB_RETRACEMENTS_ARCS = "fib_retracements_arcs"
    FIB_WEDGE = "fib_wedge"
    PITCHFAN = "pitchfan"
    GAN_BOX = "gan_box"
    GAN_SQUARE_FIX = "gan_square_fix"
    GAN_SQUARE = "gan_square"
    GAN_FAN = "gan_fan"
    BRUSH = "brush"
    HIGHLIGHTER = "highlighter"
    ARROW_MAKER = "arorw_maker"
    ARROW = "arow"
    ARROW_MAKER_UP = "arow_macker_up"
    ARROW_MAKER_DOWN = "arow_macker_down"
    RECTANGLE = "rectangle"
    ROTATE_RECTANGLE = "rotate_rectangle"
    PATH = "path"
    CIRCLE = "circle"
    ELIPSE = "elipse"
    POLIGON = "poligon"
    TRIANGLE = "triangle"
    ARC = "arc"
    CURVE = "curve"
    DOUBLE_CURVE = "double_curve"
    TEXT = "text"
    IMAGE = "image"
    IDEA = "idea"
    FLAG_MARK = "flag_mark"
    SIGNPOST = "signpost"
    PRICE_NOTE = "price_note"
    PRICE_LABEL = "price_label"
    COMMENT = "comment"
    CALLOUT = "callout"
    NOTE_ANCHORED = "note_anchored"
    NOTE = "note"
    TEXT_ANCHORED = "text_anchored"
    CURSOR = "cursor"
    ZOOM = "zoom"
    MEASURE = "measure"
    MAGNET = "magnets"
    UNLOCK = "unlock"
    LOCK = "lock"
    CYCLEBIN = "cyclebin"
    CANDLE = "candle"
    HEIKINASHI = "heikinashi"
    CHOIDU = "ChoiDuCandles"
    RENKO = "renko"
    INDICATOR = "indicator"
    HOME = "home"
    HELP = "help"
    NOTICE = "notice"
    NEWS = "news"
    DARKMODDE = "darkmode"
    SIGNOUT = "signout"
    GOTO_DATE = "goto_date"
    OBJECT_DATA = "object_data"
    HOT_LIST = "hot_list"
    WATCHLIST = "watchlist"
    FAVORITE = "favorite"
    SPONSOR = "sponsor"
    PERSONAL = "personal"
    TECHNICAL = "technical"
    EYE_OPEN = "eye_drawing"
    EYE_CLOSE = "eye_close_drawing"
    ADVANCE = "advance"
    REPLAY = "replay"
    UNPIN = "Unpin"
    VIDEO = "Video"
    TRAIN = "Train"
    ADD_TO  ="AddTo"
    ACCEPT = "Accept"
    CAMERA = "Camera"
    CANCEL = "Cancel"
    DELETE = "Delete"
    FOLDER = "Folder"
    FILTER = "Filter"
    MARKET = "Market"
    SCROLL = "Scroll"
    LAYOUT = "Layout"
    GITHUB = "GitHub"
    UPDATE = "Update"
    REMOVE = "Remove"
    RETURN = "Return"
    PEOPLE = "People"
    QRCODE = "QRCode"
    RINGER = "Ringer"
    ROTATE = "Rotate"
    SEARCH = "Search"
    VOLUME = "Volume"
    FRIGID  = "Frigid"
    SAVE_AS = "SaveAs"
    ZOOM_IN = "ZoomIn"
    CONNECT  ="Connect"
    HISTORY = "History"
    SETTING = "Setting"
    PALETTE = "Palette"
    MESSAGE = "Message"
    FIT_PAGE = "FitPage"
    ZOOM_OUT = "ZoomOut"
    AIRPLANE = "Airplane"
    ASTERISK = "Asterisk"
    CALORIES = "Calories"
    CALENDAR = "Calendar"
    FEEDBACK = "Feedback"
    LIBRARY = "BookShelf"
    MINIMIZE = "Minimize"
    CHECKBOX = "CheckBox"
    DOCUMENT = "Document"
    LANGUAGE = "Language"
    DOWNLOAD = "Download"
    QUESTION = "Question"
    SPEAKERS = "Speakers"
    DATE_TIME = "DateTime"
    FONT_SIZE = "FontSize"
    HOME_FILL = "HomeFill"
    PAGE_LEFT = "PageLeft"
    SAVE_COPY = "SaveCopy"
    SEND_FILL = "SendFill"
    SKIP_BACK = "SkipBack"
    SPEED_OFF = "SpeedOff"
    ALIGNMENT = "Alignment"
    BLUETOOTH = "Bluetooth"
    COMPLETED = "Completed"
    CONSTRACT = "Constract"
    HEADPHONE = "Headphone"
    MEGAPHONE = "Megaphone"
    PROJECTOR = "Projector"
    EDUCATION = "Education"
    LEFT_ARROW = "LeftArrow"
    ERASE_TOOL = "EraseTool"
    PAGE_RIGHT = "PageRight"
    PLAY_SOLID = "PlaySolid"
    BOOK_SHELF = "BookShelf"
    HIGHTLIGHT = "Highlight"
    FOLDER_ADD = "FolderAdd"
    PAUSE_BOLD = "PauseBold"
    PENCIL_INK = "PencilInk"
    PIE_SINGLE = "PieSingle"
    QUICK_NOTE = "QuickNote"
    SPEED_HIGH = "SpeedHigh"
    STOP_WATCH = "StopWatch"
    ZIP_FOLDER = "ZipFolder"
    BASKETBALL = "Basketball"
    BRIGHTNESS = "Brightness"
    DICTIONARY = "Dictionary"
    MICROPHONE = "Microphone"
    ARROW_DOWN = "ChevronDown"
    MINDOWN = "mindown"
    MAXIMUM = "maximum"
    FULL_SCREEN = "FullScreen"
    MIX_VOLUMES = "MixVolumes"
    REMOVE_FROM = "RemoveFrom"
    RIGHT_ARROW = "RightArrow"
    QUIET_HOURS  ="QuietHours"
    FINGERPRINT = "Fingerprint"
    APPLICATION = "Application"
    CERTIFICATE = "Certificate"
    TRANSPARENT = "Transparent"
    IMAGE_EXPORT = "ImageExport"
    SPEED_MEDIUM = "SpeedMedium"
    LIBRARY_FILL = "LibraryFill"
    MUSIC_FOLDER = "MusicFolder"
    POWER_BUTTON = "PowerButton"
    SKIP_FORWARD = "SkipForward"
    CARE_UP_SOLID = "CareUpSolid"
    ACCEPT_MEDIUM = "AcceptMedium"
    CANCEL_MEDIUM = "CancelMedium"
    CHEVRON_RIGHT = "ChevronRight"
    CLIPPING_TOOL = "ClippingTool"
    SEARCH_MIRROR = "SearchMirror"
    SHOPPING_CART = "ShoppingCart"
    FONT_INCREASE = "FontIncrease"
    BACK_TO_WINDOW = "BackToWindow"
    COMMAND_PROMPT = "CommandPrompt"
    CLOUD_DOWNLOAD = "CloudDownload"
    DICTIONARY_ADD = "DictionaryAdd"
    CARE_DOWN_SOLID = "CareDownSolid"
    CARE_LEFT_SOLID = "CareLeftSolid"
    CLEAR_SELECTION = "ClearSelection"
    DEVELOPER_TOOLS = "DeveloperTools"
    BACKGROUND_FILL = "BackgroundColor"
    CARE_RIGHT_SOLID = "CareRightSolid"
    CHEVRON_DOWN_MED = "ChevronDownMed"
    CHEVRON_RIGHT_MED = "ChevronRightMed"
    EMOJI_TAB_SYMBOLS = "EmojiTabSymbols"
    EXPRESSIVE_INPUT_ENTRY = "ExpressiveInputEntry"
    DASH_LINE = "dashline"
    DOT_LINE = "dotline"
    LINE = "line"
    ONE_PIX = "1px"
    TWO_PIX = "2px"
    THREE_PIX = "3px"
    FOUR_PIX = "4px"
    SELECT_BAR = "selectbar"
    FORWARD = "forward"
    JUMP_TO_NOW = "jump_to_now"

    def path(self, theme=Theme.AUTO):
        return f':/qfluentwidgets/images/icons/{self.value}_{getIconColor(theme)}.svg'
    def icon_path(self):
        return f':/qfluentwidgets/images/icons/{self.value}.svg'



class Icon(QIcon):

    def __init__(self, fluentIcon: FluentIcon):
        super().__init__(fluentIcon.path())
        self.fluentIcon = fluentIcon



class Action(QAction):
    """ Fluent action

    Constructors
    ------------
    * Action(`parent`: QWidget = None, `**kwargs`)
    * Action(`text`: str, `parent`: QWidget = None, `**kwargs`)
    * Action(`icon`: QIcon | FluentIconBase, `parent`: QWidget = None, `**kwargs`)
    """

    @singledispatchmethod
    def __init__(self, parent: QObject = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.fluentIcon = None

    @__init__.register
    def _(self, text: str, parent: QObject = None, **kwargs):
        super().__init__(text, parent, **kwargs)
        self.fluentIcon = None

    @__init__.register
    def _(self, icon: QIcon, text: str, parent: QObject = None, **kwargs):
        super().__init__(icon, text, parent, **kwargs)
        self.fluentIcon = None

    @__init__.register
    def _(self, icon: FluentIconBase, text: str, parent: QObject = None, **kwargs):
        super().__init__(icon.icon(), text, parent, **kwargs)
        self.fluentIcon = icon

    def icon(self) -> QIcon:
        if self.fluentIcon:
            return Icon(self.fluentIcon)

        return super().icon()

    def setIcon(self, icon: Union[FluentIconBase, QIcon]):
        if isinstance(icon, FluentIconBase):
            self.fluentIcon = icon
            icon = icon.icon()

        super().setIcon(icon)
