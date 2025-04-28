import time
import subprocess
import json
import os
import vlc
import re
import threading
import datetime
from datetime import datetime
from zoneinfo import ZoneInfo

RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
WHITE = '\033[37m'
RESET = '\033[0m'

class SSIDObject:
    def __init__(self, id, first_seen):
        self.id = id
        self.first_seen = first_seen

    def print_time(self, censored = True, color = BLUE):
        est_zone = ZoneInfo("America/New_York")
        dt_est = datetime.fromtimestamp(int(float(self.first_seen)), tz=est_zone)
        human_readable = dt_est.strftime("%Y-%m-%d %H:%M:%S %Z%z")
        if censored:
            print(f'{color}',censor_word(self.id),"first seen:", human_readable, f'{RESET}')

            # print(f"{RED}This text is red.{RESET}")
        else:
            print(f'{color}',self.id,"first seen:", human_readable, f'{RESET}')

global auth_key, text_list, SSID_count, bad_words
lock = threading.Lock()
data_list = []
start_time = time.time()

def censor_word(word):
    global bad_words
    pat = re.compile("|".join(re.escape(w) for w in bad_words), flags=re.I)
    temp = pat.sub(lambda g: "*" * len(g.group(0)), word)
    return temp

def authenticate():
    global auth_key

    with open('GetTokenCurl.txt', 'r') as file:
        curl_command = file.read()
    curl_command = curl_command.replace('REPLACE', os.environ['pass'])

    result = subprocess.run(curl_command, shell=True, capture_output=True, text=True)
    response_json = json.loads(result.stdout)
    auth_key = response_json.get('token')


def update_archived_list(unclean_input):
    global text_list
    existing_ssids = []
    if text_list is None:
        return
    for item in text_list:
        existing_ssids.append(item.id)

    for candidate in unclean_input:
        if candidate not in existing_ssids:
            print('New entry!')
            seconds = time.time()
            new_ssid = SSIDObject(id = candidate, first_seen = seconds)
            new_ssid.print_time(color=RED)
            text_list.append(new_ssid)


def get_SSIDs():
    global auth_key, text_list, SSID_count

    with open('GetSSIDs.txt', 'r') as input_file:
        curl_command = input_file.read()
        curl_command = curl_command.replace('REPLACE', auth_key)
        result = subprocess.run(curl_command, shell=True, capture_output=True, text=True)
        response_json = json.loads(result.stdout)

        response_ssids = response_json['ssids'].strip().split('\n')
        if len(response_ssids[0]) > 1:
            update_archived_list(response_ssids)

        if len(text_list) > SSID_count:
            player = vlc.MediaPlayer("greencouch.wav")
            player.play()
            save_ssids()
        SSID_count = len(text_list)


def save_ssids():
    print(f"{WHITE}Saving...{RESET}")
    with open('time_logs/' + str(int(start_time)) + ".txt", "w") as output_file:
        for item in text_list:
            output_file.write(f"{item.id},{item.first_seen}\n")
    with open('time_logs/recent.txt', "w") as output_file:
        for item in text_list:
            output_file.write(f"{item.id},{str(item.first_seen).strip()}\n")

def load_existing_ssids():
    global text_list, SSID_count
    try:
        with open('time_logs/recent.txt', 'r') as input_file:
            lines = input_file.readlines()
            for line in lines:
                if ',' in line:
                    line = line.split(',')
                    text_list.append(SSIDObject(line[0], line[1]))
    except:
        print('No recent.txt')
    SSID_count = len(text_list)
    for item in text_list:
        item.print_time()

def load_bad_words():
    global bad_words
    try:
        with open('BadWords.txt', 'r') as file:
            bad_words = file.read()
        bad_words = bad_words.strip().split('\n')
    except:
        print('Bad words not loaded, does BadWords.txt exist?')
        bad_words = []


if __name__ == '__main__':
    global text_list, SSID_count
    SSID_count = 0
    text_list = []

    authenticate()
    load_bad_words()
    load_existing_ssids()

    while True:
        get_SSIDs()
        time.sleep(1)
