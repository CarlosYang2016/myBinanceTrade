# -*- coding: utf-8 -*-
"""
Created on Sat May 19 17:38:22 2018

@author: carlos CY
"""
import time
from decimal import *
from binance.client import Client
from binance.exceptions import BinanceAPIException

viBTC = 0.3
viXVG = 43795  

api_key = ''
api_secret = ''

# create the Binance client, no need for api key
client = Client(api_key=api_key, api_secret=api_secret)

count = 0
buyCount = 0
sellCount = 0
errCount = 0
while True:
    # 2.get accounts
    count = count + 1
    try:
        myBTC = client.get_asset_balance(asset='BTC')
        # {'asset': 'BTC', 'free': '0.68327561', 'locked': '0.00000000'}
        myXVG = client.get_asset_balance(asset='XVG')

        # 3.get lastest price
        # priceBTC = client.get_symbol_ticker(symbol = 'BTCBTC')
        # {'symbol': 'BTCBTC', 'price': '0.00154130'}
        priceXVG = client.get_symbol_ticker(symbol='XVGBTC')
        print(priceXVG['price'])	
        
        # use buy 2 price as sell price and sell2 price as buy price
        #bidAsk = client.get_order_book(symbol='XVGBTC', limit=10)
        #sellPrice = bidAsk['bids'][1][0]
 
        #buyPrice = bidAsk['asks'][1][0]

        sellPrice = priceXVG['price']
        buyPrice = priceXVG['price']

        # 4.caculate the xvg/btc rate
        assetActXVG = float(myXVG['free']) * float(priceXVG['price'])  
        assetXVG = assetActXVG + viXVG * float(priceXVG['price'])
        assetActBTC = float(myBTC['free'])
        assetBTC = assetActBTC + viBTC
        
        
        print('XVG asset rate: ',assetXVG/(assetXVG + assetBTC))

        myOper = 'Idle'

        if assetXVG/(assetXVG + assetBTC) > 0.503:
            print('XVG asset rate up to: ', assetXVG/(assetXVG + assetBTC))

            sellXVG = int((assetXVG - assetBTC) / (2 * float(priceXVG['price'])))
            if (sellXVG > int(float(myXVG['free']))) and (assetActXVG > 0.001):
                sellXVG = int(float(myXVG['free']))
            
            if assetActXVG > 0.001:
                try:
                    mySell = client.order_limit_sell(symbol='XVGBTC', quantity=Decimal(str(sellXVG)), price=sellPrice)
                    # {'symbol': 'XVGBTC', 'orderId': 37475851, 'clientOrderId': 'Xhq837HZAIKRrgd4c97Ey1', 'transactTime': 1526217559759,
                    #  'price': '0.00000728', 'origQty': '500.00000000', 'executedQty': '0.00000000', 'status': 'NEW',
                    #  'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'SELL'}
                    myOper = 'Sell'
                    
                    msg = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + 'sell {} XVG by price {}'.format(sellXVG,sellPrice)
                    print(msg)
                    #bot.file_helper.send(msg)
                    sellCount = sellCount + 1
                except BinanceAPIException:
                    print("Sell XVG Error!")
            else:
                print("no enough XVG to sell.")
        elif assetXVG/(assetXVG + assetBTC) < 0.49:
            print('XVG asset rate low to : ', assetXVG/(assetXVG + assetBTC))
            buyXVG = int((assetBTC - assetXVG) / (2 * float(priceXVG['price'])))
            if buyXVG > int(assetActBTC/float(buyPrice)) and assetActBTC > 0.001:
                buyXVG = int(assetActBTC/float(buyPrice))
            
            if assetActBTC > 0.001:
                try:
                    myBuy = client.order_limit_buy(symbol='XVGBTC', quantity=Decimal(str(buyXVG)), price=buyPrice)
                    myOper = 'Buy'
                    msg = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + 'buy {} XVG by price {}'.format(buyXVG,buyPrice)
                    print(msg)
                    #bot.file_helper.send(msg)
                    buyCount = buyCount + 1
                except BinanceAPIException:
                    print("Buy XVG Error!")
            else:
                print("no enough BTC to buy XVG")
        else:
            pass
            
        # 5.delay 5s
        time.sleep(5)
        
        # 6.check the sell/buy order is finlished for 150s.otherwise cancel the order
        if myOper != 'Idle':
            if myOper == 'Sell':
                orderId = mySell['orderId']
            elif myOper == 'Buy':
                orderId = myBuy['orderId']
            for i in range(30):
                checkTrade = client.get_order(symbol='XVGBTC', orderId=orderId)
                # {'symbol': 'XVGBTC', 'orderId': 37483565, 'clientOrderId': '502U4xz0h26U4qMnVEe3DF', 'price': '0.00000715',
                #  'origQty': '200.00000000', 'executedQty': '200.00000000', 'status': 'FILLED', 'timeInForce': 'GTC',
                #  'type': 'LIMIT', 'side': 'SELL', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1526221430207,
                #  'isWorking': True}
                if checkTrade['status'] == 'FILLED' or checkTrade['status'] == 'CANCELED':
                    break
                time.sleep(5)

            # 7.cancel the order
            if checkTrade['status'] != 'FILLED' and checkTrade['status'] != 'CANCELED':
                cancelTrade = client.cancel_order(symbol='XVGBTC', orderId=orderId)
                print("The Trade is failed.Cancel this order!")
                #bot.file_helper.send("The Trade is failed.Cancel this order!")
            time.sleep(5)
        errCount = 0
    except Exception:
        errCount = errCount + 1
        print('Program Error!')
