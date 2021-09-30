
"""
Name: timer.py
Author: Thesacraft
Version: 1.0
lastchange: 30.09.2021
description: showing how much time you have left when using a speedport(Telekom)
"""




#Importing
from selenium import webdriver
from time import sleep
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

#Quitting the programm correctly
def on_quit_callback(systray):
    global destroyed
    destroyed = None

#creating the systemtray and starting it
systray = SysTrayIcon("logo.ico", "verbleibende zeit: ", on_quit=on_quit_callback)
systray.start()

#creating a loop to update the systemtray
while True:
    #opening the driver
    options = Options()                 #creating and specefing the options
    options.add_argument('--headless')  #creating and specefing the options
    
    my_url: str = "http://speedport.ip/html/login/clienttime.html?lang=de#"
    driver = webdriver.Firefox(options=options)
    driver.get(my_url)

    #Searching for the elements
    p_element = driver.find_element_by_id('var_remainingtime')
    p_element2 = driver.find_element_by_id('var_trule_to1') #var_trule_to1
    p_element3 = driver.find_element_by_id('var_time') #var_time
    wait: float = 0.3
    sleep(wait)

    #converting htmlelements to valid variables
    vb: float = p_element.text
    bis: float = p_element2.text
    lastupdate: float = p_element3.text
    
    #updating the systemtray
    if(int(vb)>60):
        vb=int(vb)/60
        vb=round(vb*10)
        vb=vb/10
        systray.update("logo.ico", " Verbleibende Zeit: " + str(vb) + " Stunden und bis " + str(bis) + " Uhr,\n zuletzt geupdatet: " + str(lastupdate) + " Uhr.")
    else:
        systray.update("logo.ico", " Verbleibende Zeit: " + str(vb) + " Minuten und bis " + str(bis) + " Uhr,\n zuletzt geupdatet: " + str(lastupdate) + " Uhr.")

    #closing the driver
    driver.close()
    os.system('tskill plugin-container')
    driver.quit()
    systray.update()

    #waiting to the next update and checking if the systemtray was closed during the sleeping
    for x in range(24):
        if vb != " ":
            if destroyed == None:
                os.system('taskkill /IM Python')
                exit()
                break
            else:
                sleep(5)
        else:
            pass
            
        
        
