import requests
import pandas as pd
from datetime import datetime 
import matplotlib.pyplot as plt
import seaborn as sns

def osmosis_api(token, minutes):
    api_url = "https://api-osmosis.imperator.co/tokens/v2/historical/"+token+"/chart?tf="+str(minutes)
    response = requests.get(api_url)
    data = response.json()
    ohlc = pd.DataFrame(data) 
    ohlc['datetime']= ohlc['time'].apply(lambda d: datetime.fromtimestamp(int(d)).strftime('%d-%m-%Y %H:%M'))
    ohlc['datetime']=pd.to_datetime(ohlc['datetime'],format='%d-%m-%Y %H:%M')
    ohlc.set_index('datetime', inplace= True)
    price = pd.DataFrame(ohlc['close'])
    price.columns = [token]
    return price   

price= osmosis_api("EVMOS",60)

price.tail(10)

price['date']=price.index.date
price['time']=price.index.time

daily_mean = price.EVMOS.groupby(price['date']).mean()
daily_mean.columns=['date','mean']
daily_mean

mean=price.groupby('date')['EVMOS'].mean()
evmos_dev= pd.merge(left=price, right=mean, left_on='date', right_on='date', how='left',suffixes=('_price','_mean'))

evmos_dev['dev_from_mean']=evmos_dev['EVMOS_price']-evmos_dev['EVMOS_mean']
evmos_dev['dev_from_mean'].describe()

evmos_dev.tail(5)

evmos_dev.reset_index().set_index(['date','time'])


evmos_dev_pp = pd.pivot_table(evmos_dev, values='dev_from_mean', index=['date'],
                    columns=['time'])
sns.heatmap(data=evmos_dev_pp,center=0,cmap="YlGnBu")
plt.show()

evmos_dev.tail(25)

time_dev = evmos_dev.groupby('time').dev_from_mean.mean()

time_dev.plot(kind='bar')
plt.show()

time_dev

price['weekday']=price.index.weekday
price

buytime = 1
selltime =15
buysell= price[(price.index.hour == buytime )| (price.index.hour== selltime)]
buysell

# Create a dictionary that maps integers to strings
mapping = {buytime:'buy', selltime:'sell'}

# Convert the 'bad_conditions' integers to strings using the 'mapping'
buysell['signal'] = buysell.index.hour.map(mapping)


buysell['return']= buysell.EVMOS.pct_change()
buysell.dropna()
buysell.sort_values(by='return')

sns.lmplot(data=buysell, y= 'return',x='weekday',hue='signal')

