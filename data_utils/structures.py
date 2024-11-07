
sockets = []
weapons = []
dataframe = {
    'hash': [],
    'name': [],
    'icon': [],
    'watermark': [],
    'screenshot': [],
    'displayName': [],
    'flavorText': [],
    'tierTypeName': [],
    'damageType': [],
    'lore_description': [],
    'lore_subtitle': [],
    'source_string': []
}
csv_frames = [['hash', 'name', 'icon', 'watermark', 'screenshot', 'displayName', 'flavorText', 'tierTypeName', 'damageType', 'lore_description', 'lore_subtitle', 'source_string']]
file_urls = [
    './data/json_objects/DestinyInventoryItemDefinition.json',
    './data/json_objects/DestinyStatDefinition.json',
    './data/json_objects/DestinyLoreDefinition.json',
    './data/json_objects/DestinyDamageTypeDefinition.json',
    './data/json_objects/DestinyCollectibleDefinition.json',
    './data/json_objects/DestinyPlugSetDefinition.json',
    './data/json_objects/DestinySocketCategoryDefinition.json',
]

write_filenames = [
    'weapons.json',
    'dataframe.json',
    'weapons.csv',
    'sockets.json'
]

ammo_types = {
    '1': {
        'name': 'Primary',
        'icon': '/common/destiny2_content/icons/99f3733354862047493d8550e46a45ec.png',
        'enum': 1,
        'children': [
            'Auto Rifles',
            'Bows',
            'Hand Cannons',
            'Pulse Rifles',
            'Scout Rifles',
            'Sidearms',
            'Submachine Guns'
        ]
    },
    '2': {
        'name': 'Special',
        'icon': '/common/destiny2_content/icons/d920203c4fd4571ae7f39eb5249eaecb.png',
        'enum': 2,
        'children': [
            'Shotguns',
            'Grenade Launchers',
            'Fusion Rifles',
            'Sniper Rifles',
            'Trace Rifles',
            'Sidearms',
            'Glaives'
        ]
    },
    '3': {
        'name': 'Heavy',
        'icon': '/common/destiny2_content/icons/78ef0e2b281de7b60c48920223e0f9b1.png',
        'enum': 3,
        'children': [
            'Linear Fusion Rifles',
            'Grenade Launchers',
            'Machine Guns',
            'Rocket Launchers',
            'Trace Rifles',
            'Swords'
        ]
    }
}

if __name__ == '__main__':
    pass
