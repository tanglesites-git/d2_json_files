from json import dumps
from time import perf_counter_ns
from configuration import config

from requests import get

from configuration import DATA


def destiny_request(url: str):
    api_key = config["Destiny"]["apikey"]
    t1 = perf_counter_ns()
    with get(url, stream=True, allow_redirects=True, headers={'x-api-key': api_key}) as r:
        return r.json()
    t2 = perf_counter_ns()
    print(f'Downloaded {url} {(t2 - t1)/1_000_000}ms')

def download_json_file(url: str, filename: str):
    try:
        t1 = perf_counter_ns()
        json_dict = destiny_request(url)
        with open(DATA / f'{filename}.json', 'w', encoding='utf-8') as file:
            file.write(dumps(json_dict))
        t2 = perf_counter_ns()
        print(f"Getting File: {filename}.json {(t2 - t1)/1_000_000}ms")
    except Exception as e:
        print(e)
