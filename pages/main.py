"""
Table of tock instruments

"""
#import itertools
import pandas as pd
import sqlite3 as db
from dash import callback_context
from dash import dcc, html, register_page

import dash_bootstrap_components as dbc

import yfinance as yf

# Путь до главной БД
MWDb = 'c:\Inetpub\wwwroot\DB\MarketWind.db'
# Рабочие модели для главной страницы сайта
Work_Folder = "C:/inetpub/wwwroot/Engine/"
Models_Folder = "Models/"

cnxx = db.connect(Work_Folder + Models_Folder + 'QuotesSettings.sqlite3')
df = pd.read_sql_query("SELECT Quote, Price0, Quantity0 FROM Parameters", cnxx)
cnxx.close()
equities = []
prices = []
lastprices = []
quantities = []
curquantities = []
created = []
changed = []
volumes = []
profit_abs = []
profit_percent = []
iLI = df.last_valid_index()
iFV = df.first_valid_index()
while iFV <= iLI:
    quote = df.loc[iFV]['Quote']
    print("Dispatching " + quote + "...")

    readYFianance = 0
    acctbl = db.connect(Work_Folder + Models_Folder + "acc_table.sqlite3")
    # load local  acc table if exist
    try:
        query = "SELECT Shortname FROM NAMES WHERE Ticker = \'" + quote + "\'"
        accname = pd.read_sql_query(query, acctbl)
        if len(accname.index) > 0:
            print(accname.loc[0]['Shortname'])
            equities.append([quote, accname.loc[0]['Shortname']])
        else:
            readYFianance = 1# table is exists but has not a ticker
    except Exception as e: 
        print (str(e))
        # no table, create it from Yahoo Finance
        c = acctbl.cursor()
        c.execute("CREATE TABLE NAMES(Ticker TEXT, Shortname TEXT)")
        c.close()
        readYFianance = 1

    # load names from Yahoo Finance
    if readYFianance == 1:
        try: # NYSE NASDAQ tickers
            to_yf = quote
            name = yf.Ticker(to_yf)
            company_name = name.info['shortName']
            values = "VALUES(\'" + quote + "\', \'" + company_name + "\')"
            query = "INSERT INTO NAMES(Ticker, Shortname) " + values
            equities.append([df.loc[iFV]['Quote'], name.info['shortName']])
            
        except:
            try: # MOEX tickers
                to_yf = quote + ".ME"
                name = yf.Ticker(to_yf)
                company_name = name.info['shortName']
                values = "VALUES(\'" + quote + "\', \'" + company_name + "\')"
                query = "INSERT INTO NAMES(Ticker, Shortname) " + values
                equities.append([df.loc[iFV]['Quote'], name.info['shortName']])

            except: # unknown
                equities.append([quote, quote])
                values = "VALUES(\'" + quote + "\', \'" + quote + "\')"
                query = "INSERT INTO NAMES(Ticker, Shortname) " + values
        
        c = acctbl.cursor()
        c.execute(query)
        acctbl.commit()

    acctbl.close()

    prices.append(df.loc[iFV]['Price0'])
    quantities.append(df.loc[iFV]['Quantity0'])

    model = df.loc[iFV]['Quote'] + ".sqlite3"
    try:
        cnxxc = db.connect(Work_Folder + Models_Folder + model)
        dfm = pd.read_sql_query("SELECT Time, BudgetQuantity, ChangeT0, BudgetBalance, Comission FROM Market ORDER BY Time DESC", cnxxc)
        #last deviation percentage of price from T0
        changed.append(dfm.iloc[dfm.first_valid_index()][2])
        #current quantity of the model
        curquantities.append(dfm.iloc[dfm.first_valid_index()][1])
        #time of creation of the model
        created.append(dfm.iloc[dfm.last_valid_index()][0])
        # get balancies from start and now
        balT0 = dfm.iloc[dfm.last_valid_index()][3]
        balCur= dfm.iloc[dfm.first_valid_index()][3]
        #calculating profit
        comm = dfm.iloc[dfm.first_valid_index()][4]
        prabs = balCur - balT0  - comm
        profit_abs.append(prabs)
        prpr = ((prabs * 100.0) / (balT0/2.0))
        profit_percent.append(prpr)

        #start money volume
        volumes.append(balT0/2.0)

        #last known market price
        try:
            dfa = pd.read_sql_query("SELECT Price FROM Analisys ORDER BY Time DESC LIMIT 1", cnxxc)
            lastprices.append(dfa.iloc[dfa.first_valid_index()][0])
        except:
            lastprices.append(0.0)
            
        cnxxc.close()
    except Exception as e: 
        print (str(e))

        print("Error during working with ", model)
        print("Market Table is needs!")
        changed.append(0.0)
        curquantities.append(0)
        created.append("Unknown")
        lastprices.append(0.0)
        profit_abs.append(0.0)
        profit_percent.append(0.0)
        volumes.append(0)

    iFV += 1

data = {
    "Equities": [f"[{stock}](/stocks/{ticker})" for stock, ticker in equities],
    "Created": [f"{tm}" for tm in created],
    "Start Items": [f"{qu}" for qu in quantities],
    "Start Volume, $": [f"{v}" for v in volumes],
    "Enter Price, $": [f"{pr}" for pr in prices],
    "Cur. Items": [f"{cqu}" for cqu in curquantities],
    "Last Price, $": [f"{lpr}" for lpr in lastprices],
    "Price Changed %": [f"{ch}" for ch in changed],
    "Profit Abs, $": [f"{prabs}" for prabs in profit_abs],
    "Profit %": [f"{prpr}" for prpr in profit_percent],
}

df = pd.DataFrame(data)

# dash.DataTable with links formatted by setting the column to  "presentation": "markdown"
#datatable = dash_table.DataTable(
#    data=df.to_dict("records"),
#    columns=[{"id": "Equities", "name": "Equities", "presentation": "markdown"}]
#    + [{"id": c, "name": c} for c in df.columns if c != "Equities"],
#    markdown_options={"link_target": "_self"},
#    css=[{"selector": "p", "rule": "margin: 0; width: 98vw;"}],
#    style_cell={"textAlign": "right"},
#    id='tbl_main',
#    style_data_conditional=[{
#            'if': {
#                'column_id': 'Equities',
#            },
#            'backgroundColor': 'dodgerblue',
#            'color': 'white'
#        },
#    ]
#)

# html table with links formatted using dcc.Link()
df["Equities"] = [
    dcc.Link(f"{stock}", href=f"/stocks/{ticker}", id= f"the_{ticker}") for ticker, stock in equities
]
df["Cur. Items"] = [
    dcc.Link(f"{trades}" , href=f"/trades/{ticker[0]}", id= f"trade_{ticker[0]}") for trades,ticker in zip(curquantities, equities)
]

table = dbc.Table.from_dataframe(df, striped = True, bordered=True, hover=True)

# pop up text Loading....
def make_popover(ticker):
    return dbc.Popover(
        "Loading, please wait.",
        body=True,
        target=f"the_{ticker}",
        id=f"pop_{ticker}",
        trigger="legacy",
    )

to_layout = []
to_layout.append(table)
for t,n in equities:
    to_layout.append(make_popover(t))

# show finished layout
layout = html.Div(
    to_layout,
    #datatable,  -  for colors into cells
    id = 'portfolio_page',
    
)
