#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 19 21:17:26 2021

@author: shu
"""

from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool
import os
#import shutil
import time
import requests
#import re
#import json
import glob
import sys
import subprocess
#import sys
import urllib.request
'''
system argument 0: the last page to be scraped
'''
#sys.path.append("/usr/local/bin/wget")
BASE_URL = 'https://en.m.wikipedia.org/wiki/List_of_IBA_official_cocktails'
#BASE = 'https://imgflip.com'
session = requests.Session()
HEADERS = {
    'user-agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 '
                   '(KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36')
}
DATA_DIR = 'data'

save_path = os.path.join("/Users/sheng/ai-somm.github.io/cocktail", DATA_DIR)
os.chdir(save_path)

class Scraper():
    """Scraper for Winemag.com to collect wine reviews"""

    def __init__(self, pages_to_scrape=(1,1), num_jobs=1, clear_old_data=True):
        self.pages_to_scrape = pages_to_scrape
        self.num_jobs = num_jobs
        self.clear_old_data = clear_old_data
        self.session = requests.Session()
        self.start_time = time.time()
        self.data = []
        #self.cross_process_review_count = 0
        #self.estimated_total_reviews = (pages_to_scrape[1] + 1 - pages_to_scrape[0]) * 30

        if num_jobs > 1:
            self.multiprocessing = True
            self.worker_pool = Pool(num_jobs)
        else:
            self.multiprocessing = False

    def scrape_site(self):
        if self.clear_old_data:
            self.clear_data_dir()
        if self.multiprocessing:
            link_list = [BASE_URL.format(page) for page in range(self.pages_to_scrape[0],self.pages_to_scrape[1] + 1)]
            self.worker_pool.map(self.scrape_page, link_list)
            self.worker_pool.terminate()
            self.worker_pool.join()
        else:
            self.data.append(self.scrape_page(BASE_URL))
            #for page in range(self.pages_to_scrape[0], self.pages_to_scrape[1] + 1):
            #    self.data.append(self.scrape_page(page, BASE_URL.format(page)))
            print('Scrape finished...')
        #self.condense_data()
        
            
                
    def scrape_page(self, page_url, isolated_review_count=0, retry_count=0):
        list_of_cocktails = []
        list_of_recipes = []
        try:
            response = self.session.get(page_url, headers=HEADERS)
        except:
            retry_count += 1
            if retry_count <= 3:
                self.session = requests.Session()
                self.scrape_page(page_url, isolated_review_count, retry_count)
            else:
                raise

        soup = BeautifulSoup(response.content, 'html.parser')
        # Drop the first review-item; it's always empty
        blocks = soup.find_all("dl")

        for block in blocks:
            #self.cross_process_review_count += 1
            #isolated_review_count += 1
            cocktails = block.find_all("dt")
            recipes = block.find_all("dd")
            assert len(cocktails) == len(recipes)
            for cocktail, recipe in zip(cocktails, recipes):
                try:
                    ct = cocktail.string
                except:
                    ct = "NA"
                try:
                    rp = recipe.string
                except:
                    rp = "NA"
                list_of_cocktails.append(ct)
                list_of_recipes.append(rp)
            
            
                        


    def scrape_meme(self, meme_url):
        meme_response = self.session.get(meme_url, headers=HEADERS)
        meme_soup = BeautifulSoup(meme_response.content, 'html.parser')
        try:
            return self.parse_download(meme_soup)
        except Exception as e:
            print('\n-----\nError parsing: {}\n{}\n-----'.format(
                meme_url,
                e.message
            ))

    def parse_download(self, meme_soup):
        try:
            soups = meme_soup.find_all(attrs={'class':"base-img"})
        except Exception as e:
            print("did not find base-img!")
            pass
        
        for soup in soups:
            #print(soup)
            try:
                
                url = "https:" + soup['src']
                print(url)
                try:
                    #subprocess.run(["/usr/local/bin/wget", "-r", "-nc", "-P", save_path, url], shell=True)
                    subprocess.run(["/usr/local/bin/wget", "-r", "-nc", url])
  
                    #urllib.request.urlretrieve(url, os.path.join(save_path, url.split("/")[-1]))
                    print("downloaded from "+url)
                except Exception as e:
                    print("no images downloaded!")
            except Exception as e:
                print("did not find src for soup:\n")  
                #print(soup)
                try:
                    url = "https:" + soup['data-src']
                    subprocess.run(["/usr/local/bin/wget", "-r", "-nc", url])
  
                    #urllib.request.urlretrieve(url, os.path.join(save_path, url.split("/")[-1]))
                    print("downloaded from "+url)
                    
                except Exception as e:
                    print("did not fine data-src either for soup:\n")
                    print(soup)
                
                #else:
                #    meme_count += 1
                    
                
  
if __name__ == '__main__':
    # Total review results on their site are conflicting, hardcode as the max tested value for now
    pages_to_scrape = 2413, 2413
    meme_scraper = Scraper(pages_to_scrape=pages_to_scrape, num_jobs=1, clear_old_data=False)

    # Step 1: scrape data
    meme_scraper.scrape_site()


# 1350, 1415, 1416, 1525, 1608, 1663, 2198