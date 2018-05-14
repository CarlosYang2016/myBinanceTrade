# coding=utf-8
import time
from decimal import *
from binance.client import Client
from binance.exceptions import BinanceAPIException

viBTC = 0.3
viXVG = 0.3

api_key = api_key #
api_secret = api_key #

# create the Binance client, no need for api key
client = Client(api_key=api_key, api_secret=api_secret)

count = 0
while True:
    count = count + 1
    print('*'*20)
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ' ---- {}.'.format(count))
    myBTC = client.get_asset_balance(asset='BTC')
    myXVG = client.get_asset_balance(asset='XVG')
    priceXVG = client.get_symbol_ticker(symbol='XVGBTC')
    bidAsk = client.get_order_book(symbol='XVGBTC', limit=10)
    sellPrice = bidAsk['bids'][1][0]
    buyPrice = bidAsk['asks'][1][0]
    assetActXVG = float(myXVG['free']) * float(priceXVG['price'])  # BTC价值
    assetXVG = assetActXVG + viXVG
    assetActBTC = float(myBTC['free'])
    assetBTC = assetActBTC + viBTC
    myOper = 'Idle'

    if assetXVG/(assetXVG + assetBTC) > 0.51:
        myOper = 'Sell'
        sellXVG = int((assetXVG - assetBTC) / (2 * float(priceXVG['price'])))
        if sellXVG > float(myXVG['free']) and assetActXVG > 0.001:
            sellXVG = float(myXVG['free'])
            try:
                mySell = client.order_limit_sell(symbol='XVGBTC', quantity=Decimal(str(sellXVG)), price=sellPrice)
            except BinanceAPIException:
                myOper = 'Idle'
                print("卖出XVG错误")
        else:
            print("没有足够的XVG个数可卖了")
    elif assetXVG/(assetXVG + assetBTC) < 0.49:
        myOper = 'Buy'
        # 买入个数
        buyXVG = int((assetBTC - assetXVG) / (2 * float(priceXVG['price'])))
        print('买入XVG个数: ', buyXVG)
        if buyXVG > assetActBTC and assetActBTC > 0.001:
            buyXVG = assetActBTC
            try:
                myBuy = client.order_limit_buy(symbol='XVGBTC', quantity=Decimal(str(buyXVG)), price=buyPrice)
            except BinanceAPIException:
                myOper = 'Idle'
                print("买入XVG错误")
        else:
            print("没有足够的BTC买XVG了")
    else:
        myOper = 'Idle'
        print("正常监控")
    
    time.sleep(5)
    
    if myOper != 'Idle':
        print("查看交易是否完成")
        if myOper == 'Sell':
            orderId = mySell['orderId']
        elif myOper == 'Buy':
            orderId = myBuy['orderId']
        for i in range(10):
            checkTrade = client.get_order(symbol='XVGBTC', orderId=orderId)
            if checkTrade['status'] == 'FILLED' or checkTrade['status'] == 'CANCELED':
                break
            time.sleep(5)

         if checkTrade['status'] != 'FILLED' and checkTrade['status'] != 'CANCELED':
            cancelTrade = client.cancel_order(symbol='XVGBTC', orderId=orderId)
            print("交易失败了，取消该订单")
        time.sleep(5)
