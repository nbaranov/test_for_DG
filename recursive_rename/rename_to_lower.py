#!/usr/bin/python3
import os 

from argparse import ArgumentParser
from chardet import detect
from pynvim import encoding
from termcolor import colored


# Get ariguments Folder name, and level of recurcion 
def get_args():
    parser = ArgumentParser()
    parser.add_argument(
        "-f", "--folder", 
        dest="folder", 
        help="write name of start folder",
        metavar="folder_name",
        required=True
    )
    parser.add_argument(
        "-r", "--recurcive", 
        dest="rl",
        metavar='Recurcive level', 
        default=0,
        help="write recurcive level, default: 0 - only current folder"
    )
    return parser.parse_args()


def get_encoding_type(file):
    '''get file encoding type from first 5Kb of file'''
    with open(file, 'rb') as f:
        rawdata = f.read(5120)
    return detect(rawdata)['encoding']


def read_in_chunks(file_object, chunk_size=1024):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data

def rename(old_name, new_name):
    if old_name != new_name:
        os.renames(old_name, new_name)
        print_blue(f'{old_name}  -----> {new_name}')
    else: 
        print_green(f'{old_name}  ----- dont\'t need to rename')


def scan_and_rename(folder, r_limit, r_level = 1):
    """
    folder - start folder name, str()\n
    r_limit - max level of recurcion, int()\n
    r_level - current level of recurcion, int() \n 
    """
    with os.scandir(folder) as ls:
        for entry in ls:
            old_name = f"{folder}/{entry.name}"
            new_name = f"{folder}/{str(entry.name).lower()}"
            # run recurce 
            if entry.is_dir() and r_level < r_limit:
                rename(old_name, new_name)
                scan_and_rename(new_name, r_limit, r_level + 1)               
            # rename dir
            elif entry.is_dir():
                rename(old_name, new_name)
            # recode file
            elif entry.is_file():
                encoding_type = get_encoding_type(entry)
                if encoding_type == 'utf-8':
                    print_green(f"{entry.name}, already utf-8")
                    continue
                print_blue(f"{entry.name} of {encoding_type} encoding to utf-8")
                with open(old_name, 'r', encoding=encoding_type) as in_file, \
                     open('template', 'w', encoding='utf-8') as outfile:
                    for piece in read_in_chunks(in_file):
                        outfile.write(piece)
                    os.remove(old_name)
                    os.rename('template', new_name)
                    print_green(f'Encoded {old_name} of {encoding_type} ----> {new_name} of utf-8')


# скопировал разноцветные выводы из второго задания
def print_green(msg):
    print(colored(msg, 'green'))

def print_blue(msg):
    print(colored(msg, 'blue'))


if __name__ == '__main__':
    args = get_args()
    folder = str(args.folder).rstrip('/')
    rl = int(args.rl)

    rename(folder, folder.lower())
    if rl:
        scan_and_rename(folder.lower(), rl)
