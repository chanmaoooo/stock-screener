import yfinance as yf

ticker = 'AAPL'

data = yf.download(
    ticker,
    period='1mo',
    interval='1d',
)

data.columns = data.columns.droplevel('Ticker')
data = data[['Open', 'High', 'Low', 'Close', 'Volume']]

print(data)

data.to_csv('sample_data/AAPL.csv')
