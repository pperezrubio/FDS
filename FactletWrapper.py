# -*- coding: utf-8 -*-
"""
Created on Thu Oct 30 11:16:16 2014

@author: dbi
"""
from Kratos_3 import *
from Kratos_3.Network import *
from Kratos_3.RunTimePlatform import *

import pandas as pd
import datetime


fsod = FactSetOnDemand()
config = fsod.getConfig()

# Set our configuration. We definitely need to set our username and password, as given to us by FactSet Support staff
config.setConfig(ConfigOptions.DataDirectUserName, "FDS_DEMO_FE_369354_SERVICES")
config.setConfig(ConfigOptions.DataDirectPassword, "UCqpU2d1foJq46Vw")


factlet = fsod.ExtractFormulaHistory("AAPL","p_price_open,p_price_high,p_price_low,p_price,p_volume_frq","20131006:20141014:D")

raw = []
for r in range(factlet.getNumberOfRows()):
    date = factlet.getCellAt(r, 1)
    op = factlet.getCellAt(r, 2)
    high = factlet.getCellAt(r, 3)
    low = factlet.getCellAt(r, 4)
    close = factlet.getCellAt(r, 5)
    vol = factlet.getCellAt(r, 6)
    raw.append((date, op,high,low,close,vol))	# store

data = pd.DataFrame(raw, columns=['Date','Open','High','Low','Close','Volume'])
data.Date = pd.tseries.tools.to_datetime(data.Date)
data = data.set_index('Date')

print (data)

"""
start_date = datetime.datetime(2001,1,10)
end_date = datetime.datetime(2005,12,31)

factlet1 = Factlet.ExtractFormulaHistory("AAPL","p_price_open,p_price_high,p_price_low,p_price,p_volume_frq",["dates","20131006:20141014:D"])
factlet2 = Factlet.ExtractFormulaHistory("AAPL","p_price_open,p_price_high,p_price_low,p_price,p_volume_frq",["dates",start_date.strftime("%m/%d/%Y") + ":" + end_date.strftime("%m/%d/%Y")+":Q"])


print (factlet1.getFactletResult())

print (factlet2.getFactletResult())		
"""