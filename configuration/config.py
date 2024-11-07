import configparser
from pathlib import Path

ROOT = Path(__file__).parent.parent.absolute()

config = configparser.ConfigParser()
config.read(ROOT / 'dev.ini')