#lots of the indicators I am using are for like long term stuff and they really don't work here but I needed data points to test
#I think this works properly, it is just that there is not much 

from ast import Num
from pickle import TRUE
from typing import Counter
import cbpro
import time
import random
import numpy as np
import pandas as pd
import csv

keys = open(r'C:\Users\lukegillespie\VSC\CrytoBot\passphrase').read().splitlines() #gets the codes to my coinbase account

passphrase = keys[0]
secret = keys[1]
public = keys[2]

auth_client = cbpro.AuthenticatedClient(public, secret, passphrase) #uses the keys to talk to the coinbase API

#these are the lists of data that I am collecting
price_array = []
average5_array = [0]
change = [0]
RSI_array = []
profit_array = []
profit_change_array = [0]
aroon_array = []
bitcoin_array = []
roc_array = []
buy_array = []
sell_array = []     

#in case you want to change the amount bought
sell_percent = 1
buy_percent = 1

#just declaring some variables
starting_funds = 1000
profit = 0
current_funds = 0
counter2 = 1
price = 0
bitcoin_value = 0
bitcoin = 0 

#counters for the loop
counter = 1
model_counter = 1000
aroon_period = 25
RSI_period = 10
roc_period = 10
#these just fill in the arrays with 0's so that they are all matching in size, I should remove this begining data from the csv
for x in range(0,RSI_period):
    RSI_array.append(0)
for x in range(0,aroon_period):
    aroon_array.append(0)
for x in range(0,roc_period):
    roc_array.append(0)

def RSI(): #relative strength index calculator
    global change, RSI_period, RSI_array
    gain = []
    loss = []
    for i in change[-RSI_period:]:
        if i > 0:
            gain.append(i)
        else:
            new = abs(i)
            loss.append(new)
    av_gain = sum(gain)/RSI_period
    av_loss = sum(loss)/RSI_period
    if av_loss == 0:
        RSI = 100
        RSI_array.append(RSI)
        return RSI
    else:
        RS = av_gain/av_loss
        RSI = 100 - (100/(1+RS))
        RSI_array.append(RSI)
        return RSI

def aroon(): #aroon indicator calculator
    global price_array, aroon_period
    array = price_array[-aroon_period:]
    maxi = max(array)
    mini = min(array)
    maxindex = array.index(maxi)
    minindex = array.index(mini)
    periods_since_high = len(array) - maxindex
    periods_since_low = len(array) - minindex
    up = 100 * (aroon_period - periods_since_high)/ aroon_period
    down = 100 * (aroon_period - periods_since_low)/ aroon_period
    oscillator = up - down
    aroon_array.append(oscillator)
    return oscillator

def checkprofit_every5(): #this just checks the profit and let's you know how much you have made
    global bitcoin, bitcoin_value, profit, counter, price, current_funds, starting_funds
    if counter % 5 == 0:
        bitcoin_value = (bitcoin*price)
        profit = current_funds + bitcoin_value - starting_funds
        print("Current profit: ", profit)

def checkprofit(): #adds the profit and the amount of bitcoin in possesion to the arrays
    global bitcoin, bitcoin_value, profit, counter, price, current_funds, starting_funds, bitcoin_array
    bitcoin_value = (bitcoin*price)
    profit = current_funds + bitcoin_value - starting_funds
    #print("Current profit: ", profit)
    profit_array.append(profit)
    bitcoin_array.append(bitcoin)

def cal_change(): #function that looks at the change of price every 5 loops
    global price_array, change, average5_array
    diff = price_array[-1] - price_array[-2]
    change.append(diff)
    av_change = sum(change[-5:])/5
    average5_array.append(av_change)

def roc(): #price rate of change indicator (ROC)
    global price_array, roc_array, roc_period
    roc = ((price_array[-1] - price_array[-roc_period])/price_array[-roc_period]) * 100
    roc_array.append(roc)

def buy(): #executes a simulated buy, notice you cannot buy if no funds
    global bitcoin,buy_percent,current_funds,price
    #buy_change()
    if current_funds != 0:
        buying = current_funds / price
        current_funds = 0 
        bitcoin = buying
        bs_arry(2)
        print("buy")
    else:
        print("I can't buy, I'm out of money!")
        print("got",current_funds,"of money")
        bs_arry(1)

def sell(): #executes a simulated sell, notice you cannot sell if no bitcoin
    global bitcoin,sell_percent,current_funds,price
    if bitcoin != 0:
        print(bitcoin)
        selling = bitcoin * sell_percent
        current_funds += selling*price
        bitcoin -= selling     
        bs_arry(3)
        print("sell")
    else:
        print("tried to sell but no coin",)
        print("got", bitcoin,"coin")
        bs_arry(1)

def random_buy_sell(): #this randomly buys and sells for the original model creation
    if  counter2 == 1 :
        buy()
        checkprofit()
    elif counter2 == 2: 
        sell()
        checkprofit()
    else:
        checkprofit()
        checkprofit_every5()
        bs_arry(1)

