"""
Shows tables with last 100 trades in stock instrument
"""

from .main import Work_Folder
from .main import Models_Folder

GRAPH_STYLE = {
    "margin-left": "0%",
    "height": "90vh",
    "width": "98vw"
}

import dash
import pandas as pd
import sqlite3 as db
import dash_bootstrap_components as dbc

def title(ticker=None):
    return f"{ticker} - last trades"


def description(ticker=None):
    return f"Last trades for {ticker}"


dash.register_page(
    __name__,
    path_template="/trades/<ticker>",
    title=title,
    description=description,
    path="/trades/<ticker>",
)

limit_records = 300
def layout(ticker=None, **other_unknown_query_strings):
    if ticker is not None:
        dbfile = 'file:///' + Work_Folder + Models_Folder + ticker + '.sqlite3' + '?mode=ro'
        # Dataframe from trading DB of the Ticker
        cnx = db.connect(dbfile, uri=True)
        df = pd.read_sql_query("SELECT Time, Price, Change, BudgetQuantity FROM Market ORDER BY Time DESC LIMIT " + str(limit_records + 1), cnx)
        
        df['Time'] = pd.to_datetime(df['Time'])
        df['Price'] = df['Price'].astype(float)
        df['Change'] = df['Change'].astype(float)
        df['BudgetQuantity'] = df['BudgetQuantity'].astype(int)

        real_count = df['Time'].count() - 1
        actions = []

        index = 1
        for q in df['BudgetQuantity']:
            actions.append(q - df['BudgetQuantity'][index])
            if index == real_count:
                break

            index += 1
        actions.append('not valid')
        
        #for (a, b, c) in zip(num, color, value):
        #    print (a, b, c)
    
        data = {
            "Time": [f"{tm}" for tm in df['Time']],
            "Items": [f"{cqu}" for cqu in df['BudgetQuantity']],
            "Action": [f"{ac}" for ac in actions],
            "Price, $": [f"{pr}" for pr in df['Price']],
            "Price Deviation %": [f"{ch}" for ch in df['Change']],
            
        }

        df = pd.DataFrame(data)

        table = dbc.Table.from_dataframe(df, striped = True, bordered=True, hover=True)
        return table

    return dash.html.H3(f"Financial and Technical Analysis for: {ticker}")
