"""
Shows graph of profit for stock instrument
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
import plotly.graph_objects as go

def title(ticker=None):
    return f"{ticker} Analysis"


def description(ticker=None):
    return f"Dynamic profit for {ticker}"


def layout(ticker=None, **other_unknown_query_strings):
    if ticker is not None:
        dbfile = 'file:///' + Work_Folder + Models_Folder + ticker + '.sqlite3' + '?mode=ro'
        # Dataframe from trading DB of the Ticker
        cnx = db.connect(dbfile, uri=True)
        df = pd.read_sql_query("SELECT Time, BudgetQuantity, BudgetMoney, BudgetBalance, Price, ChangeT0, Comission, BudgetSyntheticProfit FROM Market", cnx)
        
        df['Time'] = pd.to_datetime(df['Time'])
        df['Price'] = df['Price'].astype(float)
        df['ChangeT0'] = df['ChangeT0'].astype(float)
        df['BudgetQuantity'] = df['BudgetQuantity'].astype(int)
        df['BudgetMoney'] = df['BudgetMoney'].astype(float)
        df['BudgetBalance'] = df['BudgetBalance'].astype(float)
        df['Comission'] = df['Comission'].astype(float)

        Quantity0 = df.loc[0]['BudgetQuantity']
        iPrice0 = df.loc[0]['Price']
        iLotSz0 = int(.5 + (df.loc[0]['BudgetMoney'] / (iPrice0*Quantity0)))
        EstimateT0Pure = Quantity0 * iLotSz0 * iPrice0

        Estimate = float(df.loc[0]['BudgetQuantity']) * iLotSz0 * float(df.loc[0]['Price'])     
        Balance = Estimate + df.loc[0]['BudgetMoney']

        iPt = df.first_valid_index()

        count_row = df.shape[0]  # gives number of row count   
        cnx.close()
        col = [] # profit of the algorithm
        ind_pr = [] #profit of the index    
        # calc profit of instrument
        iLI = df.last_valid_index()

        for i in range(0, iLI + 1, 1):
            Estimate = float(df.loc[i]['BudgetQuantity']) * iLotSz0 * float(df.loc[i]['Price'])
            EstimateT0 = (EstimateT0Pure + (EstimateT0Pure - df.loc[i]['BudgetMoney'] ))
            dPar = (((Estimate - df.loc[i]['Comission'])- EstimateT0) / EstimateT0Pure ) * 100.0
            col.append(dPar)
        
        begin = df.loc[0]['Time']
        last = df.loc[count_row-1]['Time'] 
        if begin >= last:
            return  go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 1, 2])])  
        
        legendaAlgo  = col[len(col) - 1]  # get last value
        legendaQuote = df.loc[df.last_valid_index()]['ChangeT0']# get last value   

        # web
        global fig
        fig = go.Figure()
        title_ticker='<span style="font-size: 22px;font-weight: bold;">' + ticker + ' - ' + str(count_row) + ' trades' + '</span>'
        fig.add_trace(go.Scatter(x = df['Time'], y = col, mode='lines', name= "Profit, %: " + "{:6.1f}".format(legendaAlgo), line=dict(color='green', width=2)))
        fig.add_trace(go.Scatter(x = df['Time'], y = df['ChangeT0'], mode='lines', name= ticker + ", %: " + "{:6.1f}".format(legendaQuote), line=dict(color='blue', width=2)))
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            title={
                
                'text': title_ticker,
                'y':0.98,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
                },
            legend=dict(
                x=0.7,
                y=0.99,
                traceorder='normal',
                font=dict(size=16,),
            ),
            annotations=[
                dict(
                    x=0.7,
                    y=0.99,
                    xref='paper',
                    yref='paper',
                    text='',
                    showarrow=False
                )
            ])        

        data = pd.DataFrame()   
        return dash.dcc.Graph(id='live-update-graph', figure = fig, style=GRAPH_STYLE, config={'displayModeBar': False, 'displaylogo': False})

    return dash.html.H3(f"Financial and Technical Analysis for: {ticker}")
