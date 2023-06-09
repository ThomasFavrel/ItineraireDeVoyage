import pandas
from param import database
from param import path_POI_csv, path_theme_csv, path_theme_unique_csv
from param import struct_table_POI, struct_table_theme_unique, struct_table_theme
from postgres import BDDR
#from etl import main

import pandas as pd
import os
from fastapi import FastAPI



api = FastAPI(
    title = 'BD Postgres',
    description =  'Base de données PostgreSQL',
    version = "1.0.1")

@api.get("/init")
def init():
    BDDR1 = BDDR()

    #BDDR1.query("DROP DATABASE itinerairedevoyage;")
    #BDDR1.info()

    BDDR1.query("CREATE DATABASE {db};".format(db = database))
    BDDR1.ConnectDB(database)

    BDDR1.query(struct_table_POI)
    BDDR1.query(struct_table_theme_unique)
    BDDR1.query(struct_table_theme)

    BDDR1.info()

    #main()

    BDDR1.insert_df("poi", path_POI_csv, True)
    BDDR1.insert_df("themeunique", path_theme_unique_csv, True)
    BDDR1.insert_df("theme", path_theme_csv, True)

    print(BDDR1.query("SELECT * FROM poi LIMIT 10;"))


@api.get("/connect")
def connect():
    global BDD
    BDD = BDDR()


@api.get("/connectDB/db")
def connect_db(database: str = database):
    BDD.ConnectDB(database)


@api.get("/query")
def query(sql_query: str):
    BDD.query(sql_query)


@api.post("/add")
def add(table: str, row: set):
    sql_query = "INSERT INTO " + table + " VALUES " + str(row) + ";"
    print(sql_query)
    #BDD.query(sql_query)


@api.post("/update")
def update(table: str, setd: dict, where: str = None):

    setd = ["{col} = {val}".format(col = col, val = setd[col]) for col in setd]
    sql_query = "UPDATE " + table + " SET " + str(setd)[1:-1].replace("'","")
    if where:
        sql_query += " WHERE " + where
    sql_query += ";"

    print(sql_query)
    #BDD.query(sql_query)


@api.post("/delete")
def delete(table: str, where: str):
    sql_query = "DELETE FROM " + table + " WHERE " + where + ";"
    print(sql_query)
    BDD.query(sql_query)


@api.get("/read")
def read(table: str, select: str = None, where: str = None, limit: int = None):

    sql_query = "SELECT "
    if select:
        sql_query += str(select)[1:-1]
    else:
        sql_query += "*"

    sql_query += " FROM " + table

    if where:
        sql_query += " WHERE " + where

    if limit:
        sql_query += " LIMIT " + str(limit)
    
    sql_query += ";"
    print(sql_query)
    return BDD.query(sql_query)

"""
read(["po", "pi"], "ville == paris", 10)
add("yui", ("pi", "pou", "po"))
update("eri", {"dffe" :"paz", "ajcnb" : "jbsd"})
"""
