import yfinance as yf

ticker = 'AAPL'

data = yf.download(
    ticker,
    period='1mo',
    interval='1d',
)

print(data)
