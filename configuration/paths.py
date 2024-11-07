from pathlib import Path

ROOT = Path(__file__).parent.parent.absolute()
DATA = ROOT / 'data' / 'json_objects'
BASE_ADDRESS = 'https://www.bungie.net'
store_dict = {
    'DestinyInventoryItemDefinition': {},
    'DestinyStatDefinition': {},
    'DestinyLoreDefinition': {},
    'DestinyDamageTypeDefinition': {},
    'DestinyCollectibleDefinition': {},
    'DestinyPlugSetDefinition': {},
    'DestinySocketCategoryDefinition': {}
}