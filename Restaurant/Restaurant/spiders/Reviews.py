# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
from random import randint
from time import sleep
from ..items import NoItem, ReviewItem, MiscInfoItem
import socket
import numpy as np
import psycopg2 as pg2

class ReviewsSpider(scrapy.Spider):
    name = "Reviews"

    def check_connection(self):
        try:
            socket.create_connection(("www.google.com", 443))
            return(True)
        except:
            pass
        return(False)

    def start_requests(self):
        # Handle connection issues.
        if not self.check_connection():
            print('Connection Lost! Please check your internet connection!', flush=True)
            self.close(self, 'Connection Lost!')
            return []
        
        # Expected outcome with working internet
        start_url = 'https://www.yelp.com/biz/international-smoke-san-francisco-san-francisco-2?start=0&sort_by=date_desc'
        yield(scrapy.Request(url=start_url, meta = {'review_count': 0}, callback=self.parse))

    def parse(self, response):
        hostname = 'localhost'
        username = 'postgres'
        password = '*******'
        database = 'RestaurantReviews'
        
        conn = pg2.connect(host = hostname, database = database, user = username, password = password)
        cur = conn.cursor()
        
        if 'last_review_date' not in response.meta:
            # Define the last dated review in the database
            cur.execute("SELECT MAX(review_date) FROM Reviews;")
            last_review_date = cur.fetchone()[0]
            
            # Define the last_review_date as an early date before the restaurant's creation if not in database(first scrape)
            if last_review_date is None:
                last_review_date = datetime(2000,1,1).date()
        
        else:
            last_review_date = response.meta['last_review_date']

        
        names = response.xpath("//meta[@itemprop='author']/@content").getall()
        ratings = response.xpath("//meta[@itemprop='ratingValue']/@content").getall()[1:len(names)+1]
        review_dates = response.xpath("//meta[@itemprop='datePublished']/@content").getall()
        review_dates = np.array([datetime.strptime(date_str, '%Y-%m-%d').date() for date_str in review_dates])
        reviews = response.xpath("//p[@itemprop='description']/text()").getall()
        
        if any(review_dates <= last_review_date):
            print('\n\nFound review dates less than last_review_date!\n\n')
            review_dates_trunc = review_dates[review_dates >= review_dates[review_dates <= last_review_date].max()]
            print(review_dates_trunc)
            for i in range(len(review_dates_trunc)):
                cur.execute("SELECT * FROM Reviews WHERE review_date = %s AND reviewer_name = %s;", (review_dates_trunc[i], names[i]))
                check_response = cur.fetchone()
                if check_response is not None:
                    names = names[:i]
                    ratings = ratings[:i]
                    review_dates = review_dates[:i]
                    reviews = reviews[:i]
                    break
        
        data = ReviewItem()
        data['names'] = names
        data['reviewdates'] = review_dates
        data['ratings'] = ratings
        data['reviews'] = reviews
        review_count = response.meta['review_count'] + len(reviews)
        
        conn.close()
        yield(data)
        
        if len(reviews) == 20:
            sleep(randint(7,30))
            print(response.xpath("//link[@rel='next']/@href").get())
            if response.xpath("//link[@rel='next']/@href").get() is not None:
                yield(scrapy.Request(url = response.xpath("//link[@rel='next']/@href").get(),
                                     meta = {'last_review_date': last_review_date, 'review_count': review_count},
                                     callback = self.parse))
        else:
            print('\n\nDone scraping.\n\n')
            conn.close()
            misc = MiscInfoItem()
            misc['num_reviews'] = review_count
            yield(misc)
            
            
                    
            
        
        
        