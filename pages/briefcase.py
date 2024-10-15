from dash import Dash, html, dcc, Output, Input, State, callback
import dash
import sqlite3 as db
from flask import session
from applocal import server
import pandas as cases
import urllib.request, json

# dash.register_page(__name__)

# layout = html.Iframe(
#     id == "case",
#     src="../assets/Profile/briefcase.html",
#     style={"width": "98vw", "height": "95vh", "margin-right": "1rem !important"},
# )


def GetMarkets(mwdb):
    conn = db.connect(mwdb)
    cursor = conn.cursor()
    qMarkets = "SELECT * from MARKETS"
    cursor.execute(qMarkets)
    markets = cursor.fetchall()
    result = []
    for market in markets:
        result.append({"id": market[0], "text": market[1]})

    conn.close()
    return result


def GetCompanies(mwdb, idMarket):
    conn = db.connect(mwdb)
    result = []
    # Для получения данных о крипте, берем внешний источник
    if idMarket == "1":
        data = ""
        with urllib.request.urlopen(
            "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd"
        ) as url:
            data = json.load(url)
        cursor = conn.cursor()
        for crypto in data:
            qCompanies = (
                "select * from COMPANIES WHERE MarketID = '{}' And Name == '{}'".format(
                    idMarket, crypto["name"]
                )
            )
            cursor.execute(qCompanies)
            company = cursor.fetchone()
            if company != None:
                result.append(
                    {
                        "Id": company[0],
                        "Name": company[1],
                        "current_price": "$" + str(crypto["current_price"]),
                        "Icon": company[4],
                        "high_24h": "$" + str(crypto["high_24h"]),
                        "low_24h": "$" + str(crypto["low_24h"]),
                        "price_change_24h": "$"
                        + str(round(float(crypto["price_change_24h"]), 5)),
                        "price_change_percentage_24h": crypto[
                            "price_change_percentage_24h"
                        ],
                    }
                )
    else:
        qCompanies = (
            "select * from COMPANIES WHERE MarketID = '{}' And Name != ''".format(
                idMarket
            )
        )
        cursor = conn.cursor()
        cursor.execute(qCompanies)
        companies = cursor.fetchall()
        for company in companies:
            result.append(
                {
                    "Id": company[0],
                    "Name": company[1],
                    "Ticker": company[2],
                    "Icon": company[4],
                    "Desc": company[5],
                }
            )
    conn.close()
    return result


# Функция создания портфеля пользователя
def CreatePortfolio(mwdb, positions, userId):
    newID = 0
    conn = db.connect(mwdb)
    try:
        dbcursor = conn.cursor()
        queryChenkingPortfolioName = (
            "SELECT Name FROM PORTFOLIO WHERE Name = '{}'".format(
                positions["portfolioName"]
            )
        )
        dbcursor.execute(queryChenkingPortfolioName)
        isDublicatePortfolioName = cases.read_sql_query(
            queryChenkingPortfolioName, conn
        )
        if isDublicatePortfolioName.shape[0] > 0:
            return "Duplicate name!"

        dbcursor.execute(
            "INSERT INTO PORTFOLIO (Name, UserId, MarketId) values (?,?,?)",
            [positions["portfolioName"], userId, positions["marketID"]]
        )
        conn.commit()
        queryGetPortfolioID = "SELECT ID FROM PORTFOLIO ORDER BY ID DESC Limit 1"
        portfolio = cases.read_sql_query(queryGetPortfolioID, conn)  # found created id
        if portfolio.shape[0] > 0:
            newID = int(portfolio["ID"][0])
        else:
            return "Error: New id not found"

        for pf in positions["data"]:
            dbcursor.execute(
                "INSERT INTO POSITIONS (PortfolioID, CompanyID, Quantity0, Price0, LotSize, Comission, RISK) values (?,?,?,?,?,?,?)",
                [
                    newID,
                    pf["CompanyID"],
                    pf["Quantity"],
                    pf["Price"],
                    pf["LotSize"],
                    pf["Comission"],
                    pf["Risk"],
                ],
            )
            conn.commit()

    except Exception as e:
        print(str(e))
        return str(e)

    conn.close()
    return "Success! You created portfolio: " + positions["portfolioName"]


# Функция выгрузки портфелей c позициями пользователя
def GetMyPortfoliosPositions(mwdb, userId):
    result = []
    conn = db.connect(mwdb)
    dbcursor = conn.cursor()
    try:
        queryGetPortfolios = (
            "SELECT ID, Name, UserId FROM PORTFOLIO WHERE UserId = '{}'".format(userId)
        )
        dbcursor.execute(queryGetPortfolios)
        portfolios = dbcursor.fetchall()
        for portfolio in portfolios:
            queryGetPositios = "SELECT p.ID, c.Name, p.Quantity0, p.Price0, p.LotSize, p.Comission, p.RISK, p.PortfolioID FROM POSITIONS p LEFT JOIN COMPANIES c ON p.CompanyID = c.ID WHERE p.PortfolioID = '{}'".format(
                portfolio[0]
            )
            dbcursor.execute(queryGetPositios)
            positions = dbcursor.fetchall()
            for position in positions:
                result.append(
                    {
                        "ID": position[0],
                        "PortfolioName": portfolio[1],
                        "Name": position[1],
                        "Quantity": position[2],
                        "Price": position[3],
                        "LotSize": position[4],
                        "Comission": position[5],
                        "Risk": position[6],
                        "PortfolioID": position[7],
                    }
                )
        conn.close()

    except Exception as e:
        print(str(e))
        result = str(e)
    return result

