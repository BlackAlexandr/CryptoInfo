"""
Table of tock instruments

"""
#import itertools
import pandas as pd
import sqlite3 as db

import dash_bootstrap_components as dbc

import yfinance as yf

from .main import Work_Folder
from .main import Models_Folder

def GetMarketsData():
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

    counter = 0
    result = []
    while counter < len(quantities):
            result.append(
                    {
                        "Stocks": equities[counter][0],
                        "Equities": equities[counter][1],
                        "Created": str(created[counter]),
                        "StartItems":  str(quantities[counter]),
                        "StartVolume": str(round(volumes[counter], 3)),
                        "EnterPrice": str(round(prices[counter], 3)),
                        "CurItems": str(curquantities[counter]),
                        "LastPrice": str(round(lastprices[counter], 3)),
                        "PriceChanged": str(round(changed[counter], 3)),
                        "ProfitAbs": str(round(profit_abs[counter], 3)),
                        "Profit": str(round(profit_percent[counter], 3))
                    }
                )  
            counter += 1      


    return result

def GetGraphData(ticker=None, **other_unknown_query_strings):
    result = [];
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
        ind_pr = [] #profit of the index    
        # calc profit of instrument
        iLI = df.last_valid_index()
        legendaAlgo  = 0  # get last value
        legendaQuote = df.loc[df.last_valid_index()]['ChangeT0']# get last value   

        for i in range(0, iLI, 1):
            Estimate = float(df.loc[i]['BudgetQuantity']) * iLotSz0 * float(df.loc[i]['Price'])
            EstimateT0 = (EstimateT0Pure + (EstimateT0Pure - df.loc[i]['BudgetMoney'] ))
            dPar = (((Estimate - df.loc[i]['Comission'])- EstimateT0) / EstimateT0Pure ) * 100.0
            if  i == (iLI - 1):
                legendaAlgo = dPar
                result.append(
                        {
                            "time": str(df['Time'][i]),
                            "profit": round(dPar, 3),
                            "changeT0": round(df['ChangeT0'][i], 3),
                            "legendaAlgo": round(legendaAlgo, 2),
                            "legendaQuote": round(legendaQuote, 2)
                        }
                ) 
            else: 
                result.append(
                        {
                            "time": str(df['Time'][i]),
                            "profit": round(dPar, 3),
                            "changeT0": round(df['ChangeT0'][i], 3),
                        }
                ) 
            
        
    return result

