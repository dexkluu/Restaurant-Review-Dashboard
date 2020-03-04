# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 21:10:48 2020

@author: dluu1
"""

import psycopg2 as pg2
from psycopg2.extras import execute_values
import pandas as pd
from nltk.tokenize import word_tokenize
from collections import Counter


def ReviewWords(month, year):
    hostname = 'localhost'
    username = 'postgres'
    password = 'danny6'
    database = 'RestaurantReviews'
    
    conn = pg2.connect(host = hostname, database = database, user = username, password = password)
    cur = conn.cursor()
    
    sql = """SELECT * FROM Reviews WHERE (EXTRACT (MONTH FROM review_date) = %s) 
    AND (EXTRACT (YEAR FROM review_date) = %s);""" %(month, year)
    df = pd.read_sql_query(sql, conn)
    
    df['Above 3'] = df['rating'] > 3
    
    df['unique_words'] = df['review'].apply(lambda x: [*{*word_tokenize(x.lower())}])
    df = df[['Above 3', 'unique_words']].groupby('Above 3').sum()
    
    countedgood = Counter(df['unique_words'][True])
    countedbad = Counter(df['unique_words'][False])
    
    cur.execute('SELECT word FROM ExcludedWords;')
    excludedwords = cur.fetchall()
    
    for i in excludedwords:
        if i[0] in countedgood:
            del countedgood[i[0]]
        
        if i[0] in countedbad:
            del countedbad[i[0]]
            
            
    return({'badcounts': countedbad.most_common(5), 'goodcounts': countedgood.most_common(5), 'month': month, 'year': year})
    

def FinalizeKeywords(dictionary):
    hostname = 'localhost'
    username = 'postgres'
    password = 'danny6'
    database = 'RestaurantReviews'
    
    conn = pg2.connect(host = hostname, database = database, user = username, password = password)
    cur = conn.cursor()
    
    monthlist = [dictionary['month']]*len(dictionary['badcounts'])
    yearlist = [dictionary['year']]*len(dictionary['badcounts'])
    
    negwords = []
    poswords = []
    negwordscount = []
    poswordscount = []
    for i in range(len(dictionary['badcounts'])):
        negwords.append(dictionary['badcounts'][i][0])
        poswords.append(dictionary['goodcounts'][i][0])
        negwordscount.append(dictionary['badcounts'][i][1])
        poswordscount.append(dictionary['goodcounts'][i][1])
        
    goodwords = list(zip(monthlist, yearlist, poswords, poswordscount))
    badwords = list(zip(monthlist, yearlist, negwords, negwordscount))
    
    execute_values(cur, """INSERT INTO PositiveWords(month, year, word, unique_count) VALUES %s;""", goodwords)
    conn.commit()
    execute_values(cur, """INSERT INTO NegativeWords(month, year, word, unique_count) VALUES %s;""", badwords)
    print('Inserted values.')
    conn.commit()
    return(None)
