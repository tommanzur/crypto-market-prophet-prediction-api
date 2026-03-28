from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from statsforecast import StatsForecast
from statsforecast.models import AutoARIMA
from dependencies import authenticate_user, create_access_token, get_current_user
from data import load_data
import config
import pandas as pd
import plotly.graph_objects as go

router = APIRouter()

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get('/api/data/{symbol}/{years}')
async def get_historical_data(request: Request, symbol: str, years: int, token: str = Depends(get_current_user)):
    start_date = (datetime.now() - timedelta(days=years * 365)).strftime('%Y-%m-%d')
    data = load_data(symbol, start_date)
    return data.to_dict(orient='records')

@router.get('/api/forecast/{symbol}/{years}/{forecast_years}')
async def get_forecast(request: Request, symbol: str, years: int, forecast_years: int, token: str = Depends(get_current_user)):
    start_date = (datetime.now() - timedelta(days=years * 365)).strftime('%Y-%m-%d')
    data = load_data(symbol, start_date)

    df = data.copy()
    df['ds'] = pd.to_datetime(df['timestamp'])
    df['y'] = df['close'].astype(float)
    df['unique_id'] = symbol
    df = df[['unique_id', 'ds', 'y']].sort_values('ds')

    h = forecast_years * 365
    sf = StatsForecast(models=[AutoARIMA(season_length=7)], freq='D', n_jobs=1)
    sf.fit(df)
    pred = sf.predict(h=h, level=[80]).reset_index()

    pred = pred.rename(columns={
        'AutoARIMA': 'yhat',
        'AutoARIMA-lo-80': 'yhat_lower',
        'AutoARIMA-hi-80': 'yhat_upper',
    })
    pred['ds'] = pred['ds'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    forecast_data = pred[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_dict(orient='records')

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=pred['ds'], y=pred['yhat'], name='Forecast', line=dict(color='#feb236')))
    fig.add_trace(go.Scatter(x=pred['ds'], y=pred['yhat_upper'], name='Upper bound', line=dict(width=0), showlegend=False))
    fig.add_trace(go.Scatter(x=pred['ds'], y=pred['yhat_lower'], name='Lower bound', fill='tonexty', fillcolor='rgba(254,178,54,0.15)', line=dict(width=0), showlegend=False))
    fig.update_layout(title='Forecast Components', xaxis_title='Date', yaxis_title='Price (USD)', template='plotly_dark')

    return JSONResponse(content={
        "components_plot": fig.to_json(),
        "forecast_data": forecast_data,
    })
