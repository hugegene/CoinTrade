import pandas as pd
import datetime


def organiseTransAft2022(transactdf):
    if isinstance(transactdf, pd.DataFrame):
        print("dataframe found")
    else:
        transactdf = pd.read_csv("streamTransaction.csv")
        transactdf['timestamp'] = pd.to_datetime(transactdf['timestamp'])

    transactdf['price'] = transactdf['price'].str.strip()
    transactdf[['price','amount']] = transactdf['price'].str.split(' ', expand=True)
    transactdf.loc[transactdf["type"]==" SGD Sell Instant Order ","temp"] = transactdf.loc[transactdf["type"]==" SGD Sell Instant Order ","qty"]
    transactdf.loc[transactdf["type"]==" SGD Sell Instant Order ","qty"] = transactdf.loc[transactdf["type"]==" SGD Sell Instant Order ","amount"]
    transactdf.loc[transactdf["type"]==" SGD Sell Instant Order ","amount"] = transactdf.loc[transactdf["type"]==" SGD Sell Instant Order ","temp"]

    transactdf['type'] = transactdf['type'].str.strip()
    transactdf.to_csv("transacprocess.csv")

    yearend = datetime.datetime(2022, 1, 4,00,00)

    transactdf = transactdf.loc[transactdf.timestamp > yearend, :]

    buydf = transactdf.loc[transactdf["type"]== "SGD Buy Instant Order", :]
    buydf.loc[:, "qtyS"] = buydf.loc[:, "qty"].astype(str).str[:-1]
    buydf.to_csv("buydf.csv")

    selldf = transactdf.loc[transactdf["type"]=="SGD Sell Instant Order", :]
    selldf.loc[:, "qtyS"] = selldf.loc[:, "qty"].astype(str).str[:-1]
    selldf.to_csv("selldf.csv")


    ss = buydf.merge(selldf, left_on = "qtyS", right_on="qtyS", how="outer", suffixes = ["","_sell"])
    ss.to_csv("transactionHistory.csv")

    return ss

# organiseTransAft2022(None)



# transactdf = pd.read_csv("streamTransaction.csv")

# transactdf['price'] = transactdf['price'].str.strip()
# transactdf[['price','amount']] = transactdf['price'].str.split(' ', expand=True)
# transactdf.loc[transactdf["type"]==" SGD Sell Instant Order ","temp"] = transactdf.loc[transactdf["type"]==" SGD Sell Instant Order ","qty"]
# transactdf.loc[transactdf["type"]==" SGD Sell Instant Order ","qty"] = transactdf.loc[transactdf["type"]==" SGD Sell Instant Order ","amount"]
# transactdf.loc[transactdf["type"]==" SGD Sell Instant Order ","amount"] = transactdf.loc[transactdf["type"]==" SGD Sell Instant Order ","temp"]

# transactdf['type'] = transactdf['type'].str.strip()
# transactdf.to_csv("transacprocess.csv")

# buydf = transactdf.loc[transactdf["type"]== "SGD Buy Instant Order", :]
# buydf.to_csv("buydf.csv")

# selldf = transactdf.loc[transactdf["type"]=="SGD Sell Instant Order", :]

# swapdf = transactdf.loc[transactdf["type"].str[-18:]=="Swap Instant Order" , :]
# swapdf.to_csv("swap.csv")

# swapdf_b = swapdf.copy()
# swapdf_b["coin"] = swapdf_b["type"].str.split(" ").str[0]
# swapdf_b["price"] = np.nan
# swapdf_b["amount"] = np.nan

# swapdf_s = swapdf.copy()
# swapdf_s["qty"] = swapdf_s["amount"]
# swapdf_s["amount"] = np.nan

# buySwap = pd.concat([buydf, swapdf_b])
# buySwap.sort_values(by=["coin", "timestamp"], inplace = True)
# buySwap.to_csv("buySwap.csv")

# sellSwap = pd.concat([selldf, swapdf_s])
# sellSwap.sort_values(by=["coin", "timestamp"], inplace = True)
# sellSwap.to_csv("sellSwap.csv")

# closedf = pd.DataFrame()

# for coin in buydf.coin.unique():

#     bcoindf = buySwap.loc[buySwap.coin== coin, :]
#     bcoindf.to_csv("bcondf.csv")
#     scoindf = sellSwap.loc[sellSwap.coin== coin, :]

#     scoindf.to_csv("scondf.csv")
    
#     break



# buydf = buydf.sort_values(by=['coin', 'timestamp'])

# for coin in buydf.coin.unique():
#     buydf.loc[buydf.coin==coin, "qty1Cum"] = buydf.loc[buydf.coin==coin, "qty"].rolling(1, min_periods=1).sum().astype(str).str[:-2]
#     buydf.loc[buydf.coin==coin, "qty2Cum"] = buydf.loc[buydf.coin==coin, "qty"].rolling(2, min_periods=2).sum().astype(str).str[:-2]
#     buydf.loc[buydf.coin==coin, "qty3Cum"] = buydf.loc[buydf.coin==coin, "qty"].rolling(3, min_periods=3).sum().astype(str).str[:-2]
#     buydf.loc[buydf.coin==coin, "qty4Cum"] = buydf.loc[buydf.coin==coin, "qty"].rolling(4, min_periods=4).sum().astype(str).str[:-2]
#     buydf.loc[buydf.coin==coin, "qty5Cum"] = buydf.loc[buydf.coin==coin, "qty"].rolling(5, min_periods=5).sum().astype(str).str[:-2]


# ss1 = buydf.merge(selldf, left_on = "qty1Cum", right_on="qtyS", how="outer", suffixes = ["","_sell"])
# ss1.to_csv("transacprocess1.csv")

# for i in ["qty2Cum", 
# "qty3Cum", "qty4Cum", "qty5Cum"
# ]:
#     ss2 = ss1.loc[:, ["coin", i]].merge(selldf, left_on = i, right_on="qtyS", how="left", suffixes = ["","_sell"])
#     notnull = ss2.loc[pd.notna(ss2["coin_sell"]),:].index

#     ss1.loc[notnull, "coin_sell":] = ss2.loc[pd.notna(ss2["coin_sell"]),"coin_sell":].values

#     mergeNull = ss1.merge(ss2.loc[pd.notna(ss2["coin_sell"]),["coin", "qtyS"]], left_on = "qtyS", right_on="qtyS", how="left", suffixes = ["","_toDelete"])

#     dropindex = mergeNull.loc[(mergeNull.coin_toDelete.isna() == False) & (mergeNull.coin.isna() == True),:].index

#     ss1 = ss1.drop(dropindex)

# ss1.to_csv("transacprocess2.csv")




# buydf = pd.concat([buydf, swapdf_b])
# buydf.to_csv("buyafterconcatswap.csv")

# ss = buydf.merge(swapdf_s, on = "qty", how="outer", suffixes=('', '_swap'))
# ss.to_csv("transacprocess2.csv")


# enjdf = pd.read_csv("ENJtest.csv")
# enjdf["timestamp"] = pd.to_datetime(enjdf["timestamp"])
# enjdf = enjdf.sort_values(by = "timestamp")

# enjdf.to_csv("enjsave.csv")

# ss = ss.merge(swapdf, on = "qty", how="outer", suffixes=('_b', '_s'))
