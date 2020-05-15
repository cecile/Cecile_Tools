###############################################################
# Library: utils.py
# Description: Several common code
# Author: jamedina@gmail.com
# -------------------------------------------------------------
# Required Modules: lxml
###############################################################

import os
import logging
import re
import codecs
from os import walk
import requests
from lxml import html
from urllib.parse import urlparse
from urllib import request
import zipfile
import shutil
import stat
import subprocess
import shutil

# Log object
log = None


class AddonInfo:

    def __init__(self):

        self.log = logging.getLogger(self.__class__.__name__)

        self.name = self.GetAddonName()

        self.src_folder = os.path.abspath(os.path.join(os.pardir, "src"))

        self.main_addon = self.src_folder + os.sep + self.name

        self.toc = self.main_addon + os.sep + self.name + ".toc"

        self.version = self.GetAddonVersion()
        self.WowVersion = self.GetAddonWoWVersion()

        self.folders, self.files, self.main_folders = self.GetSources()

    def GetAddonName(self):
        addon_folder = os.path.abspath(os.pardir)

        parent_folder = os.path.abspath(os.path.join(addon_folder, os.pardir))

        addon_name = addon_folder.replace(parent_folder + os.sep, "")

        self.log .info("Addon is : '%s'", addon_name)

        return addon_name

    def GetAddonVersion(self):

        version = None
        reg_exp = re.compile(r'## Version..(.*)')

        with codecs.open(self.toc, encoding='utf-8') as input_file:
            for line in input_file.readlines():
                match = re.search(reg_exp, line)
                if not(match is None):
                    version = match.group(1)
                    version = version.replace("\r", "")
                    break

        self.log .info("Addon version is : '%s'", version)

        return version

    def GetAddonWoWVersion(self):

        WowVersion = None
        reg_exp = re.compile(r'## Interface..(.*)')

        with codecs.open(self.toc, encoding='utf-8') as input_file:
            for line in input_file.readlines():
                match = re.search(reg_exp, line)
                if not(match is None):
                    WowVersion = match.group(1)
                    WowVersion = WowVersion.replace("\r", "")
                    break

        self.log .info("Addon WoW version is : '%s'", WowVersion)

        return WowVersion

    def GetSources(self):

        self.log.info("reading src folder [%s]", self.src_folder)

        folders = []
        files = []
        main_folders = []

        for (dirpath, dirnames, filenames) in walk(self.src_folder):
            folders.append(dirpath)
            for filename in filenames:
                if not (dirpath == self.src_folder):
                    files.append(dirpath + os.sep + filename)

        for folder in folders:
            folder_partial = folder.replace(self.src_folder + os.sep, "")
            if(re.search(r"\\", folder_partial) is None):
                main_folders.append(folder)

        return folders, files, main_folders


def del_rw(action, name, exc):
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)


def del_tree(path):
    if os.path.exists(path):
        shutil.rmtree(path, onerror=del_rw)


def copy_tree(from_path, to_path):

    overwrite = False

    if os.path.exists(to_path):
        del_tree(to_path)
        overwrite = True

    shutil.copytree(from_path, to_path)

    return overwrite


def get_svn(url, folder):

    proc = subprocess.Popen(["svn", "checkout", url, folder],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            shell=True, universal_newlines=True)
    out, err = proc.communicate()
    exitcode = proc.returncode
    if not (exitcode == 0):
        raise Exception("Fail to get SVN :" + err.replace("\n", ""))
    del_tree(folder + os.sep + ".svn")


def get_git(url, folder):

    proc = subprocess.Popen(["git", "clone", url, folder],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            shell=True, universal_newlines=True)
    out, err = proc.communicate()
    exitcode = proc.returncode
    if not (exitcode == 0):
        raise Exception("Fail to get Git :" + err.replace("\n", ""))

    del_tree(folder + os.sep + ".git")


def download_file(url, file_path):
    myfile = requests.get(url, allow_redirects=True)
    open(file_path, 'wb').write(myfile.content)


def get_wowace(addon_url, folder):
    url = addon_url + "/files/latest"

    if not os.path.exists(folder):
        os.makedirs(folder)

    zip_file = folder + os.sep + "ace.zip"

    download_file(url, zip_file)

    with zipfile.ZipFile(zip_file, "r") as z:
        z.extractall(folder)

    os.remove(zip_file)
