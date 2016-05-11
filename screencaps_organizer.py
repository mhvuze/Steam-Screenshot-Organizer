import os
import re

import requests
from bs4 import BeautifulSoup


def steam():
    def get_app_name(app_id):
        print 'retrieving name for steam app', app_id
        try:
            soup = BeautifulSoup(
                requests.get('https://steamdb.info/app/' + app_id)
                    .content, 'html.parser')
            name = soup.find('td', itemprop='name').string

            # replace illegal characters with an underscore
            for c in ['\\', '/', ':', '"', ',', '*', '?', '<', '>', '|']:
                name = name.replace(c, '_')

            return name
        except requests.exceptions.RequestException:
            print 'error obtaining name for', app_id
            return None

    pattern = re.compile(r'^(\d{6})_(\d{14}|\d{4}-\d{2}-\d{2})_(\d+)\.png$')

    path = r'C:\Users\Blake\Pictures\screencaps\Steam'

    # TODO: load app IDs and Names from file, if one exists
    app_names = {}

    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)

        if os.path.isdir(file_path):
            continue

        match = re.match(pattern, filename)

        if match:
            app_id = match.group(1)

            # TODO: save app IDs and Names to file
            if app_id not in app_names:
                app_names[app_id] = get_app_name(app_id)

            if app_names[app_id] is None:
                continue

            # date_time = match.group(2)
            # shot_number = match.group(3)

            new_path = os.path.join(path, app_names[app_id], filename)

            os.renames(file_path, new_path)

            # print new_path


def VLC():
    pattern = re.compile(r'^(.+)-(\d{5}).png$')

    path = r'C:\Users\Blake\Pictures\screencaps\VLC'

    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)

        if os.path.isdir(file_path):
            continue

        match = re.match(pattern, filename)

        if match:
            title = match.group(1)
            image_number = match.group(2)

            new_path = os.path.join(path, title, image_number + '.png')

            os.renames(file_path, new_path)
    return


def clean_empty_directories(path):
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
    steam()
    VLC()
    print 'pruning screencaps folder for empty directories'
    clean_empty_directories(r'C:\Users\Blake\Pictures\screencaps\16')
