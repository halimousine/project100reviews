#!/usr/bin/env python
# coding: utf-8

# In[103]:


import requests
from lxml import html
from bs4 import BeautifulSoup
import re
import json

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

import gspread
from oauth2client.service_account import ServiceAccountCredentials


# In[104]:


scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('project-100-reviews-6063049ddd77.json', scope)
client = gspread.authorize(creds)
def GetSpreadsheetData(sheetNameurl, worksheetIndex):
    sheet = client.open_by_url(sheetNameurl).get_worksheet(worksheetIndex)
    return sheet.get_all_values()[1:]


# In[105]:


spreadsheet = GetSpreadsheetData('https://docs.google.com/spreadsheets/d/13Tg3hMg5gvRycZ9eD93NnYcMCUm5BVgnB3SvvP2Hcco/edit?'+
                                 'usp=sharing', 0)


# In[106]:


spreadsheet_df = pd.DataFrame(spreadsheet, columns=['form_timestamp', 'full_name', 'email', 'group_name', 'business_name1',
                                                    'visit_date1', 'reviewurl', 'cocoapreneursubmit', 'pledge'])
yelp_df = spreadsheet_df[spreadsheet_df['reviewurl'].str.contains('https://www\.yelp\.com.*')]
yelp_df


# In[107]:


def get_scriptcontent(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, 'lxml')
    content = soup.find_all('script')
    return content


# In[108]:


def get_reviews(scriptcontent):
    script_text = '<script type="application/ld+json">        {"aggregateRating":'
    counter = -1
    for rev in scriptcontent:
        counter += 1
        if str(rev)[:62] == script_text:
            reviews = str(rev)[43:]
    return reviews


# In[109]:


def get_firstreview(reviews):
    business_name = re.findall(r'"name": (.*?),', reviews)[0].replace('"', '').replace('\\u2019', "'")
    review_dict = json.loads(re.findall(r'"review": \[(.*?), {"reviewRating":', reviews)[0])
    #searching review_dict
    review_date = review_dict['datePublished']
    review_desc = review_dict['description'].replace('\n',"")
    reviewer_name = review_dict['author']
    star_rating = list(review_dict['reviewRating'].values())[0]
    return [business_name, reviewer_name, star_rating, review_desc, review_date]


# In[110]:


def YelpReviewScraper(urls):
    business_name, reviewer_name, star_rating, review_desc, review_date = [], [], [], [], []
    for url in urls:
        content = get_scriptcontent(url)
        reviews = get_reviews(content)
        info = get_firstreview(reviews)
        business_name.append(info[0])
        reviewer_name.append(info[1])
        star_rating.append(info[2])
        review_desc.append(info[3])
        review_date.append(info[4])
    review_data = {'business_name2': business_name, 'reviewer_name': reviewer_name,'star_rating': star_rating,                    'review_desc': review_desc, 'review_date': review_date, 'review_platform': 'Yelp', 'reviewurl' : urls}
    return pd.DataFrame(review_data)


# In[112]:


reviews_df0 = YelpReviewScraper(yelp_df['reviewurl'])
reviews_df0.head()


# In[114]:


reviews_df = yelp_df.merge(reviews_df0, on="reviewurl")[['form_timestamp','full_name', 'reviewer_name','email',
                                                         'group_name','business_name1', 'business_name2','visit_date1',
                                                         'review_date','review_platform','reviewurl','review_desc',
                                                         'star_rating', 'cocoapreneursubmit','pledge']]
reviews_df


# In[115]:


reviews_df.to_csv('yelpreviews_df.csv', index=False)


# In[ ]:


#for public production, I should use the Google and Yelp API's but I created
#web crawlers at first before I learned about Terms of Service and limits
#on scraping, especially for use in public production.


# In[ ]:
