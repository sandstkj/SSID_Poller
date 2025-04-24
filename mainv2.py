from tkinter import ttk
import time
import subprocess
import json
import tkinter as tk
import os
import vlc
import re
import threading

global auth_key, text_list, SSID_count, bad_words
lock = threading.Lock()
data_list = ['']
start_time = time.time()
print('The time is: ' + str(int(start_time)))

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


def clean_list(input_list):
    new_list = []
    for item in input_list:
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
        response_json = json.loads(result.stdout)
        unclean_text_list = response_json['ssids'].strip().split('\n')

        clean_text_list = clean_list(unclean_text_list)
        text_list = clean_text_list
        if len(text_list) > SSID_count:
            player = vlc.MediaPlayer("tuturu_1.mp3")
            player.play()
        SSID_count = len(text_list)

# COLORS = ['red', 'green', 'blue', 'purple', 'orange', 'brown', 'magenta', 'cyan', 'black']

def update_gui():
    global text_list
    previous_list = text_list
    get_SSIDs()
    for widget in content_frame.winfo_children():
        widget.destroy()

    for line in text_list:
        if line in previous_list:
            label = tk.Label(content_frame, text=line, fg='black', font=("Arial", 14), anchor="w")
            label.pack(fill="x")
        else:
            label = tk.Label(content_frame, text=line, fg='green', font=("Arial", 14), anchor="w")
            label.pack(fill="x")

    root.after(1000, update_gui)

def save_ssids():
    while True:
        with open('time_logs/' + str(int(start_time)) + ".txt", "w") as file:
            for item in text_list:
                file.write(f"{item}\n")
        time.sleep(10)


if __name__ == '__main__':
    global text_list, SSID_count, bad_words
    SSID_count = 0
    text_list = []
    authenticate()

    with open('BadWords.txt', 'r') as file:
        bad_words = file.read()
    bad_words = bad_words.strip().split('\n')

    root = tk.Tk()
    root.title("SSIDs")

    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    canvas = tk.Canvas(root)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    content_frame = scrollable_frame

    # threading.Thread(target=get_SSIDs(), daemon=True).start()
    update_gui()

    t = threading.Thread(target=save_ssids, daemon=True)
    t.start()

    # Keep the main program alive to allow daemon thread to run
    # while True:
    #     time.sleep(1)

    root.mainloop()
