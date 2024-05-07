from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from dependencies import authenticate_user, create_access_token, get_current_user
from prophet import Prophet
from datetime import timedelta, datetime
from data import load_data
import config
from limiter_setup import limiter

router = APIRouter()

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@limiter.limit("3/minute")
@router.get('/api/data/{symbol}/{years}')
async def get_data(request: Request, symbol: str, years: int, token: str = Depends(get_current_user)):
    start_date = (datetime.now() - timedelta(days=years * 365)).strftime('%Y-%m-%d')
    data = load_data(symbol, start_date)
    return data.to_dict(orient='records')

@limiter.limit("3/minute")
@router.get('/api/forecast/{symbol}/{years}/{forecast_years}')
async def get_forecast(request: Request, symbol: str, years: int, forecast_years: int, token: str = Depends(get_current_user)):
    start_date = (datetime.now() - timedelta(days=years * 365)).strftime('%Y-%m-%d')
    data = load_data(symbol, start_date)
    df_train = data.rename(columns={'timestamp': 'ds', 'close': 'y'})
    m = Prophet()
    m.fit(df_train)
    future = m.make_future_dataframe(periods=forecast_years * 365)
    forecast = m.predict(future)
    forecast['ds'] = forecast['ds'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    return JSONResponse(content=forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_dict(orient='records'))
