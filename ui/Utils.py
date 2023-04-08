#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 27 13:03:20 2021

@author: eugene
"""
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time
import numpy as np
from pyotp import *
# import msvcrt
import logging
import sys
import pickle
import os

def string2Float(x):
    x = x.split(" ")[1]
    x= x.replace(',', '')
    return float(x)

def save_cookie(driver, path):
    with open(path, 'wb') as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)

def load_cookie(driver, path):
     with open(path, 'rb') as cookiesfile:
         cookies = pickle.load(cookiesfile)
         for cookie in cookies:
             driver.add_cookie(cookie)

def login():

    options = Options()
    options.add_argument("--start-maximized") #open Browser in maximized mode
    options.add_argument("--disable-web-security")
    options.add_argument("--no-sandbox") #bypass OS security model
    options.add_argument('--allow-running-insecure-content')
    options.add_argument("--window-size=1920,1080")
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument("no-default-browser-check")
    options.add_argument("no-first-run")
    options.add_experimental_option("detach", True)

    if sys.platform == "linux":
        chromedriverpath = "ui/chromedriver_linux64/chromedriver"
    if sys.platform == "win32":
        chromedriverpath = "ui/chromedriver_win32/chromedriver.exe"

    driver = webdriver.Chrome(executable_path=chromedriverpath, options=options)
    # if os.path.exists('/tmp/cookie'):
    #     print("loading cookie")
    #     # load_cookie(driver, '/tmp/cookie')

    driver.get("https://www.coinhako.com/wallet/")
    time.sleep(2)
    
    user = driver.find_element_by_id('user_email')
    
    for i in "eugene.chian@gmail.com":
        user.send_keys(i)
        time.sleep(0.4)
        
    password = driver.find_element_by_id('user_password')
    
    for i in "Meettheexperts1@":
        password.send_keys(i)
        time.sleep(0.4)
    
    time.sleep(3)
    
    submitbtn =driver.find_element_by_css_selector('button.g-recaptcha.btn.btn-primary.submit-btn.js-submit-btn')
    submitbtn.click()
    time.sleep(2)
    
    totp = TOTP("4sen7epfebr6pthvxw7pyswiv2dgd6f5rdzrmheyzhzcgyelhduf4c4wl5v4ywt3")
    token = totp.now()
    print (token)
    
    atokenfield = driver.find_element_by_id('user_gauth_token')
    atokenfield.send_keys(token)
    
    asubmit = driver.find_element_by_css_selector('button.btn.btn-primary.js-submit-btn')
    
    asubmit.click()
    
    time.sleep(1)
    # save_cookie(driver, '/tmp/cookie')
    
    return driver, True