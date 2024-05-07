# Financial Forecasting API

This API allows users to authenticate and retrieve historical data and forecasts for various financial symbols. It uses FastAPI and is designed to be scalable and secure.

## Features

- User authentication for secure access.
- Rate limiting to prevent abuse.
- Retrieval of historical financial market data.
- Generation of financial forecasts using the Prophet library.

## Technologies Used

- FastAPI
- Prophet for time series forecasting
- Pydantic for data validation
- JWT for authentication
- SlowAPI for request rate limiting

## Installation

1. Clone the repository:
```Bash
git clone <repository-url>
```
2. Install dependencies:
```Bash
pip install -r requirements.txt
```
3. Run the server:
```Bash
uvicorn main:app --reload
```

## Usage

To use the API, you first need to authenticate to obtain a token, and then you can make requests to retrieve data or forecasts:

### Authentication

POST `/token`

```json
{
"username": "user",
"password": "password"
}
```
### Get Data
```Bash
GET /api/data/{symbol}/{years}
```
### Get Forecast
```Bash
GET /api/forecast/{symbol}/{years}/{forecast_years}
```
## Contributing

To contribute to the project, please send a pull request or open an issue to discuss proposed changes.



