
"""
Name: timer.py
Author: Thesacraft
Version: 1.0
lastchange: 27.04.2022
description: showing how much time you have left when using a speedport(Telekom)
"""




#Importing
from selenium import webdriver
import logging
from time import sleep
import sys
from selenium.webdriver.firefox.options import Options
#from selenium.webdriver.support.wait import WebDriverWait
import os
from infi.systray import SysTrayIcon

#defining variables


global destroyed
destroyed: int = 1
global systray
global menu_options
global say_hello

#setting up logging
if(len(sys.argv)>1):
    loglevel = sys.argv[1]
    if "--log=" in loglevel:
        loglevel = loglevel.replace("--log=","")
        numeric_level = getattr(logging,loglevel.upper(),None)
if(numeric_level!= None):
    logging.basicConfig(filename="logfile-timer.log", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%m/%d/%Y %I:%M:%S %p', level=loglevel)
else:
    logging.basicConfig(filename="logfile-timer.log", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
logging.debug(f"Start arguments: {sys.argv}")
logging.info(f"Starting...")
#Quitting the programm correctly
def on_quit_callback(systray):
    global destroyed
    destroyed = None
    logging.info(f"exiting...")

#creating the systemtray and starting it
systray = SysTrayIcon("logo.ico", "verbleibende zeit: ", on_quit=on_quit_callback)
systray.start()

#creating a loop to update the systemtray
while True:
    vb = ""
    #opening the driver
    options = Options()                 #creating and specefing the options
    options.add_argument('--headless')  #creating and specefing the options
    
    my_url: str = "http://speedport.ip/html/login/clienttime.html?lang=de#"
    driver = webdriver.Firefox(options=options)
    driver.get(my_url)

    #Searching for the elements
    div_maxtime = driver.find_element_by_id('maxtimeNolimit')

    bt_yes_div = driver.find_element_by_id('timeruleTimeYes')

    p_element = driver.find_element_by_id('var_remainingtime')
    try:
        p_element2 = driver.find_element_by_id('var_trule_to2')  # var_trule_to1
    except BaseException as err:
        logging.info(f"Unexpected {err=}, {type(err)=}")
        p_element2 = driver.find_element_by_id('var_trule_to1') #var_trule_to1
    p_element3 = driver.find_element_by_id('var_time') #var_time
    wait: float = 0.3
    sleep(wait)
    #converting htmlelements to valid variables

    vb: float = p_element.text
    bis: float = p_element2.text
    lastupdate: float = p_element3.text
    if(bt_yes_div.is_displayed()):
        moeglich="Ja"
    else:
        moeglich="Nein"

    #updating the systemtray
    if(not vb == ""):
        if(int(vb)>60):
            vb=int(vb)/60
            vb=round(vb*10)
            vb=vb/10
            systray.update("logo.ico", " Verbleibende Zeit: " + str(vb) + " Stunden und bis " + str(bis) + " Uhr,\n Internet Verbindung möglich: {moeglich}\n zuletzt geupdatet: " + str(lastupdate) + " Uhr.")
        else:
            systray.update("logo.ico", " Verbleibende Zeit: " + str(vb) + " Minuten und bis " + str(bis) + " Uhr,\n Internet Verbindung möglich: {moeglich}\n zuletzt geupdatet: " + str(lastupdate) + " Uhr.")
    else:
        vb = "other"
        if (div_maxtime.is_enabled()):
            systray.update("logo.ico", f" Verbleibende Zeit: Unbeschränkt\n Internet Verbindung möglich: {moeglich}\n zuletzt geupdatet: " + str(lastupdate) + " Uhr.")
        else:
            systray.update("logo.ico",f" Verbleibende Zeit: Abgelaufen\n Internet Verbindung möglich: {moeglich}\n zuletzt geupdatet: " + str(lastupdate) + " Uhr.")
    #closing the driver
    driver.close()
    #driver.quit()
    systray.update()
    logging.debug("looping")

    #waiting to the next update and checking if the systemtray was closed during the sleeping
    for x in range(24):
        if vb != " " and vb != "" and vb != None:
            if destroyed == None:
                logging.info("exiting...")
                logging.debug(f"because of the exiting button on the Gui no Error caused it!")
                exit()
                break
            else:
                sleep(5)
        else:
            logging.info(f"something went wrong")
            logging.debug(f"vb is empty when it shouldnt be that means it couldn't read the page properly")
        
