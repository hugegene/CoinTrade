
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time
import numpy as np
from pyotp import *
from ui.Utils import login, string2Float
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt
import math
from adjustText import adjust_text

# def string2Float(x):
#     x = x.split(" ")[1]
#     x= x.replace(',', '')
#     return float(x)

def mergelive(periods = ["24h", "7d", "1m"]):

    for i in os.listdir("24h/"):
        
        coinname = i.split("_")[0]
        print(coinname)

        # coinname = "BTC"

        if os.path.isfile("live/"+coinname +".csv"):
            livedf = pd.read_csv("live/"+coinname +".csv")  
            livedf['timestamp'] = pd.to_datetime(livedf['timestamp'])
        else:
            livedf = pd.DataFrame(columns = ["buyPrice", "sellPrice"])
            livedf["sellPrice"] = 0

        # periods = ["24h"]
        for i in periods:
            try:
                filename = i + "/" +coinname +"_"+ i+".csv"
                perioddf  = pd.read_csv(filename) 
                perioddf['timestamp'] = pd.to_datetime(perioddf['timestamp']) 

                livedf = pd.concat([livedf, perioddf], ignore_index=True, sort=False)

                livedf = livedf.resample('1min', on='timestamp').agg({'buyPrice':'mean', 'sellPrice':'mean'}).reset_index()
                livedf['buyPrice'] = livedf['buyPrice'].interpolate(method='linear')

                livedf.to_csv("live/"+coinname +".csv", index=False)
            except Exception as e :
                print(e)
       

# mergelive(periods = ["24h"])

coin = "ETH"
# df = pd.read_csv("live/"+coin+".csv")
df = pd.read_csv("1m/"+coin+"_1m.csv")
# df = pd.read_csv("7d/"+coin+"_7d.csv")
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['timestamp2'] = pd.to_datetime(df['timestamp'])
df["sellPrice"] = 0
df = df.set_index('timestamp')

# df = df.resample('min', on='timestamp').agg({'buyPrice':'mean', 'sellPrice':'mean'}).reset_index()
# df['buyPrice'] = df['buyPrice'].interpolate(method='linear')

df["buyGradient"] = df["buyPrice"].diff()/df['timestamp2'].diff().dt.seconds/60

buyGrad_Std = math.sqrt(((df["buyGradient"]-0)**2).sum()/df["buyGradient"].count())

df["buyGradient_norm"] = df["buyGradient"]/buyGrad_Std

df["buyGradient2"] = df["buyGradient"].diff()

df["buyGradient_roll1dmean"] = df["buyGradient_norm"].rolling('48H').mean()

df["diurnal_range"] = (df["buyPrice"] - df["buyPrice"].rolling('7D').min())/df["buyPrice"].rolling('7D').min()

df["diurnal"] = (df["buyPrice"] - df["buyPrice"].rolling('7D').min())/(df["buyPrice"].rolling('7D').max() - df["buyPrice"].rolling('7D').min())

# df['next_time'] = (df.apply(lambda x: next((z for (y, z) in zip(df['price'], df['time'])
#                                             if y > x['price'] if z > x['time']), None), axis=1))
df = df.sort_values(by="timestamp2", ascending=False)
threshold = 0.10


# df.loc[(df.index < df.index[3]) & (df.buyGradient_roll1dmean.abs() < threshold), :]

# df.loc[(df.index > 6) & (df.buyGradient_roll1dmean < threshold), "buyPrice"] 

df[['next_time']] = df.apply(lambda x: next((t for (p, g, t) in zip(df.loc[(df.index < x.name) & (df.buyGradient_roll1dmean.abs() < threshold), "buyPrice"], df.loc[(df.index < x.name) & (df.buyGradient_roll1dmean.abs() < threshold), "buyGradient_roll1dmean"], df.loc[(df.index < x.name) & (df.buyGradient_roll1dmean.abs() < threshold), "timestamp2"])
                                            if abs((x['buyPrice']-p)/p) > 0.05), None), axis=1)
                                            
