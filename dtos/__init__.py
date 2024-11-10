from time import perf_counter_ns
from configuration import store_dict


class ValueDTO:

  def get_value(self, key: str, value: dict):
    if value is None:
        return None
    if key in value:
        return value[key]


class WeaponDto(ValueDTO):

  def __init__(self, value: dict):
    self.displayProperties = self.get_value('displayProperties', value)
    self.inventory = self.get_value('inventory', value)
    self.equippingBlock = self.get_value('equippingBlock', value)
    self.investment_stats = self.get_value('investmentStats', value)
    self.sockets_list = self.get_value('sockets', value)
    self.socket_categories = self.get_value('socketCategories', self.sockets_list)
    self.socket_entries = self.get_value('socketEntries', self.sockets_list)

    self.hash_id = self.get_value('hash', value)
    self.name = self.get_value('name', self.displayProperties)
    self.icon = self.get_value('icon', self.displayProperties)
    self.watermark = self.get_value('iconWatermark', value)
    self.screenshot = self.get_value('screenshot', value)
    self.displayName = self.get_value('itemTypeDisplayName', value)
    self.flavorText = self.get_value("flavorText", value)
    self.tierTypeName = self.get_value('tierTypeName', self.inventory)
    self.ammoType = self.get_value('ammoType', self.equippingBlock)

    self.collectible_hash = self.get_value('collectibleHash', value)
    self.lore_hash = self.get_value('loreHash', value)
    self.damage_type_hash = self.get_value('defaultDamageTypeHash', value)
    


class DamageTypDto(ValueDTO):
   
  def __init__(self, damage_type_value):
    self.dt_hash = self.get_value('hash', damage_type_value)
    self.dt_displayProperties = self.get_value('displayProperties', damage_type_value)
    self.dt_name = self.get_value('name', self.dt_displayProperties)
    self.dt_icon = self.get_value('icon', self.dt_displayProperties)
    self.dt_description = self.get_value('description', self.dt_displayProperties)
    self.dt_transparentIcon = self.get_value('transparentIconPath', damage_type_value)
    self.dt_color = self.get_value('color', damage_type_value)


class LoreTypeDto(ValueDTO):
  
  def __init__(self, lore_value: dict):
    self.lt_displayProperties = self.get_value('displayProperties', lore_value)
    self.lt_hash = self.get_value('hash', lore_value)
    self.lt_description = self.get_value('description', self.lt_displayProperties)
    self.lt_subtitle = self.get_value('subtitle', lore_value)


class CollectibleDto(ValueDTO):

  def __init__(self, collectible_value):
    self.ct_hash = self.get_value('hash', collectible_value)
    self.ct_sourceString = self.get_value('sourceString', collectible_value)


class PlugItemDto(ValueDTO):

  def __init__(self, plug_item, diid_json):
    self.plug_item_hash = self.get_value('plugItemHash', plug_item)
    self.inventory_item = self.get_value(str(self.plug_item_hash), diid_json)
    self.inventory_item_display_props = self.get_value('displayProperties', self.inventory_item)
    self.inventory_item_inventory = self.get_value('inventory', self.inventory_item)
    self.inventory_item_hash = self.get_value('hash', self.inventory_item)
    self.inventory_item_name = self.get_value('name', self.inventory_item_display_props)
    self.inventory_item_desc = self.get_value('description', self.inventory_item_display_props)
    self.inventory_item_icon = self.get_value('icon', self.inventory_item_display_props)
    self.inventory_item_display_name = self.get_value('itemTypeDisplayName', self.inventory_item)
    self.inventory_item_tier_type = self.get_value('tierTypeName', self.inventory_item_inventory)
    self.inventory_item_invenstment_stats = self.get_value('investmentStats', self.inventory_item)


class CacheStore:

  def __init__(self):
    self.diid_json = CacheStore.open("DestinyInventoryItemDefinition")
    self.stats_json = CacheStore.open("DestinyStatDefinition")
    self.collectible_json = CacheStore.open("DestinyCollectibleDefinition")
    self.lore_json = CacheStore.open("DestinyLoreDefinition")
    self.plugset_json = CacheStore.open("DestinyPlugSetDefinition")
    self.damage_type = CacheStore.open("DestinyDamageTypeDefinition")

  @staticmethod
  def open(filename):
    t1 = perf_counter_ns()
    j = store_dict[filename]
    t2 = perf_counter_ns()
    print(f'Pull {filename} into memory {(t2 - t1)/1_000_000}ms')
    return j