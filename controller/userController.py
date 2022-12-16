import pandas as pd
import sqlite3


conn=sqlite3.connect('data.db',check_same_thread=False)
c=conn.cursor()

def create():
    c.execute('CREATE TABLE IF NOT EXISTS coldDrinks (Date TEXT, Name TEXT, Count INTEGER)')

def insert(date,name,count):
    c.execute('INSERT INTO coldDrinks (Date, Name, Count) VALUES (?, ?, ?)',(date, name, count))
    conn.commit()

def read():
    c.execute("SELECT * FROM pragma_table_info('coldDrinks')")
    ind=[entry[1] for entry in c.fetchall()]
    c.execute('SELECT * FROM coldDrinks')
    values=c.fetchall()
    data= pd.DataFrame(values,columns=ind)
    return data

def count_drinks():
    c.execute("SELECT Name, sum(Count) from coldDrinks GROUP BY name")
    values=c.fetchall()
    data=pd.DataFrame(values,columns=["Name","Count"])
    return data