def bs_arry(num): #creates two arrays that indicate if a buy or sell was conducted
    global buy_array, sell_array
    if num == 1:
        buy_array.append(0)
        sell_array.append(0)
    elif num == 2:
        buy_array.append(1)
        sell_array.append(0)
    elif num ==3:
        buy_array.append(0)
        sell_array.append(1)

def profit_change_arrays_fun(): #calculates profit change every iteration
    global profit,profit_array, profit_change_array
    num = profit_array[-2] - profit
    profit_change_array.append(num)   

#the bot starts running here

while True:
    price = float(auth_client.get_product_ticker(product_id="BTC-USD")['price']) #gets the price of whatever coin, I have it at bitcoin right now 
    price_array.append(price)
    
    if counter == 1: #this just starts the loop by giving you some info
        start_price = price
        print("Using my money to buy 100 percent in at $", start_price)
        bitcoin = starting_funds / start_price
        print("Bitcoin purchased = ", bitcoin)
        current_funds = 0
        print("Funds remaining: $", current_funds)
        checkprofit()
        bs_arry(1)
    
    elif counter > RSI_period: #starts tracking RSI after a defined period
        cal_change()
        rsi = RSI()
        counter2 = random.randint(1,3) #random integer for the random buy sell (weird location but it works lol)
        if counter <= model_counter: # this is the random buy sell...again this was a weird place looking at it again but whatever it works, I should probably move it out of this if loop
            random_buy_sell()
    else: #this just keeps adding stuff to the arrays if we are still below the period requirements
        checkprofit() 
        cal_change()
        bs_arry(1)
    
    if counter > 1: #adds the profit change array
        profit_change_arrays_fun()
    if counter > aroon_period: #the aroon calculator comes in at the defined period
        aroon()
    if counter > roc_period: # the ROC calculator comes in at its defined period
        roc()   

    if counter == model_counter: #builds the linear model at the defined time
        import model_builder #this calls the other script that builds the model
        with open('regression.csv', newline='') as f: #this grabs the coefficients of the linear regression function
            reader = csv.reader(f)
            coefs1 = list(reader)
            coefs2 = coefs1[0] #idk why but it leaves a second empty list in here
            coefs = []
            for x in coefs2: #floats the str values
                n = float(x)
                coefs.append(n)
            #print(coefs)
            #print(isinstance(coefs[0], float))

    if counter > model_counter: #so after the model is built the random buy/sell stops and follows the following parameters
        decision_buy = coefs[0]*price_array[-1] + coefs[1]*change[-1] + coefs[2]*average5_array[-1] + coefs[3]*RSI_array[-1] + coefs[4]*aroon_array[-1] + coefs[5]*bitcoin_array[-1] + coefs[6]*roc_array[-1] + coefs[7]*1 + coefs[8]*0 #I should proably make these interact with the dataframe so it isn't so manual 
        #this should give the estimated profit change if it would execute a buy at this moment from the regression model
        decision_sell = coefs[0]*price_array[-1] + coefs[1]*change[-1] + coefs[2]*average5_array[-1] + coefs[3]*RSI_array[-1] + coefs[4]*aroon_array[-1] + coefs[5]*bitcoin_array[-1] + coefs[6]*roc_array[-1] + coefs[7]*0 + coefs[8]*1
        #this should give the profit change if it would execute a sell at this moment according to the regression model
        decision_none = coefs[0]*price_array[-1] + coefs[1]*change[-1] + coefs[2]*average5_array[-1] + coefs[3]*RSI_array[-1] + coefs[4]*aroon_array[-1] + coefs[5]*bitcoin_array[-1] + coefs[6]*roc_array[-1] + coefs[7]*0 + coefs[8]*0
        #this is the profit change if the bot chooses to do nothing as estimated by the model
        if decision_sell > decision_buy and decision_sell > decision_none: #so if the profit change for the sell is higher than the buy and the none then it will sell
            sell()
            checkprofit()
        elif decision_buy > decision_sell and decision_buy > decision_none: # if the profit change for the buy is bigger than the sell and the do nothing then it will buy
            buy()
            checkprofit()
        else: #if none is bigger than buy and sell then nothing happens
            checkprofit()
            bs_arry(1)
    
    if counter > aroon_period and counter > roc_period and counter > RSI_period: #adds everything to the dataframe and throws it on a csv 
        d = {'profit change':profit_change_array,'profit':profit_array, 'price':price_array, 'price change':change, 'average5':average5_array, 
        'RSI':RSI_array, 'aroon':aroon_array, 'bitcoin':bitcoin_array, 'ROC':roc_array,'buy':buy_array, 'sell':sell_array}
        df = pd.DataFrame(data=d)
        df.to_csv('coin_data.csv', mode='w', index=False, header=True)
    
    #some prints for information on what's happening 
    print(len(profit_array), len(profit_change_array),
    len(price_array), len(change), len(average5_array), len(RSI_array), 
    len(aroon_array), len(bitcoin_array), 
    len(buy_array), len(sell_array), 
    len(roc_array), "funds",current_funds, "profit", profit) 

    counter +=1 #increase the counter every iteration
    #print(counter)
    time.sleep(2) #I leave this at 2 seconds so coinbase has enough time to update the price of the coin
