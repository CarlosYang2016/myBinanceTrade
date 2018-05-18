# coding=utf-8
import time
from decimal import *
from binance.client import Client
from binance.exceptions import BinanceAPIException

viBTC = 0.3
viXVG = 43795  # 0.3/0.00000687

api_key = ''
api_secret = ''

# create the Binance client, no need for api key
client = Client(api_key=api_key, api_secret=api_secret)

# 1.初始化到50%XVG和50%BTC
count = 0
buyCount = 0
sellCount = 0
errCount = 0
while True:
    # 2.获取账户资产
    count = count + 1
    try:
        #print()
        #print('*'*20)
        #print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ' 执行第{}次监控。'.format(count))
        #print('执行过{}次卖出和{}次买入。'.format(sellCount,buyCount))
        myBTC = client.get_asset_balance(asset='BTC')
        # {'asset': 'BTC', 'free': '0.68327561', 'locked': '0.00000000'}
        myXVG = client.get_asset_balance(asset='XVG')
        #print('账户BTC资产: ',myBTC['free'],'账户XVG资产:',myXVG['free'])
        # 3.获取最新的BTC价格
        # priceBTC = client.get_symbol_ticker(symbol = 'BTCBTC')
        # {'symbol': 'BTCBTC', 'price': '0.00154130'}
        priceXVG = client.get_symbol_ticker(symbol='XVGBTC')
        print(priceXVG['price'])	#'最新的XVG价格: ',
        # 使用买2价作为买价，以卖2价作为卖价
        #bidAsk = client.get_order_book(symbol='XVGBTC', limit=10)
        #sellPrice = bidAsk['bids'][1][0]
        #print('卖2价: ', sellPrice)
        #buyPrice = bidAsk['asks'][1][0]
        #print('买2价: ', buyPrice)
        sellPrice = priceXVG['price']
        buyPrice = priceXVG['price']
        # 4.计算当前价格下的BTC资产比例
        assetActXVG = float(myXVG['free']) * float(priceXVG['price'])  # BTC价值
        assetXVG = assetActXVG + viXVG * float(priceXVG['price'])
        assetActBTC = float(myBTC['free'])
        assetBTC = assetActBTC + viBTC
        #计算当前价格下的XVG资产比例
        print('XVG资产比例: ',assetXVG/(assetXVG + assetBTC))

        myOper = 'Idle'

        if assetXVG/(assetXVG + assetBTC) > 0.503:
            print('XVG价值变高达到: ', assetXVG/(assetXVG + assetBTC))
            # 卖出XVG
            # 卖出XVG个数--必须是整数
            sellXVG = int((assetXVG - assetBTC) / (2 * float(priceXVG['price'])))
            if (sellXVG > int(float(myXVG['free']))) and (assetActXVG > 0.001):
                sellXVG = int(float(myXVG['free']))
            print('卖出XVG个数: ', sellXVG)
            if assetActXVG > 0.001:
                try:
                    mySell = client.order_limit_sell(symbol='XVGBTC', quantity=Decimal(str(sellXVG)), price=sellPrice)
                    # {'symbol': 'XVGBTC', 'orderId': 37475851, 'clientOrderId': 'Xhq837HZAIKRrgd4c97Ey1', 'transactTime': 1526217559759,
                    #  'price': '0.00000728', 'origQty': '500.00000000', 'executedQty': '0.00000000', 'status': 'NEW',
                    #  'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'SELL'}
                    myOper = 'Sell'
                    #print('执行卖出XVG操作，卖出价格: ',sellPrice)
                    msg = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '以{}的价格卖出{}个XVG'.format(sellPrice, sellXVG)
                    print(msg)
                    #bot.file_helper.send(msg)
                    sellCount = sellCount + 1
                except BinanceAPIException:
                    print("卖出XVG错误")
            else:
                print("没有足够的XVG个数可卖了")
        elif assetXVG/(assetXVG + assetBTC) < 0.49:
            print('XVG价值变低达到: ', assetXVG/(assetXVG + assetBTC))
            # 买入XVG
            # 买入个数
            buyXVG = int((assetBTC - assetXVG) / (2 * float(priceXVG['price'])))
            if buyXVG > int(assetActBTC/float(buyPrice)) and assetActBTC > 0.001:
                buyXVG = int(assetActBTC/float(buyPrice))
            print('买入XVG个数: ', buyXVG)

            if assetActBTC > 0.001:
                try:
                    myBuy = client.order_limit_buy(symbol='XVGBTC', quantity=Decimal(str(buyXVG)), price=buyPrice)
                    myOper = 'Buy'
                    #print('执行买入XVG操作，买入价格: ',buyPrice)
                    msg = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '以{}的价格买入{}个XVG'.format(buyPrice,buyXVG)
                    print(msg)
					#bot.file_helper.send(msg)
                    buyCount = buyCount + 1
                except BinanceAPIException:
                    print("买入XVG错误")
            else:
                print("没有足够的BTC买XVG了")
        else:
            pass
            #print("正常监控，没有处罚交易条件")
        # 5.延时5s
        time.sleep(5)
        # 6.查看交易是否完成，循环5次，没有完成则取消交易

        if myOper != 'Idle':
            if myOper == 'Sell':
                orderId = mySell['orderId']
            elif myOper == 'Buy':
                orderId = myBuy['orderId']
            for i in range(30):
                #print("查看交易是否完成...")
                checkTrade = client.get_order(symbol='XVGBTC', orderId=orderId)
                # {'symbol': 'XVGBTC', 'orderId': 37483565, 'clientOrderId': '502U4xz0h26U4qMnVEe3DF', 'price': '0.00000715',
                #  'origQty': '200.00000000', 'executedQty': '200.00000000', 'status': 'FILLED', 'timeInForce': 'GTC',
                #  'type': 'LIMIT', 'side': 'SELL', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1526221430207,
                #  'isWorking': True}
                if checkTrade['status'] == 'FILLED' or checkTrade['status'] == 'CANCELED':
                    break
                time.sleep(5)

            # 7.10次检查都失败了，取消该订单
            if checkTrade['status'] != 'FILLED' and checkTrade['status'] != 'CANCELED':
                cancelTrade = client.cancel_order(symbol='XVGBTC', orderId=orderId)
                print("交易失败了，取消该订单")
                #bot.file_helper.send("交易失败了，取消该订单")
            time.sleep(5)
        errCount = 0
    except Exception:
        errCount = errCount + 1
        print('程序报错')

    # if errCount > 5:    #连续5次报错进行通知
    #     bot.file_helper.send('程序连续5次报错')
