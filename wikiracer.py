from lxml import html
import json
import re
import requests

WIKIPEDIA_BASE_URL = "https://en.wikipedia.org"
HASHTAG_SLUG_REGEX = r'(#|%E2%80%93).*'
RESULTS_FILE = 'results.json'

def get_race_params(params_file):
    with open(params_file) as infile:
        return json.load(infile)

def output_result(start, end, path):
    with open(RESULTS_FILE, 'w') as outfile:
        json.dump({'start': start, 'end': end, 'path': path}, outfile)

def get_page_links(page_url):
    page = requests.get(page_url)
    tree = html.fromstring(page.content)
    anchors = tree.xpath('//div[@id="mw-content-text"]/p/a')
    return [WIKIPEDIA_BASE_URL + re.sub(HASHTAG_SLUG_REGEX, '', anchor.get('href'))
            for anchor in anchors if anchor.get('href').startswith('/wiki/')]

def find_path(start, end):
    if start == end:
        return [start, end]
    visited_pages = set()

    end_links = get_page_links(end)

    path_queues = {1: [[start]] }
    current_path_queue_key = 1
    current_path_queue = path_queues[1]

    while current_path_queue:
        current_path = current_path_queue.pop(0)
        current_page = current_path[-1]
        if current_page not in visited_pages:
            visited_pages.add(current_page)
            print(len(visited_pages))
            page_links = get_page_links(current_page)
            if end in page_links:
                return current_path + [end]
            for page_link in page_links:
                if page_link in end_links:
                    path_queues.setdefault(len(current_path)+1, []).insert(0, current_path+[page_link])
                else:
                    path_queues.setdefault(len(current_path)+1, []).append(current_path+[page_link])

        if not current_path_queue:
            current_path_queue_key += 1
            if current_path_queue_key in path_queues:
                current_path_queue = path_queues[current_path_queue_key]
            else:
                return None
    return None

if __name__ == "__main__":
    params_file = input("Input JSON File: ")
    race_params = get_race_params(params_file)
    path = find_path(**race_params)
    output_result(path=path, **race_params)