df[['gain']] = df.apply(lambda x: next(((x['buyPrice']-p)/p for (p, g, t) in zip(df.loc[(df.index < x.name) & (df.buyGradient_roll1dmean.abs() < threshold), "buyPrice"], df.loc[(df.index < x.name) & (df.buyGradient_roll1dmean.abs() < threshold), "buyGradient_roll1dmean"], df.loc[(df.index < x.name) & (df.buyGradient_roll1dmean.abs() < threshold), "timestamp2"])
                                            if abs((x['buyPrice']-p)/p) > 0.05), None), axis=1)
    
# df[['next_time']] = df.apply(lambda x: next((t for (p, g, t) in zip(df.loc[x.name:,'buyPrice'], df.loc[x.name:,'buyGradient_roll1dmean'], df.loc[x.name:,'timestamp2'])
#                                             if abs((x['buyPrice']-p)/p) > 0.05 and g < threshold), None), axis=1)

# df[['gain']] = df.apply(lambda x: next(((x['buyPrice']-p)/p for (p, g, t) in zip(df.loc[x.name:,'buyPrice'], df.loc[x.name:,'buyGradient_roll1dmean'], df.loc[x.name:,'timestamp2'])
#                                             if abs((x['buyPrice']-p)/p) > 0.05 and g < threshold), None), axis=1)
                                         
gradientplot = df.loc[df["buyGradient_roll1dmean"].abs()<threshold,:]

minplot = df.loc[df["diurnal"]<0.10,:]

# posgrad = df.loc[(df["buyGradient2"].abs()>threshold) & (df["buyGradient"]>0),:]
# neggrad = df.loc[(df["buyGradient2"].abs()>threshold) & (df["buyGradient"]<0),:]

# df["1dayChange"]= df.buyPrice.pct_change(periods=1440)

# df["2dayChange"]= df.buyPrice.pct_change(periods=2880)
# df["3dayChange"]= df.price.pct_change(periods=1440)
# df["4dayChange"]= df.price.pct_change(periods=1440)

# neggrad = df.loc[df["gradient"]< -10,:]

df.to_csv(coin +"_Analysis.csv")

fig, ax = plt.subplots(figsize=(10, 10))

ax.plot(df.index,
        df['buyPrice'],
        color='blue')

# ax.scatter(posgrad['timestamp'],
#         posgrad['buyPrice'],
#         color='green')

# ax.scatter(neggrad['timestamp'],
#         neggrad['buyPrice'],
#         color='red')

ax.scatter(gradientplot.index,
        gradientplot['buyPrice'],
        color='red')

# ax.scatter(minplot.index,
#         minplot['buyPrice'],
#         color='green', s=10)

# day1C = df.loc[df['1dayChange'].abs()> 0.05,:]
# ax.scatter(day1C['date'],
#         day1C['price'],
#         color='blue')

# day2C = df.loc[df['2dayChange'].abs()> 0.05,:]
# ax.scatter(day2C['timestamp'],
#         day2C['buyPrice'],
#         color='green')


texts = []
# annotate points in axis
count = 0
for idx, row in gradientplot.iterrows():
    count += 1
    if (count) %10 ==0:
        annotate = str(row["gain"])[:6]

        texts += [plt.text(row.name, row['buyPrice'], str(row["gain"])[:6] + "_" +str(row["next_time"])[:10])]
        
        # ax.annotate(row["gain"], (row.name, row['buyPrice']) )

# count = 0
# for idx, row in gradientplot.iterrows():
#     count +A= 1
#     if (count -1)%8 ==0:
#         ax.annotate(row["next_time"], (row.name, row['buyPrice']) )


# texts = [plt.text(x[i], y[i], 'Text%s' %i) for i in range(len(x))]
adjust_text(texts)

# adjust_text(texts, only_move={'points':'y', 'texts':'y'}, arrowprops=dict(arrowstyle="->", color='r', lw=0.5))

fig.savefig(coin+'.png')
fig.clear()
