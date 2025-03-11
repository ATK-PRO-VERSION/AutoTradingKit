import json
import threading
from PySide6.QtCore import QCoreApplication,Signal,QObject,Qt,Slot
from atklip.gui.qfluentwidgets.common.icon import *
# Gets or creates a logger

config_path = get_real_path("atklip/appdata")

class ConfigManager(QObject):
    sig_set_single_data = Signal(tuple)
    def __init__(self, filepath=f"{config_path}/config.json"):
        super().__init__()
        #self.moveToThread(QCoreApplication.instance().thread())
        self.config_lock = threading.Lock()
        self.config = {}
        self.filepath = filepath
        if filepath:
            self.load_config_file(filepath)
        self.sig_set_single_data.connect(self.set_config_value,Qt.ConnectionType.AutoConnection)
  
    def create_config_file(self, filepath):
        with open(filepath, 'w') as f:
            json.dump(self.config, f)
            f.close()
    @Slot()
    def set_config_value(self, args):
        key, value = args[0], args[1]
        keys = key.split('.')
        current = self.config 
        if len(keys) == 1:
            current[keys[-1]] = value
            self.save_config_file()
            return
        current = self.config   
        for k in keys[:-1]:
            if current != {}:
                if k not in list(current.keys()):
                    current[k] = {}
            else:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value
        self.save_config_file()
        return self.get_config_value(key)
        #self.load_config_file(self.filepath)

    def set_config_values(self, *args, **kwargs):
        for arg in args:
            if not isinstance(arg, tuple) or len(arg) != 2:
                raise ValueError('Arguments must be passed as tuples with two elements')
            key, value = arg[0], arg[1]
            self.sig_set_single_data.emit((key, value))
            QCoreApplication.processEvents()

        for key, value in kwargs.items():
            self.sig_set_single_data.emit((key, value))
            QCoreApplication.processEvents()

    def get_config_value(self, key, default=None):
        keys = key.split('.')
        current = self.config
        for k in keys[:-1]:
            if k not in current:
                return default
            current = current[k]
        return current.get(keys[-1], default)

    def delete_config_value(self, key):
        keys = key.split('.')
        current = self.config
        for k in keys[:-1]:
            if k not in current:
                return
            current = current[k]
        if keys[-1] in current:
            del current[keys[-1]]
            self.save_config_file()
            #self.load_config_file(self.filepath)
        else:
            return
        
    def save_config_file(self):
        self.create_config_file(self.filepath)

    
    def load_config_file(self, filepath):
        with self.config_lock:
            try:
                with open(filepath, 'r') as f:
                    self.config = json.load(f)
            except (IOError, json.JSONDecodeError):
                self.config = {}
                self.save_config_file()
    
    # def load_config_file(self, filepath):
    #     try:
    #         with open(filepath) as f:
    #             self.config = json.load(f)
    #             f.close()
    #     except (IOError, json.JSONDecodeError):
    #         self.config = {}
    #         self.save_config_file()
    def get_all_config(self):
        return self.config


# global AppConfig

AppConfig = ConfigManager()


# coding:utf-8
import sys
from enum import Enum

from PySide6.QtCore import QLocale
from atklip.gui import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            OptionsValidator, RangeConfigItem, RangeValidator,
                            FolderListValidator, Theme, FolderValidator, ConfigSerializer)


class Language(Enum):
    """ Language enumeration """

    CHINESE_SIMPLIFIED = QLocale(QLocale.Chinese, QLocale.China)
    CHINESE_TRADITIONAL = QLocale(QLocale.Chinese, QLocale.HongKong)
    ENGLISH = QLocale(QLocale.English)
    AUTO = QLocale()


class LanguageSerializer(ConfigSerializer):
    """ Language serializer """

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


def isWin11():
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000


class Config(QConfig):
    """ Config of application """

    # folders
    musicFolders = ConfigItem(
        "Folders", "LocalMusic", [], FolderListValidator())
    downloadFolder = ConfigItem(
        "Folders", "Download", "app/download", FolderValidator())

    # main window
    micaEnabled = ConfigItem("MainWindow", "MicaEnabled", isWin11(), BoolValidator())
    dpiScale = OptionsConfigItem(
        "MainWindow", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)
    language = OptionsConfigItem(
        "MainWindow", "Language", Language.AUTO, OptionsValidator(Language), LanguageSerializer(), restart=True)

    # Material
    blurRadius  = RangeConfigItem("Material", "AcrylicBlurRadius", 15, RangeValidator(0, 40))

    # software update
    checkUpdateAtStartUp = ConfigItem("Update", "CheckUpdateAtStartUp", True, BoolValidator())


YEAR = 2023
AUTHOR = "zhiyiYo"

HELP_URL = "https://qfluentwidgets.com"
REPO_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets"
EXAMPLE_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets/tree/PySide6/examples"
FEEDBACK_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets/issues"
RELEASE_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets/releases/latest"
ZH_SUPPORT_URL = "https://qfluentwidgets.com/zh/price/"
EN_SUPPORT_URL = "https://qfluentwidgets.com/price/"


cfg = Config()
cfg.themeMode.value = Theme.AUTO
qconfig.load('app/config/config.json', cfg)