from concurrent.futures import ThreadPoolExecutor
from configuration import BASE_ADDRESS
from data_utils import write_data, setup_data, get_value
from data_utils import (
    weapons,
    dataframe,
    csv_frames,
    file_urls,
    write_filenames,
    sockets,
    ammo_types,
)
from dtos import (
    CacheStore,
    CollectibleDto,
    DamageTypDto,
    LoreTypeDto,
    PlugItemDto,
    WeaponDto,
)
from http_io import destiny_request, download_json_file
from time import perf_counter_ns


def main():
    data = None
    jwccp = None
    names = []
    urls = []
    data = destiny_request(BASE_ADDRESS + "/Platform/Destiny2/Manifest")
    print("Downloading manifest.json...")

    jwccp = data["Response"]["jsonWorldComponentContentPaths"]["en"]
    k1 = perf_counter_ns()
    for name, url in jwccp.items():
        names.append(name)
        urls.append(BASE_ADDRESS + url)
        print("Appended: " + name + " : " + BASE_ADDRESS + url)
    k2 = perf_counter_ns()
    print(f"Preprocessing {(k2 - k1)/1_000_000}ms")

    with ThreadPoolExecutor() as executor:
        executor.map(download_json_file, urls, names)


def parse_investment_stats(investment_stats: list, stats_json: dict):
    stat_object_list = []
    for item in investment_stats:
        stat_type_hash = item["statTypeHash"]
        stat_value_value = item["value"]
        stat_value = stats_json[str(stat_type_hash)]
        stat_name = stat_value["displayProperties"]["name"]
        stat_desc = stat_value["displayProperties"]["description"]
        stat_object_list.append(
            {
                "name": stat_name,
                "description": stat_desc,
                "value": stat_value_value,
            }
        )
    return stat_object_list


def __build_sockets(
    socket_index_list: list,
    socket_entries: dict,
    socket_item: list,
    plugset_json: dict,
    diid_json: dict,
    stats_json: dict,
    type: str,
):
    plug_set_hash = None

    for socket_index in socket_index_list:
        socket_entry = socket_entries[socket_index]
        curated_roll = get_value("singleInitialItemHash", socket_entry)
        socket_item["CURATED_ROLLS"].append(curated_roll)

        if "reusablePlugSetHash" in socket_entry:
            plug_set_hash = get_value("reusablePlugSetHash", socket_entry)

        if "randomizedPlugSetHash" in socket_entry:
            plug_set_hash = get_value("randomizedPlugSetHash", socket_entry)

        if plug_set_hash is None:
            continue

        plug_set_object = plugset_json[str(plug_set_hash)]["reusablePlugItems"]
        for plug_item in plug_set_object:
            plug_item_dto = PlugItemDto(plug_item, diid_json)

            socket_item[type].append(
                {
                    "hash": plug_item_dto.inventory_item_hash,
                    "name": plug_item_dto.inventory_item_name,
                    "description": plug_item_dto.inventory_item_desc,
                    "icon": plug_item_dto.inventory_item_icon,
                    "display_name": plug_item_dto.inventory_item_display_name,
                    "tier_type": plug_item_dto.inventory_item_tier_type,
                    "stats": parse_investment_stats(
                        plug_item_dto.inventory_item_invenstment_stats, stats_json
                    ),
                }
            )


def build_sockets(wdto: WeaponDto, store: CacheStore, socket_item: list):
    for category in wdto.socket_categories:
        socket_category_hash = category["socketCategoryHash"]

        # Skip over cosmetics: They just add bloat to the file
        if socket_category_hash == 2048875504:
            continue

        socket_index_list = category["socketIndexes"]

        if socket_category_hash == 3956125808:
            __build_sockets(
                socket_index_list,
                wdto.socket_entries,
                socket_item,
                store.plugset_json,
                store.diid_json,
                store.stats_json,
                "INTRINSIC",
            )

        if socket_category_hash == 4241085061:
            __build_sockets(
                socket_index_list,
                wdto.socket_entries,
                socket_item,
                store.plugset_json,
                store.diid_json,
                store.stats_json,
                "WEAPON_PERKS",
            )

        if socket_category_hash == 2685412949:
            __build_sockets(
                socket_index_list,
                wdto.socket_entries,
                socket_item,
                store.plugset_json,
                store.diid_json,
                store.stats_json,
                "WEAPON_MODS",
            )


