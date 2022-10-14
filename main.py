# Explorateur de fichiers
from tkinter import *
from tkinter.filedialog import askopenfilename
# Selenium / Webdriver
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
# Autres
from rich.progress import track
from rich.console import Console
import getpass
from time import sleep
import re
import pandas as pd
from collections import defaultdict
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import cv2
import os
import PIL.Image
import dlib
from imutils import face_utils
import argparse
from pathlib import Path
import ntpath


console = Console()

#Import our different components
import functions.easy_facial_recognition as efr
import functions.Code_scraping as csr


#Parsing known_faces file
parser = argparse.ArgumentParser(description='Easy Facial Recognition App')
parser.add_argument('-i', '--input', type=str, required=True, help='directory of input known faces')

#Running the code 
def run():
    efr.execution_recognition()
    csr.execution_code_sraping()
run()