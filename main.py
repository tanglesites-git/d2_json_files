from concurrent.futures import ThreadPoolExecutor
from configuration import BASE_ADDRESS, store_dict
from data_utils import write_data, setup_data, get_value
from data_utils import weapons, dataframe, csv_frames, file_urls, write_filenames, sockets, ammo_types
from http_io import destiny_request, download_json_file
from time import perf_counter_ns


def main():
    data = None
    jwccp = None
    names = []
    urls = []
    data = destiny_request(BASE_ADDRESS + '/Platform/Destiny2/Manifest')
    print("Downloading manifest.json...")

    jwccp = data["Response"]["jsonWorldComponentContentPaths"]["en"]
    k1 = perf_counter_ns()
    for name, url in jwccp.items():
        names.append(name)
        urls.append(BASE_ADDRESS + url)
        print("Appended: " + name + " : " + BASE_ADDRESS + url)
    k2 = perf_counter_ns()
    print(f'Preprocessing {(k2 - k1)/1_000_000}ms')

    with ThreadPoolExecutor() as executor:
        executor.map(download_json_file, urls, names)


def open_cached_file(filename):
    t1 = perf_counter_ns()
    j = store_dict[filename]
    t2 = perf_counter_ns()
    print(f'Pull {filename} into memory {(t2 - t1)/1_000_000}ms')
    return j



def parse_damage_types(damage_type_value: dict):
    # Damage Type
    dt_hash = get_value('hash', damage_type_value)
    dt_displayProperties = get_value('displayProperties', damage_type_value)
    dt_name = get_value('name', dt_displayProperties)
    dt_icon = get_value('icon', dt_displayProperties)
    dt_description = get_value('description', dt_displayProperties)
    dt_transparentIcon = get_value('transparentIconPath', damage_type_value)
    dt_color = get_value('color', damage_type_value)
    return dt_hash, dt_name, dt_icon, dt_description, dt_transparentIcon, dt_color


def parse_lore_types(lore_value: dict):
    lt_displayProperties = get_value('displayProperties', lore_value)
    lt_hash = get_value('hash', lore_value)
    lt_description = get_value('description', lt_displayProperties)
    lt_subtitle = get_value('subtitle', lore_value)
    return lt_hash, lt_description, lt_subtitle


def parse_collectible_type(collectible_value: dict):
    ct_hash = get_value('hash', collectible_value)
    ct_sourceString = get_value('sourceString', collectible_value)
    return ct_hash, ct_sourceString


def parse_investment_stats(investment_stats: list, stats_json: dict):
    stat_object_list = []
    for item in investment_stats:
        stat_type_hash = item['statTypeHash']
        stat_value_value = item['value']
        stat_value = stats_json[str(stat_type_hash)]
        stat_name = stat_value['displayProperties']['name']
        stat_desc = stat_value['displayProperties']['description']
        stat_object_list.append({
            'name': stat_name,
            'description': stat_desc,
            'value': stat_value_value,
        })
    return stat_object_list


def build_sockets(socket_index_list: list, socket_entries: dict, socket_item: list, plugset_json: dict, diid_json: dict, stats_json: dict, type: str):
    plug_set_hash = None
    
    for socket_index in socket_index_list:
        # print(f'Type: {type} :: {socket_index}')
        socket_entry = socket_entries[socket_index]
        curated_roll = socket_entry['singleInitialItemHash']
        socket_item['CURATED_ROLLS'].append(curated_roll)

        if 'reusablePlugSetHash' in socket_entry:
            plug_set_hash = socket_entry['reusablePlugSetHash']

        if 'randomizedPlugSetHash' in socket_entry:
            plug_set_hash = socket_entry['randomizedPlugSetHash']

        if plug_set_hash is None:
            continue

        plug_set_object = plugset_json[str(plug_set_hash)]['reusablePlugItems']
        for plug_item in plug_set_object:
            plug_item_hash = plug_item['plugItemHash']
            inventory_item = diid_json[str(plug_item_hash)]
            inventory_item_display_props = get_value('displayProperties', inventory_item)
            inventory_item_inventory = get_value('inventory', inventory_item)
            inventory_item_hash = get_value('hash', inventory_item)
            inventory_item_name = get_value('name', inventory_item_display_props)
            inventory_item_desc = get_value('description', inventory_item_display_props)
            inventory_item_icon = get_value('icon', inventory_item_display_props)
            inventory_item_display_name = get_value('itemTypeDisplayName', inventory_item)
            inventory_item_tier_type = get_value('tierTypeName', inventory_item_inventory)
            inventory_item_invenstment_stats = get_value('investmentStats', inventory_item)

            socket_item[type].append({
                'hash': inventory_item_hash,
                'name': inventory_item_name,
                'description': inventory_item_desc,
                'icon': inventory_item_icon,
                'display_name': inventory_item_display_name,
                'tier_type': inventory_item_tier_type,
                'stats': parse_investment_stats(inventory_item_invenstment_stats, stats_json)
            })


