#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  2 21:14:41 2021

@author: eugene
"""

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import os
cwd = os.getcwd()
print(cwd)

import sys
sys.path.append(cwd)
print(sys.path)
print(sys.platform)

from selenium import webdriver
from pyotp import *
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time
from ui.Utils import login

driver, logined = login()
baseURL = "https://www.coinhako.com"
driver.get("https://www.coinhako.com/wallet/")
time.sleep(2)

allcoins = driver.find_elements_by_css_selector('div.item.first-item')
allcoins = [coin.get_attribute("href") for coin in allcoins]

def string2Float(x):
    x = x.split(" ")[1]
    x= x.replace(',', '')
    return float(x)
 
for i in allcoins[0:5]:
    try:
        name = i.split("/")[2]
        print(i)

        # i= '/wallet/BTC/details'
        driver.get(baseURL+i)
        time.sleep(2)
        days = driver.find_elements_by_css_selector("g.highcharts-no-tooltip.highcharts-button.highcharts-button-normal")
        # periods = driver.find_elements_by_xpath("//text[@style='color:#333333;font-weight:normal;fill:#333333;']")
        # print(periods)
        
        periods = ["1h", "24h", "7d", "1m", "3m", "1y", "all"]
        st = 1
        en = 3
        periods = periods[st:en]

        for idx, period in enumerate(days[st:en]):
                
            # print("clicking period")
            period.click()
            time.sleep(3)
            #Find graph area

            pointer = driver.find_elements_by_css_selector('g.highcharts-series.highcharts-series-0.highcharts-area-series.highcharts-color-0')
            
            # pointer = driver.find_element_by_css_selector('path.highcharts-halo.highcharts-color-0')
            
            # print(pointer[0])
            action = webdriver.ActionChains(driver)
            action.move_to_element(pointer[0]).perform()
            action.move_to_element(pointer[0]).perform()
            # action = webdriver.ActionChains(driver)
            # action.move_to_element_with_offset(pointer[0], 0, 0).perform()


            # pointer = driver.find_elements_by_css_selector('path.highcharts-crosshair.highcharts-crosshair-thin')
            # print(pointer)
            pointer = driver.find_elements_by_css_selector('g.highcharts-markers.highcharts-series-0.highcharts-area-series.highcharts-color-0.highcharts-tracker')
            action = webdriver.ActionChains(driver)
            # action.move_to_element(pointer[0]).perform()
            # action.move_to_element_with_offset(pointer[0], 0, 0).perform()
            action.move_to_element_with_offset(pointer[0], -500, 0).perform()

            # action.move_to_element_with_offset(pointer[0], 100, 0).perform()
            # action.move_to_element_with_offset(pointer[0], 1, 0).perform()
            # price = driver.find_elements_by_xpath("//b[@style='color: white; font-size: 18px; text-align: center']")
            # print(price[0].text)
            # action.move_to_element_with_offset(pointer[0], 1, 0).perform()
            # price = driver.find_elements_by_xpath("//b[@style='color: white; font-size: 18px; text-align: center']")
            # print(price[0].text)

            dateA = [] 
            priceA = []

            if periods[idx] == "24h":
                stride =20
            else:
                stride = 15

            for i in range(2000):
                action = webdriver.ActionChains(driver)
                action.move_to_element_with_offset(pointer[0], stride, 0).perform()
                price = driver.find_elements_by_xpath("//b[@style='color: white; font-size: 18px; text-align: center']")
                datee = driver.find_elements_by_xpath("//span[@style='font-size: 12px; color: #D0E4FF; text-align: center']")
                # print(price)
                priceA += [price[0].text]
                dateA += [datee[0].text]
                # print(price[0].text)
                # print(datee[0].text)
                # print(i)
                if price[0].text=="":
                    break
                
            
            df = pd.DataFrame(list(zip(dateA, priceA)),
                        columns =['timestamp', 'buyPrice'])
            df['timestamp'] =  pd.to_datetime(df['timestamp'])
            df = df.dropna()
            df["buyPrice"] = df["buyPrice"].apply(string2Float, args=())
            df.to_csv(periods[idx]+"/"+ name + "_" + periods[idx] + ".csv", index=False)
            
            # name = 'BTC'
            # df = pd.read_csv('7d/BTC_7d.csv')
            # df['timestamp'] = pd.to_datetime(df['timestamp'])

            filelive = "live/"+name+".csv"
            if os.path.exists(filelive):
                dflive = pd.read_csv(filelive)
                dflive['timestamp'] = pd.to_datetime(dflive['timestamp'])
                
                newdf = pd.concat([dflive, df], ignore_index=True, sort=False)
                newdf.to_csv("newdf.csv", index = False)
                
                newdf = newdf.resample('1min', on='timestamp').agg({'buyPrice':'mean', 'sellPrice':'mean'}).reset_index()
                newdf['buyPrice'] = newdf['buyPrice'].interpolate(method='linear')
                newdf.to_csv(filelive, index=False)
            
            else:
                df["sellPrice"] = pd.NA
                df.to_csv(filelive, index=False)

    except Exception as e:
        print(e)
        print("re-resigning in to website")
        driver.quit()
        driver, logined = login()
        driver.get("https://www.coinhako.com/wallet/trade")
        time.sleep(2)
        continue

        
        