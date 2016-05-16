import argparse
import os
import re

import requests
from bs4 import BeautifulSoup


# take a steam app id and return its name, retrieved from steamdb.info. return None if could not retrieve the name
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


def organize_steam_screenshots(path):
    # regular expression pattern for screenshot filenames
    pattern = re.compile(r'^(\d{6})_(\d{14}|\d{4}-\d{2}-\d{2})_(\d+)\.png$')

    # expand the path from ~/ format
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

    # cycle through each item in the steam screenshots folder
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)

        # skip over directories
        if os.path.isdir(file_path):
            continue

        match = re.match(pattern, filename)

        # skip files that do not match the filename pattern
        if not match:
            continue

        # extract the steam app id from the image filename
        app_id = match.group(1)

        # test that this steam app name already been retrieved. If not, retrieve it
        if app_id not in app_names:
            app_names[app_id] = get_app_name(app_id)
            if app_names[app_id] is not None:
                # if the app name was properly retrieved, the file will have to be updated
                update_storage_file = True

        # check that the steam app id was properly retrieved. If not, skip to the next item in the directory
        if app_names[app_id] is None:
            continue

        # date_time = match.group(2)
        # shot_number = match.group(3)

        # build destination path for the image
        new_path = os.path.join(path, app_names[app_id], filename)

        try:
            # move the image
            os.renames(file_path, new_path)
            print 'successfully moved', filename
        except OSError:
            print 'there was an error moving', filename

    # if a new steam app name has been retrieved, save all of the app ID's and corresponding names to file
    if update_storage_file:
        print 'saving app names to file...'
        storage_file = open(storage_path, 'w')
        for key in app_names:
            storage_file.write(key + '  :|:  ' + app_names[key] + '\n')
        storage_file.close()


# remove empty directories under the given path
def clean_empty_directories(path):
    # expand the path from ~/ format
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
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=str, help='Location of the Steam screenshots directory.'
                                               ' If contains spaces, surround with double quotes')

    args = vars(parser.parse_args())

    organize_steam_screenshots(args['path'])
    print 'pruning steam screenshots folder for empty directories'
    clean_empty_directories(args['path'])
