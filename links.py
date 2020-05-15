################################################################
# Program: links.py
# Description: Create ntfs links from the addon into WOW
# Author: jamedina@gmail.com
# -------------------------------------------------------------
# Required Modules: win32com.shell
###############################################################

# -------------------------------------------------------------
# ACTUAL CODE BELLOW, DO NOT EDIT
# -------------------------------------------------------------

# system imports
from win32com.shell import shell
import os
import subprocess
import logging
import sys
import re

from utils import AddonInfo

# Log object
log = None


def GetKeyValue(key, value, default):
    result = default
    proc = subprocess.Popen(["REG", "QUERY", key, "/V", value],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            shell=True, universal_newlines=True)
    out, err = proc.communicate()
    exitcode = proc.returncode

    if exitcode == 0:
        p = re.compile(r".*REG_SZ\s*(.*)")
        for line in out.splitlines():
            test_str = line
            found = re.search(p, test_str)
            if not(found is None):
                result = found.group(1)

    log.info("Key: %s, Value: %s = [%s]", key, value, result)

    return result


def GetWOWPath(beta):

    default = "KEY_NOT_FOUND"
    base = "HKLM\\SOFTWARE\\WOW6432Node\\"

    if beta:
        log.info("Create symslink for WoW Beta")        
        key = base + "Blizzard Entertainment\\World of Warcraft\\Beta\\"
    else:
        log.info("Create symslink for WoW Retail")
        key = base + "Blizzard Entertainment\\World of Warcraft"

    WOWPath = GetKeyValue(key, "InstallPath", default)

    log.info("WOW Path : '%s'", WOWPath)

    return WOWPath


def BetaPath():
    return GetWOWPath(True)


def RetailPath():
    return GetWOWPath(False)


def CreateSysLink(original, destination):
    proc = subprocess.Popen(["MKLINK", "/d", destination, original],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            shell=True, universal_newlines=True)
    out, err = proc.communicate()
    exitcode = proc.returncode
    if not (exitcode == 0):
        log.warning("Fail to create sys link : %s", err.replace("\n", ""))


def CreteLinks(WOWPath, addon):

    if os.path.exists(WOWPath):
        interface_folder = os.path.join(WOWPath, "interface")
        addons_folder = os.path.join(interface_folder, "addons")

        for folder in addon.main_folders:
            desired_folder = folder.replace(addon.src_folder + os.sep, "")
            new_folder = os.path.join(addons_folder, desired_folder)
            log.info("Creating syslink for: '%s'", desired_folder)
            CreateSysLink(folder, new_folder)
    else:
        log.warning("WoW folder: [%s] does not exist", WOWPath)

if __name__ == '__main__':

    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    log = logging.getLogger(__name__)

    try:

        if not shell.IsUserAnAdmin():
            raise Exception("This script require admin privileges")

        addon = AddonInfo()

        CreteLinks(RetailPath(), addon)
        CreteLinks(BetaPath(), addon)

    except Exception as ex:
        logging.error(ex, exc_info=True)
        raise ex
