import subprocess
import json
import threading
import tkinter as tk
from tkinter import font
import time
import random
import os
import vlc
import re

global auth_key, text_list, SSID_count, bad_words
lock = threading.Lock()
data_list = ['']



def censor_word(word):
    global bad_words
    print(word)
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
    print(response_json)
    auth_key = response_json.get('token')
    print('Your auth token is: ' + auth_key)

def clean_list(list):
    new_list = []
    for item in list:
        check = 1
        for bad_word in bad_words:
            if bad_word in item:
                temp = censor_word(item)
                check = 0
                new_list.append(temp)
                break
        if check == 1:
            new_list.append(item)
    return new_list



def get_SSIDs():
    global auth_key, text_list, SSID_count

    with open('GetSSIDs.txt', 'r') as file:
        curl_command = file.read()
    curl_command = curl_command.replace('REPLACE', auth_key)
    result = subprocess.run(curl_command, shell=True, capture_output=True, text=True)
    # print(result)
    response_json = json.loads(result.stdout)
    print('--List Updating--')
    # print(response_json)
    unclean_text_list = response_json['ssids'].strip().split('\n')

    clean_text_list = clean_list(unclean_text_list)
    # print('Clean list: ' + str(clean_text_list))
    text_list = clean_text_list
    if len(text_list) > SSID_count:
        player = vlc.MediaPlayer("tuturu_1.mp3")
        player.play()
    SSID_count = len(text_list)

def update_data():
    global text_list
    get_SSIDs()
    new_item = f"Item {random.randint(100, 999)}"
    data_list.append(new_item)
    listbox.delete(0, tk.END)
    for item in text_list:
        listbox.insert(tk.END, item, )
    listbox.yview_moveto(1.0)
    root.after(200, update_data)


if __name__ == '__main__':
    global text_list, SSID_count, bad_words
    SSID_count = 0
    text_list = []
    authenticate()

    with open('BadWords.txt', 'r') as file:
        bad_words = file.read()
    bad_words = bad_words.strip().split('\n')

    # GUI setup
    root = tk.Tk()
    root.title("SSIDs")

    root.geometry("600x400")  # optional: set initial size

    # Custom font
    big_font = font.Font(family="Helvetica", size=30)

    # Grid layout
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    frame = tk.Frame(root)
    frame.grid(row=0, column=0, sticky="nsew")
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    scrollbar = tk.Scrollbar(frame)
    scrollbar.grid(row=0, column=1, sticky="ns")

    listbox = tk.Listbox(frame, font=big_font, yscrollcommand=scrollbar.set)
    listbox.grid(row=0, column=0, sticky="nsew")

    scrollbar.config(command=listbox.yview)

    listbox.insert(tk.END, data_list[0])

    # Start the update cycle
    update_data()

    # Start GUI loop
    root.mainloop()
