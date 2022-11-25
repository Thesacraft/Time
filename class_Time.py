"""
Name: class_Time.py
Author: https://www.github.com/Thesacraft
description: showing how much time you have left when using a speedport(Telekom)
"""
import json
import logging
import os.path
import subprocess
import sys
import webbrowser
from time import sleep

import selenium.common.exceptions
from infi.systray import SysTrayIcon
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


class Time():
    def __init__(self, rootLoggerloglevel):
        logging.basicConfig(filename="logfile-time.log", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=rootLoggerloglevel)
        logging.error("This programm is deprecated please use speedport_time instead!")
        if rootLoggerloglevel == "INFO":
            logging.info(self.formatCleanMsg(["Starting..."]))
        else:
            logging.debug(self.formatCleanMsg(["Starting...", f"loglevel={rootLoggerloglevel}"]))
        self.logmode, self.updatetime = self.loadConfig()
        self.defineVariables(self.logmode)
        self.setupLogging()
    def restart(self,handle = True):
        self.restarting = True
        self.kill()
    def run(self):
        self.running = True
        self.startSystray()
        self.start()

    def clearLog(self, handle):
        def my_function(ext):
            return text[::-1]

        self.logger.info("Clearing Logs...")
        with open("logfile-time.log", "r") as fh:
            text = fh.read()
            fh.close()
        text = my_function(str(text))
        text_left = text.split("#                      ...gnitratS#\n###################################")
        text = text_left[0] + "#                      ...gnitratS#\n###################################"
        text = my_function(text)
        with open("logfile-time.log", "w") as fh:
            fh.write(text)
            fh.close()

    # Variables
    def defineVariables(self, loglevel):
        self.restarting = False
        self.running = False
        self.destroyed = False
        self.loglevel = loglevel
        self.numeric_level = getattr(logging, self.loglevel.upper())
        self.menu_options = (
                                ("Updatetiming", None,
                              (("Update every minute", None, self.Updating1min),
                               ("Update every 2 minutes", None, self.Updating2min),
                               ("Update every 4 minutes", None, self.Updating4min),
                               )
                              ), (
                                 ("Logging", None, (
                                     ("Debug", None, self.debug),
                                     ("Info", None, self.info),
                                     ("Warning", None, self.warning),
                                 )
                                  )
                             ),
                             (
                                 "Restart", None,self.restart
                            ),
                             ("ClearLog", None, self.clearLog),
                             ("Author", None, self.openAuthorGithub),
                             )

        self.my_url: str = "http://speedport.ip/html/login/clienttime.html?lang=de#"

    def debug(self, handle):
        with open("config.json") as json_file:
            json_object = json.load(json_file)
            self.logger.info(f'Changing logmode from {json_object["logmode"]} to debug')
            json_object["logmode"] = "DEBUG"
            json_file.close()
        with open("config.json", "w") as json_file:
            json_file.write(json.dumps(json_object))
            json_file.close()
        self.restart()

    def info(self, handle):
        with open("config.json") as json_file:
            json_object = json.load(json_file)
            self.logger.info(f'Changing logmode from {json_object["logmode"]} to info')
            json_object["logmode"] = "INFO"
            json_file.close()
        with open("config.json", "w") as json_file:
            json_file.write(json.dumps(json_object))
            json_file.close()
        self.restart()

    def warning(self, handle):
        with open("config.json") as json_file:
            json_object = json.load(json_file)
            self.logger.info(f'Changing logmode from {json_object["logmode"]} to warning')
            json_object["logmode"] = "WARNING"
            json_file.close()
        with open("config.json", "w") as json_file:
            json_file.write(json.dumps(json_object))
            json_file.close()
        self.restart()

    # Update
    def sysUpdate(self):
        self.firefoxOpen()
        # Searching for the elements
        if (self.driver.current_url == "http://speedport.ip/html/login/clienttime.html?lang=de#"):
            self.driver.refresh()
            self.logger.debug("refreshed")
        self.driver.get(self.my_url)
        div_maxtime = self.driver.find_element_by_id('maxtimeNolimit')

        bt_yes_div = self.driver.find_element_by_id('timeruleTimeYes')

        element_verbleibende_zeit = self.driver.find_element_by_id('var_remainingtime')
        try:
            element_bis = self.driver.find_element_by_id('var_trule_to2')  # var_trule_to1
        except BaseException as err:
            self.logger.info(f"Unexpected {err=}, {type(err)=}")
            element_von = self.driver.find_element_by_id('var_trule_to1')  # var_trule_to1
        zeitpunkt = self.driver.find_element_by_id('var_time')  # var_time
        wait: float = 0.3
        sleep(wait)
        # converting htmlelements to valid variables

        self.verbleibende_zeit: float = element_verbleibende_zeit.text
        bis: float = element_bis.text
        lastupdate: float = zeitpunkt.text
        if (bt_yes_div.is_displayed()):
            moeglich = "Ja"
        else:
            moeglich = "Nein"

        # updating the systemtray
        if (not self.verbleibende_zeit == ""):
            if (int(self.verbleibende_zeit) > 60):
                self.verbleibende_zeit = int(self.verbleibende_zeit) / 60
                self.verbleibende_zeit = round(self.verbleibende_zeit * 10)
                self.verbleibende_zeit = self.verbleibende_zeit / 10
                self.systray.update("logo.ico",
                                    " Verbleibende Zeit: " + str(self.verbleibende_zeit) + " Stunden und bis " + str(
                                        bis) + " Uhr,\n Internet Verbindung möglich: {moeglich}\n zuletzt geupdatet: " + str(
                                        lastupdate) + " Uhr.")
            else:
                self.systray.update("logo.ico",
                                    " Verbleibende Zeit: " + str(self.verbleibende_zeit) + " Minuten und bis " + str(
                                        bis) + " Uhr,\n Internet Verbindung möglich: {moeglich}\n zuletzt geupdatet: " + str(
                                        lastupdate) + " Uhr.")
        else:
            self.verbleibende_zeit = "other"
            if (div_maxtime.is_enabled()):
                self.systray.update("logo.ico",
                                    f" Verbleibende Zeit: Unbeschränkt\n Internet Verbindung möglich: {moeglich}\n zuletzt geupdatet: " + str(
                                        lastupdate) + " Uhr.")
            else:
                self.systray.update("logo.ico",
                                    f" Verbleibende Zeit: Abgelaufen\n Internet Verbindung möglich: {moeglich}\n zuletzt geupdatet: " + str(
                                        lastupdate) + " Uhr.")
        self.systray.update()

    # Config Stuff
    def checkforConfig(self):
        if (not os.path.exists("config.json")):
            logging.warning("config.json doesn't exist. creating config.json!")
            with open("config.json", "w+") as config:
                config_values = {"updatetime": 60, "logmode": "INFO"}
                config.write(json.dumps(config_values))
                config.close()

    def loadConfig(self):
        self.checkforConfig()
        with open("config.json") as config:
            json_object = json.load(config)
            config.close()
        logging.info("Loading config")
        logging.debug(f"Config: {json_object}")
        return json_object["logmode"], json_object["updatetime"]

    def update_updatetime(self, time: int):
        with open("config.json") as json_file:
            json_object = json.load(json_file)
            json_file.close()
        self.logger.info(f'Changing updatime from {json_object["updatetime"]} to {time}')
        json_object["updatetime"] = time
        with open("config.json", "w+") as json_file:
            json_file.write(json.dumps(json_object))
            json_file.close()

    # selenium Stuff

    def start(self):
        self.options = Options()  # creating and specefing the options
        self.options.add_argument('--headless')  # creating and specefing the options
        self.driver = webdriver.Firefox(options=self.options)
        self.logger.info("Started")

    def firefoxOpen(self):
        try:
            url = self.driver.current_url
        except selenium.common.exceptions.WebDriverException as e:
            self.logger.exception("closed Firefox")
            self.start()

    # Logging Stuff
    def setupLogging(self):
        logging.debug(self.formatCleanMsg(["Starting...", f"Start arguments: {sys.argv}"]))
        self.logger = logging.getLogger("Time")
        self.logger.setLevel(self.loglevel.upper())
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(funcName)s - %(message)s')
        self.handler = logging.FileHandler(filename=f"logfile-time.log", encoding="utf-8")
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

    def formatCleanMsg(self, msgs: list):
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

    # systray stuff
    def startSystray(self):
        self.systray = SysTrayIcon("logo.ico", "Starting...", self.menu_options, on_quit=self.on_quit_callback)
        self.systray.start()

    def on_quit_callback(self, systray):
        self.destroyed = None
        self.driver.quit()

    def openAuthorGithub(self, handle):
        webbrowser.open("https://www.github.com/Thesacraft")

    def Updating1min(self, handle):
        self.update_updatetime(60)

    def Updating2min(self, handle):
        self.update_updatetime(120)

    def Updating4min(self, handle):
        self.update_updatetime(240)

    # Maths Stuff
    def updatetiming(self, time):
        update = round(time / 5)
        return update

    # General
    def mainloop(self):
        while self.running:
            self.sysUpdate()
            self.logger.debug(f"waiting for {self.updatetime}s than repeating")
            for x in range(self.updatetiming(self.updatetime)):
                if self.verbleibende_zeit != " " and self.verbleibende_zeit != "" and self.verbleibende_zeit != None and self.running:
                    if not self.running:
                        exit()
                    if self.destroyed == None and not self.running:

                        if self.numeric_level == 10:
                            sleep(0.2)
                            self.logger.debug(
                                self.formatCleanMsg(
                                    [f"Exiting...", "Because of the exiting button on the Gui no Error caused it!"]))
                        else:
                            self.logger.info(self.formatCleanMsg(["Exiting..."]))
                        exit()
                        break
                    else:
                        sleep(5)
                else:
                    self.driver.close()
                    if not self.restarting:
                        self.logger.info(self.formatCleanMsg([f"Something went wrong","Exiting..."]))
                    else:
                        self.logger.info(self.formatCleanMsg(["Restarting..."]))
                        self.systray.shutdown()
                        os.startfile("start.bat")
                    exit()
        if self.restarting:
            self.systray.shutdown()
            self.logger.info(self.formatCleanMsg(["Restarting..."]))
            os.startfile("start.bat")
        exit()

    def kill(self):
        self.running = False
