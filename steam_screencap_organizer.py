import os
import re

import requests
from bs4 import BeautifulSoup


def get_app_name(steam_app_id):
    print 'retrieving name for steam app with ID', steam_app_id
    try:
        soup = BeautifulSoup(
            requests.get('https://steamdb.info/app/' + steam_app_id).content, 'html.parser')
        name = soup.find('td', itemprop='name').string

        # replace illegal characters with an underscore
        for c in ['\\', '/', ':', '"', ',', '*', '?', '<', '>', '|']:
            name = name.replace(c, '_')

        return name
    except requests.exceptions.RequestException:
        print 'error obtaining name for', steam_app_id
        return None


def organize_steam_screencaps(path):
    pattern = re.compile(r'^(\d{6})_(\d{14}|\d{4}-\d{2}-\d{2})_(\d+)\.png$')

    path = os.path.expanduser(path)

    app_names = {}
    # load app IDs and Names from file, if one exists
    storage_path = os.path.join(path, 'app names dictionary.txt')
    if os.path.exists(storage_path):
        names_storage_pattern = re.compile(r'^(.+)  :\|:  (.+)$')
        for line in open(storage_path, 'r'):
            match = re.match(names_storage_pattern, line)
            if match:
                app_names[match.group(1)] = match.group(2)
        del names_storage_pattern

    update_storage_file = False  # this will be made True if new steam app names are fetched

    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)

        if os.path.isdir(file_path):
            continue

        match = re.match(pattern, filename)

        if match:
            app_id = match.group(1)

            if app_id not in app_names:
                app_names[app_id] = get_app_name(app_id)
                if app_names[app_id] is not None:
                    update_storage_file = True

            if app_names[app_id] is None:
                continue

            # date_time = match.group(2)
            # shot_number = match.group(3)

            new_path = os.path.join(path, app_names[app_id], filename)

            os.renames(file_path, new_path)

    if update_storage_file:
        # save app IDs and Names to file
        print 'saving app names to file...'
        storage_file = open(storage_path, 'w')
        for key in app_names:
            storage_file.write(key + '  :|:  ' + app_names[key] + '\n')
        storage_file.close()


def clean_empty_directories(path):
    path = os.path.expanduser(path)

    # return None if path is not a directory
    if not os.path.isdir(path):
        return

    # create list of items found in given directory
    path_items = os.listdir(path)

    # if directory is empty, delete it
    if len(path_items) == 0:
        print '"' + path + '" is empty. Removing...'
        try:
            os.removedirs(path)
        except OSError:
            print 'could not remove "' + path + '"'

    # if directory is not empty, recurse for each item in directory
    else:
        for item in path_items:
            clean_empty_directories(os.path.join(path, item))


if __name__ == '__main__':
    organize_steam_screencaps(r'~\Pictures\screencaps\Steam')
    print 'pruning steam screencaps folder for empty directories'
    clean_empty_directories(r'~\Pictures\screencaps\Steam')
