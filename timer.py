"""
Name: timer.py
Author: Thesacraft
Version: 1.0
lastchange: 27.04.2022
description: showing how much time you have left when using a speedport(Telekom)
"""

import json
import logging
import os.path
import sys
import webbrowser
from time import sleep

# from selenium.webdriver.support.wait import WebDriverWait
import selenium.common.exceptions
from infi.systray import SysTrayIcon
# Importing
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

# defining variables


global destroyed
destroyed: int = 1
global systray
global menu_options
global say_hello

# config
if (not os.path.exists("config.json")):
    logging.info("Creating config.json")
    with open("config.json", "w+") as config:
        config_values = {"updatetime": 60, "debugmode": "INFO"}
        config.write(json.dumps(config_values))
        config.close()


def configUpdate():
    with open("config.json") as config:
        json_object = json.load(config)
        config.close()
    return json_object["updatetime"]


def configLoad():
    with open("config.json") as config:
        json_object = json.load(config)
        config.close()
    return json_object["debugmode"], json_object["updatetime"]


numeric_level = None
[loglevel, updatetime] = configLoad()
numeric_level = getattr(logging, loglevel.upper(), None)
# setting up logging
if (len(sys.argv) > 1):
    if "--log=" in sys.argv[1]:
        loglevel = sys.argv[1]
        loglevel = loglevel.replace("--log=", "")
        numeric_level = getattr(logging, loglevel.upper(), None)

if (numeric_level != None):
    logging.basicConfig(filename="logfile-timer.log", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=loglevel.upper())
else:
    logging.basicConfig(filename="logfile-timer.log", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
    numeric_level = 20


def formatCleanMsg(msgs: list):
    standardlength = 35
    lengths = []
    if (len(msgs) == 0):
        return ValueError
    for i in msgs:
        lengths.append(len(i) + 2)
    lengths.sort(reverse=True)
    spaces = []
    length = lengths[0]
    if (length < standardlength):
        finallength = standardlength

    else:
        finallength = length + 2
    for i in msgs:
        space = (finallength - len(i)) - 2
        spaces.append(space)
    cleanMsg = ""
    cleanMsg += "\n\n" + finallength * "#" + "\n"
    for i in range(len(msgs)):
        cleanMsg += f"#{msgs[i]}" + spaces[i] * " " + "#\n"
    cleanMsg += finallength * "#" + "\n"
    return cleanMsg


if numeric_level <= 10:
    logging.debug(formatCleanMsg(["Starting...", f"Start arguments: {sys.argv}"]))
else:
    logging.info(formatCleanMsg(["Starting..."]))


def update_updatetime(time: int):
    with open("config.json") as json_file:
        json_object = json.load(json_file)
        json_file.close()
    logging.debug(f'Changing updatime from {json_object["updatetime"]} to {time}')
    json_object["updatetime"] = time
    with open("config.json", "w+") as json_file:
        json_file.write(json.dumps(json_object))
        json_file.close()


def openAuthorGithub(self):
    webbrowser.open("https://www.github.com/Thesacraft")


def Updating1min(self):
    update_updatetime(60)


def Updating2min(self):
    update_updatetime(120)


def Updating4min(self):
    update_updatetime(240)


# Quitting the programm correctly
def on_quit_callback(systray):
    global destroyed
    destroyed = None
    driver.quit()


# creating the systemtray and starting it
menu_options = (("Updatetiming", None,
                 (("Update every minute", None, Updating1min),
                  ("Update every 2 minutes", None, Updating2min),
                  ("Update every 4 minutes", None, Updating4min),
                  )
                 ),
                ("Author", None, openAuthorGithub),
                )
systray = SysTrayIcon("logo.ico", "Starting...", menu_options, on_quit=on_quit_callback)
systray.start()
options = Options()  # creating and specefing the options
options.add_argument('--headless')  # creating and specefing the options


def updatetiming(time):
    update = round(time / 5)
    return update


driver = webdriver.Firefox(options=options)
# creating a loop to update the systemtray
while True:
    updatetime = configUpdate()
    vb = ""
    # opening the driver
    try:
        url = driver.current_url
    except selenium.common.exceptions.WebDriverException as e:
        logging.exception("closed Firefox")
        driver = webdriver.Firefox(options=options)
    my_url: str = "http://speedport.ip/html/login/clienttime.html?lang=de#"
    if (driver.current_url == "http://speedport.ip/html/login/clienttime.html?lang=de#"):
        driver.refresh()
        logging.warning("refreshed")
    driver.get(my_url)

    # Searching for the elements
    div_maxtime = driver.find_element_by_id('maxtimeNolimit')

    bt_yes_div = driver.find_element_by_id('timeruleTimeYes')

    p_element = driver.find_element_by_id('var_remainingtime')
    try:
        p_element2 = driver.find_element_by_id('var_trule_to2')  # var_trule_to1
    except BaseException as err:
        logging.info(f"Unexpected {err=}, {type(err)=}")
        p_element2 = driver.find_element_by_id('var_trule_to1')  # var_trule_to1
    p_element3 = driver.find_element_by_id('var_time')  # var_time
    wait: float = 0.3
    sleep(wait)
    # converting htmlelements to valid variables

    vb: float = p_element.text
    bis: float = p_element2.text
    lastupdate: float = p_element3.text
    if (bt_yes_div.is_displayed()):
        moeglich = "Ja"
    else:
        moeglich = "Nein"

    # updating the systemtray
    if (not vb == ""):
        if (int(vb) > 60):
            vb = int(vb) / 60
            vb = round(vb * 10)
            vb = vb / 10
            systray.update("logo.ico", " Verbleibende Zeit: " + str(vb) + " Stunden und bis " + str(
                bis) + " Uhr,\n Internet Verbindung möglich: {moeglich}\n zuletzt geupdatet: " + str(
                lastupdate) + " Uhr.")
        else:
            systray.update("logo.ico", " Verbleibende Zeit: " + str(vb) + " Minuten und bis " + str(
                bis) + " Uhr,\n Internet Verbindung möglich: {moeglich}\n zuletzt geupdatet: " + str(
                lastupdate) + " Uhr.")
    else:
        vb = "other"
        if (div_maxtime.is_enabled()):
            systray.update("logo.ico",
                           f" Verbleibende Zeit: Unbeschränkt\n Internet Verbindung möglich: {moeglich}\n zuletzt geupdatet: " + str(
                               lastupdate) + " Uhr.")
        else:
            systray.update("logo.ico",
                           f" Verbleibende Zeit: Abgelaufen\n Internet Verbindung möglich: {moeglich}\n zuletzt geupdatet: " + str(
                               lastupdate) + " Uhr.")
    systray.update()
    logging.debug("looping")
    # waiting to the next update and checking if the systemtray was closed during the sleeping
    for x in range(updatetiming(updatetime)):
        if vb != " " and vb != "" and vb != None:
            if destroyed == None:
                if numeric_level == 10:
                    sleep(0.2)
                    logging.debug(
                        formatCleanMsg([f"Exiting...", "Because of the exiting button on the Gui no Error caused it!"]))
                else:
                    logging.info(formatCleanMsg(["Exiting..."]))
                exit()
                break
            else:
                sleep(5)
        else:
            logging.info(f"Something went wrong")
            logging.debug(f"Vb is empty when it shouldn't be that means it couldn't read the page properly")
