import subprocess
import json
import threading
import tkinter as tk
from tkinter import font
import time
import random
import os

global auth_key, text_list
lock = threading.Lock()
data_list = ["Initial Item"]

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
    print(123)


def get_SSIDs():
    global auth_key, text_list

    with open('GetSSIDs.txt', 'r') as file:
        curl_command = file.read()
    curl_command = curl_command.replace('REPLACE', auth_key)
    result = subprocess.run(curl_command, shell=True, capture_output=True, text=True)
    # print(result)
    response_json = json.loads(result.stdout)
    print('----------------')
    # print(response_json)
    text_list = response_json['ssids'].strip().split('\n')
    return response_json

def update_data():
    global text_list
    get_SSIDs()
    new_item = f"Item {random.randint(100, 999)}"
    data_list.append(new_item)
    # data_list.append('1')
    listbox.delete(0, tk.END)
    for item in text_list:
        listbox.insert(tk.END, item, )
    listbox.yview_moveto(1.0)
    root.after(5000, update_data)


if __name__ == '__main__':
    print('wahh')
    global text_list
    text_list = []
    authenticate()
    print(321)
    # GUI setup
    root = tk.Tk()
    root.title("Dynamic List Update")

    root.geometry("600x400")  # optional: set initial size

    # Custom font
    big_font = font.Font(family="Helvetica", size=16)

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
