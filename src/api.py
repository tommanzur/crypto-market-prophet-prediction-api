from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from prophet import Prophet
from prophet.plot import plot_components_plotly
from dependencies import authenticate_user, create_access_token, get_current_user
from data import load_data
import config

router = APIRouter()

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Generates an access token for authenticated users."""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get('/api/data/{symbol}/{years}')
async def get_historical_data(request: Request, symbol: str, years: int, token: str = Depends(get_current_user)):
    """Retrieves historical data for a specified symbol and number of years."""
    start_date = (datetime.now() - timedelta(days=years * 365)).strftime('%Y-%m-%d')
    data = load_data(symbol, start_date)
    return data.to_dict(orient='records')

@router.get('/api/forecast/{symbol}/{years}/{forecast_years}')
async def get_forecast(request: Request, symbol: str, years: int, forecast_years: int, token: str = Depends(get_current_user)):
    """Provides a forecast for the specified symbol over a number of years based on historical data."""
    start_date = (datetime.now() - timedelta(days=years * 365)).strftime('%Y-%m-%d')
    data = load_data(symbol, start_date)
    df_train = data.rename(columns={'timestamp': 'ds', 'close': 'y'})
    m = Prophet()
    m.fit(df_train)
    future = m.make_future_dataframe(periods=forecast_years * 365)
    forecast = m.predict(future)
    fig_components = plot_components_plotly(m, forecast)
    forecast['ds'] = forecast['ds'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    forecast_json = {
        "components_plot": fig_components.to_json(),
        "forecast_data": forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_dict(orient='records')
    }
    return JSONResponse(content=forecast_json)
