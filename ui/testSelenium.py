#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  2 23:30:44 2021

@author: eugene
"""

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
import datetime as dt
import pandas as pd

# Opening the connection and grabbing the page
my_url = 'https://www.google.com/webhp?hl=en'
my_url= 'https://www.google.com/search?q=euro+dollars&hl=en&source=hp&ei=KfOoYaayIsKVseMPu4qw4A8&iflsig=ALs-wAMAAAAAYakBOZyprc6rMjqlCJ9-f0y-ppzJ_sIx&ved=0ahUKEwjm6vPCw8X0AhXCSmwGHTsFDPwQ4dUDCAk&uact=5&oq=euro+dollars&gs_lcp=Cgdnd3Mtd2l6EAMyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQyBwgAEIAEEAoyBQgAEIAEMgUIABCABDIFCAAQgAQ6CwguEIAEELEDEIMBOgsIABCABBCxAxCDAToICC4QgAQQsQM6CAgAELEDEIMBOgsILhCxAxDHARCvAToICC4QsQMQgwE6CAgAEIAEELEDOg4ILhCABBCxAxDHARCjAjoNCAAQgAQQsQMQRhCCAjoKCAAQgAQQRhCCAjoHCAAQsQMQCjoKCAAQsQMQgwEQCjoFCC4QgAQ6CwguEIAEEMcBEK8BUABYjRZgxRdoAHAAeACAAUGIAd8EkgECMTKYAQCgAQE&sclient=gws-wiz'
options = Options()
options.headless = False
driver = webdriver.Chrome(executable_path="chromedriver_linux64/chromedriver", options=options)
driver.get(my_url)
driver.maximize_window()


action = webdriver.ActionChains(driver)
print("searching")
search_bar = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[3]/form/div[2]/div[1]/div[1]/div/div[2]/input')))
         
print("searched")
search_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[3]/form/div[2]/div[1]/div[3]/center/input[1]')))
print("searched")
search_bar.send_keys('dollar euro')
search_button.click()