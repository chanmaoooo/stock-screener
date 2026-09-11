import os
from pathlib import Path
from datetime import date

import pandas as pd
from dotenv import load_dotenv

load_dotenv()
DATA_DIR = Path(os.environ['STOCK_DATA_DIR'])


SBI_URL = (
    'https://search.sbisec.co.jp/v2/popwin/info/stock/'
    'pop6040_usequity_list.html'
)


def check_sbi_stock_list():
    tables = pd.read_html(
        SBI_URL,
        encoding = 'cp932',
    )

    print(f'Number of tables: {len(tables)}')
    for i,table in enumerate(tables):
        print(f'\n--- table {i} ---')
        print(table.head())
        print(table.columns)



def fetch_sbi_stock_list():
    tables = pd.read_html(
        SBI_URL,
        encoding = 'cp932',
    )


    stock_table = tables[4]

    # 気持ちエラー処理をしておくが、基本的には実行前に↑が米国株テーブルかどうか目視確認しよう
    required_columns = ['ティッカー', '銘柄（英語）', '市場']
    if not all(column in stock_table.columns for column in required_columns):
        raise ValueError(
            'this table does not appear to be the SBI stock table.'
        )

    stock_table = stock_table[['ティッカー', '銘柄（英語）', '市場']].copy()
    stock_table = stock_table.rename(
        columns={
            'ティッカー': 'Ticker',
            '銘柄（英語）': 'Company',
            '市場': 'Exchange',
        }
    )

    return stock_table


def update_master(current_stocks):
    output_dir = DATA_DIR / 'master'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'master.csv'

    today = date.today().isoformat()


    if not output_path.exists():
        master = current_stocks.copy()
        master['FirstSeen'] = today
        master['Status'] = 'active'

        master.to_csv(
            output_path,
            index=False,
            encoding='utf-8',
        )

        print(f'Created master: {len(master)} stocks')
        return


    master = pd.read_csv(
        output_path,
        encoding='utf-8',
    )

    current_tickers = set(current_stocks['Ticker'])
    master_tickers = set(master['Ticker'])

    new_tickers = current_tickers - master_tickers
    missing_tickers = master_tickers - current_tickers

    master.loc[
        master['Ticker'].isin(current_tickers),
        'Status',
    ] = 'active'

    master.loc[
        master['Ticker'].isin(missing_tickers),
        'Status',
    ] = 'inactive'

    new_stocks = current_stocks[
        current_stocks['Ticker'].isin(new_tickers)
    ].copy()

    new_stocks['FirstSeen'] = today
    new_stocks['Status'] = 'active'

    master = pd.concat(
        [master, new_stocks],
        ignore_index = True,
    )

    master = master.sort_values('Ticker')

    print(f'New stocks: {len(new_tickers)}')
    print(f'Inactive stocks: {len(missing_tickers)}')
    print(f'Total stocks in master: {len(master)}')



def main():
    # テーブル番号手動確認用
    # check_sbi_stock_list()

    current_stocks = fetch_sbi_stock_list()
    print(current_stocks.head())
    print(f'Current SBI stocks: {len(current_stocks)}')

    update_master(current_stocks)




if __name__ == '__main__':
    main()