def create_files():

    with ThreadPoolExecutor() as executor:
        executor.map(setup_data, file_urls)

    diid_json = open_cached_file("DestinyInventoryItemDefinition")
    stats_json = open_cached_file("DestinyStatDefinition")
    collectible_json = open_cached_file("DestinyCollectibleDefinition")
    lore_json = open_cached_file("DestinyLoreDefinition")
    plugset_json = open_cached_file("DestinyPlugSetDefinition")
    damage_type = open_cached_file("DestinyDamageTypeDefinition")

    for key, value in diid_json.items():
        if 'itemType' in value and value['itemType'] == 3:
            p1 = perf_counter_ns()
            # Dictionaries
            displayProperties = get_value('displayProperties', value)
            inventory = get_value('inventory', value)
            equippingBlock = get_value('equippingBlock', value)
            investment_stats = get_value('investmentStats', value)
            sockets_list = get_value('sockets', value)
            socket_categories = get_value('socketCategories', sockets_list)
            socket_entries = get_value('socketEntries', sockets_list)

            # Top Level Properties
            hash_id = get_value('hash', value)
            # print(hash_id)
            name = get_value('name', displayProperties)
            icon = get_value('icon', displayProperties)
            watermark = get_value('iconWatermark', value)
            screenshot = get_value('screenshot', value)
            displayName = get_value('itemTypeDisplayName', value)
            flavorText = get_value("flavorText", value)
            tierTypeName = get_value('tierTypeName', inventory)
            ammoType = get_value('ammoType', equippingBlock)

            # Hashes
            collectible_hash = get_value('collectibleHash', value)
            lore_hash = get_value('loreHash', value)
            damage_type_hash = get_value('defaultDamageTypeHash', value)

            # Relative Values
            damage_type_value = get_value(f"{damage_type_hash}", damage_type)
            lore_value = get_value(f"{lore_hash}", lore_json)
            collectible_value = get_value(f"{collectible_hash}", collectible_json)

            dt_hash, dt_name, dt_icon, dt_description, dt_transparentIcon, dt_color = parse_damage_types(damage_type_value)
            lt_hash, lt_description, lt_subtitle = parse_lore_types(lore_value)
            ct_hash, ct_sourceString = parse_collectible_type(collectible_value)
            stat_object_list = parse_investment_stats(investment_stats, stats_json)

            socket_item = {
                'weapon_hash': hash_id,
                'INTRINSIC': [],
                'WEAPON_PERKS': [],
                'WEAPON_MODS': [],
                'CURATED_ROLLS': []
            }

            # Iterate over socket categories
            q1 = perf_counter_ns()
            for category in socket_categories:
                
                socket_category_hash = category['socketCategoryHash']

                # Skip over cosmetics: They just add bloat to the file
                if socket_category_hash == 2048875504:
                    continue

                socket_index_list = category['socketIndexes']

                if socket_category_hash == 3956125808:
                    build_sockets(socket_index_list, socket_entries, socket_item, plugset_json, diid_json, stats_json, 'INTRINSIC')

                if socket_category_hash == 4241085061:
                    build_sockets(socket_index_list, socket_entries, socket_item, plugset_json, diid_json, stats_json, 'WEAPON_PERKS')

                if socket_category_hash == 2685412949:
                    build_sockets(socket_index_list, socket_entries, socket_item, plugset_json, diid_json, stats_json, 'WEAPON_MODS')
                    
            q2 = perf_counter_ns()
                
            p2 = perf_counter_ns()

            wt = (p2 - p1)/1_000_000
            st = (q2 - q1)/1_000_000
            print(f"Processed Weapon {name} {wt}ms")
            print(f"Socket Processing Time {st}ms")
            print(f"Delta Processing Time {wt - st}ms")


            sockets.append(socket_item)
            weapons.append({
                'hash': hash_id,
                'name': name,
                'icon': icon,
                'displayName': displayName,
                'flavorText': flavorText,
                'tierTypeName': tierTypeName,
                'watermark': watermark,
                'screenshot': screenshot,
                'ammotype': {
                    'name': ammo_types[str(ammoType)]['name'],
                    'icon': ammo_types[str(ammoType)]['icon']
                },
                'damage': {
                    'hash_id': dt_hash,
                    'name': dt_name,
                    'icon': dt_icon,
                    'description': dt_description,
                    'transparentIcon': dt_transparentIcon,
                    'color': dt_color
                },
                'lore': {
                    'hash': lt_hash,
                    'description': lt_description,
                    'subtitle': lt_subtitle
                },
                'collectible': {
                    'hash': ct_hash,
                    'sourceString': ct_sourceString
                },
                'stats': stat_object_list
            })

            dataframe['hash'].append(hash_id)
            dataframe['name'].append(name)
            dataframe['icon'].append(icon)
            dataframe['displayName'].append(displayName)
            dataframe['flavorText'].append(flavorText)
            dataframe['tierTypeName'].append(tierTypeName)
            dataframe['watermark'].append(watermark)
            dataframe['screenshot'].append(screenshot)
            dataframe['displayName'].append(displayName)
            dataframe['damageType'].append(dt_name)
            dataframe['lore_subtitle'].append(lt_subtitle)
            dataframe['lore_description'].append(lt_description)
            dataframe['source_string'].append(ct_sourceString)

            csv_frames.append([hash_id, name, icon, watermark, screenshot, displayName, flavorText, tierTypeName, dt_name, lt_description, lt_subtitle, ct_sourceString])

    t1 = perf_counter_ns()
    with ThreadPoolExecutor() as executor:
        executor.map(write_data, write_filenames, [weapons, dataframe, csv_frames, sockets])
    t2 = perf_counter_ns()
    print(f'Files have been saved {(t2 - t1)/1_000_000}ms')

if __name__ == '__main__':
    start = perf_counter_ns()
    main()
    create_files()
    end = perf_counter_ns()
    print(f'Done: {(end - start)/1_000_000}ms')