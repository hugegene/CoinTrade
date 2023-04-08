import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time
import numpy as np
from pyotp import *
from ui.Utils import login
from datetime import datetime, timedelta
import os
import pandas as pd

def string2Float(x):
    x = x.split(" ")[1]
    x= x.replace(',', '')
    return float(x)

# folders = ["24h", "1m"]
df = pd.read_csv("7d/BTC_7d.csv")
df['date'] = pd.to_datetime(df['date'])
df["price"] = df["price"].apply(string2Float, args=())
df = df.drop(columns=["Unnamed: 0"])
df.columns = ["timestamp", "buyPrice"]


df24h = pd.read_csv("24h/BTC_24h.csv")
df24h['timestamp'] = pd.to_datetime(df24h['timestamp'])
newdf = pd.concat([df24h, df], ignore_index=True, sort=False)

newdf = newdf.resample('min', on='timestamp').agg({'buyPrice':'mean', 'sellPrice':'mean'}).reset_index()

newdf.to_csv("24h/BTC_24h.csv")