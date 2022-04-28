"""
Name: Time.py
Author: Thesacraft
description: showing how much time you have left when using a speedport(Telekom)
"""
import json
import class_Time

try:
    with open("config.json") as json_file:
        json_object = json.load(json_file)
        mode = json_object["logmode"]
except FileNotFoundError:
    mode = "INFO"
    pass

time = class_Time.Time(mode)
time.run()
time.mainloop()

