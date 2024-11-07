from json import loads
from time import perf_counter_ns

from configuration import store_dict


def get_value(key: str, value: dict):
    if value is None:
        return None
    if key in value:
        return value[key]

def setup_data(filename: str):
    t1 = perf_counter_ns()
    with open(filename, 'r', encoding='utf-8') as file:
        json_data = loads(file.read())
        name = filename.split('/')[-1].split('.')[0]
        store_dict[name] = json_data
    t2 = perf_counter_ns()
    print(f'Preparing in memory cache: {filename} {(t2 - t1) / 1_000_000}')