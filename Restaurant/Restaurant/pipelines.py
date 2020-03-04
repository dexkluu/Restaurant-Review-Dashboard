# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import psycopg2 as pg2
from psycopg2.extras import execute_values
#import sys
#sys.path.append(".") # Adds higher directory to python modules path.
from .items import NoItem, ReviewItem, MiscInfoItem

class RestaurantPipeline(object):
    def open_spider(self, spider):
        hostname = 'localhost'
        username = 'postgres'
        password = '******'
        database = 'RestaurantReviews'
        
        self.conn = pg2.connect(host = hostname, database = database, user = username, password = password)
        self.cur = self.conn.cursor()
        
    def close_spider(self, spider):
        print('\n\nClosing spider\n\n')
        self.cur.close()
        self.conn.close()

    def process_item(self, item, spider):
        if isinstance(item, ReviewItem):
            # Do Usernames stuff
            print('\n\nHandling ReviewItem\n\n')
            return(self.handleReviews(item, spider))
        elif isinstance(item, MiscInfoItem):
            # Handling MiscInfoItem
            print('\n\nHandling MiscInfoItem\n\n')
            return(self.handleMiscInfo(item,spider))
        elif isinstance(item, NoItem):
            # Handling NoItem
            print('\n\nHandling NoItem\n\n')
            return(item)

    def handleReviews(self, item, spider):
        # defaultlist = ['DEFAULT']*len(item['names'])
        rows = list(zip(item['names'], item['ratings'], item['reviews'], item['reviewdates']))
        execute_values(self.cur, """INSERT INTO Reviews(reviewer_name, rating, review, review_date) VALUES %s""",rows)
        self.conn.commit()
        
    def handleMiscInfo(self, item, spider):
        self.cur.execute("INSERT INTO MiscInfo(reviews_obtained) VALUES(%s);", (item['num_reviews'],))
        self.conn.commit()