def weapon_dict(
    wdto: WeaponDto,
    dt_dto: DamageTypDto,
    lore_dto: LoreTypeDto,
    collectible_dto: CollectibleDto,
    stat_object_list,
):
    return {
        "hash": wdto.hash_id,
        "name": wdto.name,
        "icon": wdto.icon,
        "displayName": wdto.displayName,
        "flavorText": wdto.flavorText,
        "tierTypeName": wdto.tierTypeName,
        "watermark": wdto.watermark,
        "screenshot": wdto.screenshot,
        "ammotype": {
            "name": ammo_types[str(wdto.ammoType)]["name"],
            "icon": ammo_types[str(wdto.ammoType)]["icon"],
        },
        "damage": {
            "hash_id": dt_dto.dt_hash,
            "name": dt_dto.dt_name,
            "icon": dt_dto.dt_icon,
            "description": dt_dto.dt_description,
            "transparentIcon": dt_dto.dt_transparentIcon,
            "color": dt_dto.dt_color,
        },
        "lore": {
            "hash": lore_dto.lt_hash,
            "description": lore_dto.lt_description,
            "subtitle": lore_dto.lt_subtitle,
        },
        "collectible": {
            "hash": collectible_dto.ct_hash,
            "sourceString": collectible_dto.ct_sourceString,
        },
        "stats": stat_object_list,
    }


def weapon_df(
    wdto: WeaponDto,
    dt_dto: DamageTypDto,
    lore_dto: LoreTypeDto,
    collectible_dto: CollectibleDto,
):
    dataframe["hash"].append(wdto.hash_id)
    dataframe["name"].append(wdto.name)
    dataframe["icon"].append(wdto.icon)
    dataframe["displayName"].append(wdto.displayName)
    dataframe["flavorText"].append(wdto.flavorText)
    dataframe["tierTypeName"].append(wdto.tierTypeName)
    dataframe["watermark"].append(wdto.watermark)
    dataframe["screenshot"].append(wdto.screenshot)
    dataframe["displayName"].append(wdto.displayName)
    dataframe["damageType"].append(dt_dto.dt_name)
    dataframe["lore_subtitle"].append(lore_dto.lt_subtitle)
    dataframe["lore_description"].append(lore_dto.lt_description)
    dataframe["source_string"].append(collectible_dto.ct_sourceString)


def weapon_csv(
    wdto: WeaponDto,
    dt_dto: DamageTypDto,
    lore_dto: LoreTypeDto,
    collectible_dto: CollectibleDto,
):
    return [
        wdto.hash_id,
        wdto.name,
        wdto.icon,
        wdto.watermark,
        wdto.screenshot,
        wdto.displayName,
        wdto.flavorText,
        wdto.tierTypeName,
        dt_dto.dt_name,
        lore_dto.lt_description,
        lore_dto.lt_subtitle,
        collectible_dto.ct_sourceString,
    ]


def create_files():
    t1 = perf_counter_ns()
    with ThreadPoolExecutor() as executor:
        executor.map(
            write_data, write_filenames, [weapons, dataframe, csv_frames, sockets]
        )
    t2 = perf_counter_ns()
    print(f"Files have been saved {(t2 - t1)/1_000_000}ms")


def aggregate_data():
    with ThreadPoolExecutor() as executor:
        executor.map(setup_data, file_urls)

    cache_store = CacheStore()
    s1 = perf_counter_ns()
    for key, value in cache_store.diid_json.items():
        if "itemType" in value and value["itemType"] == 3:
            p1 = perf_counter_ns()
            wdto = WeaponDto(value)

            # Relative Values
            damage_type_value = get_value(
                f"{wdto.damage_type_hash}", cache_store.damage_type
            )
            lore_value = get_value(f"{wdto.lore_hash}", cache_store.lore_json)
            collectible_value = get_value(
                f"{wdto.collectible_hash}", cache_store.collectible_json
            )

            dt_dto = DamageTypDto(damage_type_value)
            lore_dto = LoreTypeDto(lore_value)
            collectible_dto = CollectibleDto(collectible_value)
            stat_object_list = parse_investment_stats(
                wdto.investment_stats, cache_store.stats_json
            )

            socket_item = {
                "weapon_hash": wdto.hash_id,
                "INTRINSIC": [],
                "WEAPON_PERKS": [],
                "WEAPON_MODS": [],
                "CURATED_ROLLS": [],
            }

            # Iterate over socket categories
            q1 = perf_counter_ns()
            build_sockets(wdto, cache_store, socket_item)

            q2 = perf_counter_ns()

            p2 = perf_counter_ns()

            wt = (p2 - p1) / 1_000_000
            st = (q2 - q1) / 1_000_000
            print(f"Processed Weapon {wdto.name} {wt}ms")
            print(f"Socket Processing Time {st}ms")
            print(f"Delta Processing Time {wt - st}ms")

            sockets.append(socket_item)
            weapons.append(
                weapon_dict(wdto, dt_dto, lore_dto, collectible_dto, stat_object_list)
            )

            weapon_df(wdto, dt_dto, lore_dto, collectible_dto)

            csv_frames.append(weapon_csv(wdto, dt_dto, lore_dto, collectible_dto))
    s2 = perf_counter_ns()
    print(f'Data Aggregation: {(s2 - s1) / 1_000_000}ms')

if __name__ == "__main__":
    start = perf_counter_ns()
    # main()
    aggregate_data()
    create_files()
    end = perf_counter_ns()
    print(f"Done: {(end - start)/1_000_000}ms")
