from winreg import *
import sys
import os

class FileDetectionModule():

    def find_steam_installs(self):
        found_install = ""

        try:
            hkey = OpenKey(HKEY_LOCAL_MACHINE, "SOFTWARE\WOW6432Node\Valve\Steam")
        except:
            hkey = None
            print(sys.exc_info())

        try:
            steam_path = QueryValueEx(hkey, "InstallPath")
        except:
            steam_path = None
            print(sys.exc_info())

        steam_path = os.path.join(steam_path[0], "steamapps", "common")

        for item in os.listdir(steam_path):
            if item == "Skyrim Special Edition":
                found_install = os.path.join(steam_path, item)
            elif item == "Skyrim":
                found_install = os.path.join(steam_path, item)

        return found_install
    
    def find_mo_appdata(self):
        local_app_data = os.getenv('LOCALAPPDATA')
        local_list = os.listdir(local_app_data)
        local_path = ""

        for i in local_list:
            if i == "ModOrganizer":
                local_path = os.path.join(local_app_data, i)

        return local_path

    def find_saves(self):
        home = os.path.expanduser("~")
        saves_path = os.path.join(home, "Documents", "My Games")
        found_saves = ""

        for item in os.listdir(saves_path):
            if item == "Skyrim Special Edition":
                found_saves = os.path.join(saves_path, item, "Saves")

        return found_saves
    
    def find_all(self):
        paths = {}

        paths["save"] = self.find_saves()
        paths["mo_local"] = self.find_mo_appdata()
        paths["steam"] = self.find_steam_installs()
        paths["mo"] = ""
        
        return paths