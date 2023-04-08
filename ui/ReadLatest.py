#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 19 16:04:21 2021

@author: eugene
"""
###
# from ast import Str
# from asyncio.windows_events import NULL
import os
from tokenize import Double
cwd = os.getcwd()
print(cwd)

import sys
sys.path.append(cwd)
print(sys.path)
print(sys.platform)

import logging
logging.basicConfig(filename='logging.log', 
#                    encoding='utf-8', 
                    level=logging.DEBUG,
                    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    )

import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
import time
import numpy as np
from pyotp import *
from ui.Utils import login, save_cookie, load_cookie
from ui.FetchTransaction import organiseTransAft2022
from datetime import datetime, timedelta


def retrievePriceTables(driver):
    driver.get("https://www.coinhako.com/wallet/trade")
    time.sleep(2)

    coinnames = driver.find_elements_by_css_selector('div.name-group')

    coinlist = [i.text.split("\n")[0] for i in coinnames]

    coinPriceDict = {}
    for i in coinlist:
        print(i)
        if os.path.isfile("live/" + i + ".csv"):
            coinPriceDict[i] = pd.read_csv("live/" + i + ".csv")
            coinPriceDict[i]["timestamp"] = pd.to_datetime(coinPriceDict[i]["timestamp"])
        else:
            coinPriceDict[i] = pd.DataFrame({'timestamp' : [], 'buyPrice': [], 'sellPrice': []})
            coinPriceDict[i]["timestamp"] = pd.to_datetime(coinPriceDict[i]["timestamp"])
            coinPriceDict[i].to_csv("live/" + i + ".csv", index = False)
    return coinPriceDict


def sell_if_possible(driver, coin, simulate=False):
    global transactionDF
    pagechange = False
    sellitems = transactionDF.loc[((transactionDF.coin == coin) & (transactionDF.sellSignal == True)),:]
    
    if simulate == True:
        for index, row in sellitems.iterrows():
             print("selling " + row["coin"] + " at " + str(index))
             transactionDF.at[index, "coin_sell"] = row["coin"]
             transactionDF.at[index, "type_sell"] = "simulate sell order"
             transactionDF.at[index, "price_sell"] = transactionDF.at[index, "sellPrice"]
             transactionDF.at[index, "qty_sell"] = transactionDF.at[index, "qty"]
             transactionDF.at[index, "amount_sell"] = transactionDF.at[index, "qty"]*transactionDF.at[index, "sellPrice"]*0.9
             transactionDF.at[index, "timestamp_sell"] = datetime.now()
             transactionDF.to_csv("TransactionSimulation.csv", index = False)
             return pagechange

    for index, row in sellitems.iterrows():
        print("selling " + row["coin"] + " at " + str(index))
        # driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't') 
        driver.get("https://www.coinhako.com/wallet/order/sell/" + row["coin"] + "_SGD")
        time.sleep(1)
        # bal = driver.find_element_by_css_selector('span.pull-right.weight-400').text
        # bal = float(bal.split(" ")[1])
        input = driver.find_element_by_css_selector('input.ng-pristine.ng-untouched.ng-empty.ng-invalid.ng-invalid-required')
        input.send_keys(str(row["qty"]))
        button = driver.find_element_by_css_selector('button.btn.btn-block.btn-primary.mg-b-60.ng-binding')
        button.click()
        time.sleep(1)
        button = driver.find_element_by_css_selector('button.btn.btn-block.btn-primary.mg-b-45')
        # button.click()
        time.sleep(1)
        pagechange = True

    return pagechange
       
def buy_if_possible(df, driver, coin, simulate=False):

    global transactionDF
    pagechange = False

    # if coin == "BTC" or coin == "AAVE":
    #     df.iloc[-1, df.columns.get_loc('buySignal')] = True
      
    if simulate == True:
 
        if df.iloc[-1]["buySignal"]:
            
            recentbought = transactionDF.loc[transactionDF.coin == coin, "timestamp"].max()
            dategap = True
            if pd.isna(recentbought) == False:
                dategap = (datetime.now() - recentbought).days > 3

            if pd.isna(recentbought) or dategap:

                print("buying " + coin)
                dfrow = df.iloc[-1]

                new_row = {'coin': coin, 
                            'type': "simulate buy order", 
                            'price': dfrow["buyPrice"], 
                            'qty': 0.9*(5/dfrow["buyPrice"]),
                            'timestamp': datetime.now(),
                            'amount': 5,
                            }

                transactionDF = transactionDF.append(new_row, ignore_index = True)

                transactionDF.to_csv("TransactionSimulation.csv", index =False)

        return pagechange

    # for index, row in buyitems.iterrows():
        
    #     print("buying " + row["coin"] + " at " + str(index))
    #     driver.get("https://www.coinhako.com/wallet/order/buy/" + row["coin"] + "_SGD")
    #     time.sleep(1)
    #     input = driver.find_elements_by_css_selector('input.ng-pristine.ng-empty.ng-invalid.ng-invalid-required.ng-touched')
    #     input[0].send_keys(5)
    #     button = driver.find_element_by_css_selector('button.btn.btn-block.btn-primary.mg-b-60.ng-binding')
    #     button.click()
    #     time.sleep(0.5)
    #     button = driver.find_element_by_css_selector('btn.btn-block.btn-primary.mg-b-45')
    #     button.click()
    #     time.sleep(1)
    #     coinWalletDF.loc[coinWalletDF["coin"]==row["coin"],"value"] += 5
    #     coinWalletDF.to_csv("value.csv", index = False)
    #     pagechange = True
    return pagechange


def fetchTransaction(driver, simulate = False):
    print("fetching transaction")
    if simulate == True:
        transactdf = pd.read_csv("TransactionSimulation.csv")
        transactdf["timestamp"] = pd.to_datetime(transactdf["timestamp"])
        return transactdf

    checkrow = ""
    transactdf = []
    for i in range(1,10):
        # i=2
        driver.get("https://www.coinhako.com/wallet/history/trade?page=" + str(i))
        time.sleep(1)

        table = driver.find_element_by_css_selector('table.table.history-table')

        stream = []
        yearend = datetime(2022, 1, 4,00,00)

        rows = table.find_elements(By.TAG_NAME, "tr") # get all of the rows in the table
        for row in rows[1:-1]:
            print(row.text)
            if row.text != "":
                line = row.text
                line = line.replace(",", "")  
                line = line.replace("/", ",")  
                line = line.replace("--", ",")   
                line = line.replace("Completed", ",")   
                stream += [line]

        streamdf = pd.DataFrame([sub.split(",") for sub in stream], columns = ["coin", "type", "price", "qty", "timestamp"])
        streamdf["timestamp"] = pd.to_datetime(streamdf["timestamp"])

        streamdf.to_csv(str(i)+"_stream.csv")

        if isinstance(transactdf, pd.DataFrame):
            transactdf = pd.concat([transactdf, streamdf])
        else:
             transactdf = streamdf.copy()

        if streamdf.loc[0,"timestamp"] < yearend:
            break

        checkrow = streamdf.loc[0,"timestamp"]
     
    transactdf.to_csv("streamTransaction.csv", index = False)


    
    print("proceeding")

    transactdf['coin'] = transactdf['coin'].str.strip()
    transactdf['price'] = transactdf['price'].str.strip()
    transactdf['type'] = transactdf['type'].str.strip()

    transactdf[['price','amount']] = transactdf['price'].str.split(' ', expand=True)
    transactdf['price'] = transactdf['price'].astype(float)
    transactdf['amount'] = transactdf['amount'].astype(float)
    transactdf.loc[transactdf["type"]=="SGD Sell Instant Order","temp"] = transactdf.loc[transactdf["type"]=="SGD Sell Instant Order","qty"]
    transactdf.loc[transactdf["type"]=="SGD Sell Instant Order","qty"] = transactdf.loc[transactdf["type"]=="SGD Sell Instant Order","amount"]
    transactdf.loc[transactdf["type"]=="SGD Sell Instant Order","amount"] = transactdf.loc[transactdf["type"]=="SGD Sell Instant Order","temp"]
    
  
    transactdf.loc[(transactdf["type"] != "SGD Buy Instant Order") & (transactdf["type"] != "SGD Sell Instant Order"), "temp"] = transactdf.loc[(transactdf["type"] != "SGD Buy Instant Order") & (transactdf["type"] != "SGD Sell Instant Order"), "qty"]
    transactdf.loc[(transactdf["type"] != "SGD Buy Instant Order") & (transactdf["type"] != "SGD Sell Instant Order"), "qty"] = transactdf.loc[(transactdf["type"] != "SGD Buy Instant Order") & (transactdf["type"] != "SGD Sell Instant Order"), "amount"]
    transactdf.loc[(transactdf["type"] != "SGD Buy Instant Order") & (transactdf["type"] != "SGD Sell Instant Order"), "amount"] = pd.NA
    transactdf.loc[(transactdf["type"] != "SGD Buy Instant Order") & (transactdf["type"] != "SGD Sell Instant Order"), "type"] = transactdf.loc[(transactdf["type"] != "SGD Buy Instant Order") & (transactdf["type"] != "SGD Sell Instant Order"), "type"] + " (sell)"
    

    swapbuydf = transactdf.loc[(transactdf["type"] != "SGD Buy Instant Order") & (transactdf["type"] != "SGD Sell Instant Order"), :]
    swapbuydf["coin"] = swapbuydf["type"].str.split(" ").str[0]
    swapbuydf["type"] = swapbuydf["type"].str[:-7] + " (buy)"
    swapbuydf["qty"] = swapbuydf["temp"]

    resultdf  = pd.concat([transactdf, swapbuydf], ignore_index=True, sort=False)
    resultdf = resultdf.sort_values(by=['coin', 'timestamp'], ascending=[1, 0])

    
    resultdf.to_csv("transacprocess.csv", index=False)
    resultdf = pd.read_csv("transacprocess.csv")



    def resolve(x):
        if "sell" in x.type or "Sell" in x.type:
            eligible = resultdf.loc[ (resultdf.index > x.name) & (resultdf["coin"] == x.coin) & (resultdf["type"].str.contains("buy") | resultdf["type"].str.contains("Buy")),:]
            for index, row in eligible.iterrows():
                if abs((row["qty"] - x["qty"])/x["qty"]) < 0.001:
                    print("match")
                    print(x["qty"])
                    print(row["qty"])
                    # print((row["qty"] - x["qty"])/x["qty"])
                    # print(row)
    

    resultdf['found'] = resultdf.apply(lambda x: resolve(x), axis=1)

    threshold = 0.15
    resultdf['found'] = df.apply(lambda x: next((t for (p, g, t) in zip(df.loc[x.name:,'buyPrice'], df.loc[x.name:,'buyGradient_roll1dmean'], df.loc[x.name:,'timestamp2'])
                                                if ((p - x['buyPrice'])/x['buyPrice']) > 0.01
                                                if g < threshold), None), axis=1)

    
    transactdf = transactdf.loc[transactdf.timestamp > yearend, :]

    buydf = transactdf.loc[transactdf["type"]== "SGD Buy Instant Order", :]
 
    buydf["qtyS"] = buydf["qtyS"].str[:-1]
    buydf.to_csv("buydf.csv")

    selldf = transactdf.loc[transactdf["type"]=="SGD Sell Instant Order", :]

    selldf["qtyS"] = selldf["qtyS"].str[:-1]
    selldf.to_csv("selldf.csv")


    ss = buydf.merge(selldf, left_on = "qtyS", right_on="qtyS", how="outer", suffixes = ["","_sell"])
    ss.to_csv("transactionHistory.csv", index = False)

    return ss

def fetchPrices(driver):
    prices = driver.find_elements_by_css_selector('span.ticker-dollars.ng-binding')
    balances = driver.find_elements_by_css_selector('span.big-text.store-balance')
    timestamp = datetime.now()
    # day7before = timestamp - timedelta(days = 7)
    # day30before = timestamp - timedelta(days = 30)
    day45before = timestamp - timedelta(days = 45)

    pricelist = []
    for i in prices:
        pricelist += [float(i.text.split(" ")[1].replace(',', ''))]
    pricearray = np.array(pricelist).reshape((-1, 2))
    # print(pricearray)
    # balancelist = []
    # for i in balances:
    #     balancelist += [float(i.text.replace(",", ""))]
    return pricearray, timestamp, day45before

driver, logined = login()



#########################
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
########################################################33

SIMULATE = False

transactionDF = fetchTransaction(driver, simulate = SIMULATE)

coinPriceDict = retrievePriceTables(driver)

failtries = 0
while(True):
    try:
        startime = time.time()
        for idx, coin in enumerate(coinPriceDict.keys()):

            # coin = "BTC"
            # idx = 0
            
            pricearray, timestamp, day45before = fetchPrices(driver)

            df = coinPriceDict[coin]

            new_row = {'timestamp': timestamp, 'buyPrice': pricearray[idx][0], 'sellPrice': pricearray[idx][1]}
            df = df.append(new_row, ignore_index=True)
            
            df = df.loc[df["timestamp"] > day45before, :]

            df = df.resample('min', on='timestamp').agg({'buyPrice':'mean', 'sellPrice':'mean'}).reset_index()
            df['buyPrice'] = df['buyPrice'].interpolate(method='linear')

            df["buyGradient"] = (((df["buyPrice"].diff() / df["timestamp"].diff().dt.total_seconds())*60)/df["buyPrice"].shift())
            df["buyGradient2"] = df["buyGradient"].diff()

            df["7dayMin"] = df["buyPrice"].rolling(10080).max()
            df["7dayMinAdjusted"] = 0.10*(df["buyPrice"].rolling(10080).max() - df["buyPrice"].rolling(10080).min()) + df["buyPrice"].rolling(10080).min()
     
            df["7daySignal"] = df["buyPrice"] < df["7dayMinAdjusted"]
            df["buySignal"] = df["7daySignal"] 

            # df["1dayChange"]= df.buyPrice.pct_change(periods=1440)
            # df["2dayChange"]= df.buyPrice.pct_change(periods=2880)
            # df["4dayChange"]= df.buyPrice.pct_change(periods=5760)
            # df["8dayChange"]= df.buyPrice.pct_change(periods=11520)
            # df["16dayChange"]= df.buyPrice.pct_change(periods=23040)
            # df["32dayChange"]= df.buyPrice.pct_change(periods=46080)

            df.to_csv("live/" + coin + ".csv", index = False)
            coinPriceDict[coin] = df

            # buying
            retB = buy_if_possible(df, driver, coin, simulate=SIMULATE)

            #TransactionDf for selling ------------------
            transactionDF["percentSignal"] = pd.NA
            transactionDF["sellSignal"] = pd.NA
            transactionDF.loc[(transactionDF["coin"]==coin) & (pd.isna(transactionDF["price_sell"])), "sellPrice"] = pricearray[idx][1]
            transactionDF.loc[(transactionDF["coin"]==coin) & (pd.isna(transactionDF["price_sell"])), "percent_diff"] = (transactionDF.loc[(transactionDF["coin"]==coin) & (pd.isna(transactionDF["price_sell"])), "sellPrice"] - transactionDF.loc[(transactionDF["coin"]==coin) & (pd.isna(transactionDF["price_sell"])), "price"])/transactionDF.loc[(transactionDF["coin"]==coin) & (pd.isna(transactionDF["price_sell"])), "price"]
            transactionDF.loc[(transactionDF["coin"]==coin) & (pd.isna(transactionDF["price_sell"])), "percentSignal"] = transactionDF.loc[(transactionDF["coin"]==coin) & (pd.isna(transactionDF["price_sell"])), "percent_diff"] > 0.15
            transactionDF.loc[(transactionDF["coin"]==coin) & (pd.isna(transactionDF["price_sell"])), "sellSignal"] = transactionDF.loc[(transactionDF["coin"]==coin) & (pd.isna(transactionDF["price_sell"])), "percentSignal"] 
            
            if SIMULATE:
                transactionDF.to_csv("TransactionSimulation.csv", index = False)
            else:
                transactionDF.to_csv("Transaction.csv", index = False)

            # Selling 
            retS = sell_if_possible(driver, coin, simulate=SIMULATE)
           
            # if retB == True or retS == True:
            #     driver.get("https://www.coinhako.com/wallet/trade")
            # time.sleep(3)
        print("time taken for one loop at "+ str(datetime.now())    +" is " + str(time.time()-startime))

    except Exception as e:
        if failtries < 3:
            print(e)
            print("re-resigning in to website")
            logging.debug("re-resigning in to website")
            driver.quit()
            action, driver, logined = login()
            driver.get("https://www.coinhako.com/wallet/trade")
            failtries += 1
            time.sleep(2)
            continue



