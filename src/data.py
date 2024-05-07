import requests
import pandas as pd
from datetime import datetime
from config import API_KEY
from fastapi import HTTPException

headers = {'Authorization': 'Apikey ' + str(API_KEY)}

def load_data(symbol, start_date):
    end_date = datetime.now().timestamp()
    url = 'https://min-api.cryptocompare.com/data/v2/histoday'
    parameters = {'fsym': symbol, 'tsym': 'USD', 'limit': 2000, 'toTs': end_date}
    response = requests.get(url, headers=headers, params=parameters)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Error fetching data from API")
    data = pd.DataFrame(response.json()['Data']['Data'])
    data['timestamp'] = pd.to_datetime(data['time'], unit='s')
    data['timestamp'] = data['timestamp'].dt.strftime('%Y-%m-%d')
    return data[data['timestamp'] >= start_date][['timestamp', 'close']]
