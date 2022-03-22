import apiclient.discovery
import httplib2

from oauth2client.service_account import ServiceAccountCredentials
from xml.etree import ElementTree
from termcolor import colored


# ключи авторизации, id таблицы, файлы
CREDS_FILE = './creds.json' #файл ключа из google API
SHEET_ID = '1m9uq587LomH2L8Wid2Ym4K1BFz1azbHi4BT6tAxbEb8'
XML_FILE = '../test_dominigames/DominiIAP.xml'
PLIST_FILE = '../test_dominigames/Info.plist'

# чтение данных из таблицы 
def read_sheet(range: str) -> list: 
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDS_FILE,
    ['https://www.googleapis.com/auth/spreadsheets',
     'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)

    '''Read range fron google sheet\n
    range str(): "A1:B2"'''
    sheet_data = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=range,
        majorDimension='ROWS'
    ).execute()
    
    _dict = []
    for row in sheet_data['values'][1:]:
        _dict.append({
            'plist_key' : row[0],
            'plist_value' : row[1] if len(row) > 1 else '',
            'purchase' : row[2] if len(row) > 2 else '',
    })
    return _dict


def read_xml(file):
    tree = ElementTree.parse(file)
    root = tree.getroot()
    items = root[0].findall('item')

    xml_data = [] 
    for item in items:
        _dict = {}
        for tag in item:
            _dict.update({tag.tag: tag.text})
        xml_data.append(_dict)
    return xml_data


def read_plist(file):
    tree = ElementTree.parse(file)
    root = tree.getroot()
    dict_tag = root.find('dict')
    _list = []
    for i in range(0, len(root[0]), 2):
        _list.append((dict_tag[i].text, dict_tag[i+1].text))
    return _list

# разноцветные выводы, настраивать logger было лень
def print_green(msg):
    print(colored(msg, 'green'))

def print_red(msg):
    print(colored(msg, 'red'))

def print_blue(msg):
    print(colored(msg, 'blue'))

if __name__ == '__main__':
    sheet_data = read_sheet('A1:D100')
    xml_data = read_xml(XML_FILE)
    plist_data = read_plist(PLIST_FILE)


    for grow in sheet_data:
        grow_plist_key = grow.get('plist_key')
        grow_plist_value = grow.get('plist_value')
        grow_purchase = grow.get('purchase')
        for plist_row in plist_data:
            plist_key, plist_value = plist_row
            if grow_plist_key == plist_key:
                if grow_plist_value != plist_value:
                    print_red(f"ERROR: wrong key {grow_plist_key} in \
{PLIST_FILE.split('/')[-1]}. Correct key {grow_plist_value}")
                else:
                    print_green(f"INFO: {grow_plist_key} in {PLIST_FILE.split('/')[-1]} is correct.")
        if grow_purchase:
            for xml_row in xml_data:
                product_id = xml_row.get('ProductID')
                if grow_purchase == product_id:
                    print_green(f"INFO: {grow_purchase} in {XML_FILE.split('/')[-1]} is correct.")
                    break
            else:
                print_red(f"ERROR: {XML_FILE.split('/')[-1]} not include {grow_purchase}")
        else:
            print_blue(f"WARNING: Google sheet have no Purchase in row with PlistKey {grow_plist_key}")
    