# Функция выгрузки портфелей пользователя
def GetMyPortfolios(mwdb, userId, marketID):
    result = []
    conn = db.connect(mwdb)
    dbcursor = conn.cursor()
    try:
        queryGetPortfolios = (
            "SELECT ID, Name, UserId FROM PORTFOLIO WHERE UserId = '{}' AND MarketID = '{}'".format(userId, marketID)
        )
        dbcursor.execute(queryGetPortfolios)
        portfolios = dbcursor.fetchall()
        for portfolio in portfolios:
            result.append(
                    {
                        "PortfolioID": portfolio[0],
                        "PortfolioName": portfolio[1]
                    }
                )
        conn.close()

    except Exception as e:
        print(str(e))
        result = str(e)
    return result

# Функция удаления позиции из портфеля
def RemovePosition(mwdb, idPosition):
    conn = db.connect(mwdb)
    try:
        queryRemovePosition = "Delete FROM POSITIONS WHERE ID = '{}'".format(idPosition)
        dbcursor = conn.cursor()
        dbcursor.execute(queryRemovePosition)
        conn.commit()
        conn.close()

    except Exception as e:
        return str(e)
    return "This record  deleted!"


# Функция обновления позиции
def UpdatePosition(mwdb, position):
    conn = db.connect(mwdb)
    dbcursor = conn.cursor()
    try:
        queryUpdPosition = "UPDATE POSITIONS SET Quantity0 = '{}', Price0 = '{}', LotSize = '{}', Comission = '{}', RISK  = '{}' WHERE ID = '{}'".format(
            position["Quantity"],
            position["Price"],
            position["LotSize"],
            position["Comission"],
            position["Risk"],
            position["ID"],
        )
        dbcursor = conn.cursor()
        dbcursor.execute(queryUpdPosition)
        conn.commit()
        conn.close()
    except Exception as e:
        return str(e)
    return "This record  updsted!"


# Функция удаления порфтеля
def RemovePortfolio(mwdb, portfolioID):
    conn = db.connect(mwdb)
    try:
        queryRemovePortfolio = "Delete FROM PORTFOLIO WHERE ID = '{}'".format(
            portfolioID
        )
        queryRemovePortfolioPositions = (
            "Delete FROM Positions WHERE PortfolioID = '{}'".format(portfolioID)
        )
        dbcursor = conn.cursor()
        # Удаляем портфолио пользователя
        dbcursor.execute(queryRemovePortfolio)
        conn.commit()
        # Удаляем связанные с портфолио позиции
        dbcursor.execute(queryRemovePortfolioPositions)
        conn.commit()
        conn.close()

    except Exception as e:
        return str(e)
    return "This record  deleted!"


def AddPositionToPortfolio(mwdb, positions):
    conn = db.connect(mwdb)
    portfolioID = positions["portfolioID"]
    try:
        dbcursor = conn.cursor()
        for p in positions["data"]:
            dbcursor.execute(
                "INSERT INTO POSITIONS (PortfolioID, CompanyID, Quantity0, Price0, LotSize, Comission, RISK) values (?,?,?,?,?,?,?)",
                [
                    portfolioID,
                    p["CompanyID"],
                    p["Quantity"],
                    p["Price"],
                    p["LotSize"],
                    p["Comission"],
                    p["Risk"],
                ],
            )
            conn.commit()

    except Exception as e:
        print(str(e))
        return str(e)

    conn.close()
    return "New position added!"

def CheckingPositionInPortfolio(mwdb, positionID, portfolioName):
    conn = db.connect(mwdb)
    portfolioID = 0
    resText = ''
    try:
        dbcursor = conn.cursor()
        queryGetPortfolioID= ("SELECT ID FROM PORTFOLIO WHERE Name = '{}'".format(portfolioName))
        dbcursor.execute(queryGetPortfolioID)
        portfolioID = cases.read_sql_query(
            queryGetPortfolioID, conn
        )
        if portfolioID.shape[0] > 0:
              portfolioID = int(portfolioID["ID"][0])
              queryGetPosition = "SELECT ID FROM POSITIONS where CompanyID = {} AND PortfolioID = {}".format(positionID, portfolioID)
              position = cases.read_sql_query(queryGetPosition, conn)  # found created id
              resText = 'update'
              if position.shape[0] > 0:
                return "You already have this position"
        else :
             resText = 'new'

    except Exception as e:
        print(str(e))
        return str(e)
    
    return resText
