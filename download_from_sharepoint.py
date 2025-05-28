import sys

from Office365_api import SharePoint
import os
import re
from pathlib import PurePath

folder_name = sys.argv[1]
folder_dest = sys.argv[2]
file_name = sys.argv[3]
file_name_pattern = sys.argv[4]


def save_file(file_n, file_obj):
    file_dir_path = PurePath(folder_dest, file_n)
    with open(file_dir_path, 'wb') as f:
        f.write(file_obj)


def get_file(file_n, folder):
    file_obj = SharePoint().download_file(file_n, folder)
    save_file(file_n, file_obj)


def get_files(folder):
    files_list = SharePoint()._get_files_list(folder)
    for file in files_list:
        get_file(file.name, folder)


def get_files_by_pattern(keyword, folder):
    files_list = SharePoint()._get_files_list(folder)
    for file in files_list:
        if re.search(keyword, file.name):  # Corrigido: file.name em vez de file_name
            get_file(file.name, folder)


if __name__ == '__main__':
    if file_name != 'None':
        get_file(file_name, folder_name)
    elif file_name_pattern != 'None':
        get_files_by_pattern(file_name_pattern, folder_name)
    else:
        get_files(folder_name)
