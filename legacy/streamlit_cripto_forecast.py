import streamlit_stock_forecast as st
import requests
from datetime import datetime
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objects as go
import pandas as pd

# Configuración de CryptoCompare API
API_KEY = 'cf6313921d5ef0e4942ed6352948d3631051b44f6de6116dab33ffaaad9411bf'
headers = {'Authorization': 'Apikey ' + API_KEY}

# Fechas de inicio y hoy
START = '2015-01-01'
TODAY = datetime.now()

st.title("Crypto Market Prediction App")

# Selección de criptomonedas
cryptos = ("BTC", "ETH", "XRP", "LTC")
selected_crypto = st.selectbox("Selected dataset for prediction", cryptos)

n_years = st.slider("Years of prediction:", 1, 4)
period = n_years * 365

# Carga de datos utilizando CryptoCompare API
@st.cache_data
def load_data(symbol):
    url = f'https://min-api.cryptocompare.com/data/v2/histoday'
    parameters = {
        'fsym': symbol,
        'tsym': 'USD',
        'limit': '2000',  # Número máximo de días para datos históricos
        'toTs': int(datetime.now().timestamp())  # Convertir la fecha actual en un timestamp Unix
    }
    response = requests.get(url, headers=headers, params=parameters)
    response_data = response.json()
    if response.status_code == 200 and response_data.get("Response") != "Error":
        data = pd.DataFrame(response_data['Data']['Data'])
        data['timestamp'] = pd.to_datetime(data['time'], unit='s')
        data['close'] = data['close']
        return data[['timestamp', 'close']]
    else:
        st.error(f"Failed to fetch data: {response_data.get('Message', 'Unknown error')}")
        return pd.DataFrame()

data_load_state = st.text("Load data...")
data = load_data(selected_crypto)
data_load_state.text("Loading data...done!")

st.subheader('Datos históricos de la criptomoneda')
st.write(data.tail())

# Visualización de datos brutos
def plot_raw_data():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['timestamp'], y=data['close'], name=f'Precio de cierre de {selected_crypto}'))
    fig.layout.update(title_text=f'Serie Temporal del Precio de Cierre de {selected_crypto}', xaxis_title='Fecha', yaxis_title='Precio de cierre (USD)', xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)

plot_raw_data()

# Forecasting
df_train = data.rename(columns={'timestamp': 'ds', 'close': 'y'})

m = Prophet()
m.fit(df_train)
future = m.make_future_dataframe(periods=period)
forecast = m.predict(future)

st.write('Datos de la predicción')
st.write(forecast.tail())

fig_future = plot_plotly(m, forecast)
st.plotly_chart(fig_future, use_container_width=True)

st.write('Componentes del pronóstico')
fig_components = m.plot_components(forecast)
st.write(fig_components)