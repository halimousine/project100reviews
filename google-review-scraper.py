#!/usr/bin/env python
# coding: utf-8

# In[16]:


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


# In[17]:


scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('project-100-reviews-6063049ddd77.json', scope)
client = gspread.authorize(creds)
def GetSpreadsheetData(sheetNameurl, worksheetIndex):
    sheet = client.open_by_url(sheetNameurl).get_worksheet(worksheetIndex)
    return sheet.get_all_values()[1:]


# In[18]:


spreadsheet = GetSpreadsheetData('https://docs.google.com/spreadsheets/d/13Tg3hMg5gvRycZ9eD93NnYcMCUm5BVgnB3SvvP2Hcco/edit?'+
                                 'usp=sharing', 0)


# In[19]:


spreadsheet_df = pd.DataFrame(spreadsheet, columns=['form_timestamp', 'full_name', 'email', 'group_name', 'business_name1',
                                                    'visit_date1', 'reviewurl', 'cocoapreneursubmit', 'pledge'])
google_df = spreadsheet_df[spreadsheet_df['reviewurl'].str.contains('https://goo\.gl/maps/.*')]


# In[20]:


def get_metacontent(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, 'lxml')
    metas = soup.find_all('meta')
    content_array = [i.get('content') for i in metas]
    return content_array


# In[21]:


#star rating and review description
def get_review(content_arr):
    star_rating0, review_desc0 = [], []
    for c in content_arr:
        match = re.match(r'[★]+', c)
        if match != None:
            star_rating0.append(len(match[0]))
            review_desc0.append(re.findall(r'[^\'★☆].*', c))
    star_rating0 = np.mean(star_rating0)
    review_desc0 = review_desc0[0][0][1:].replace('"', "")
    return star_rating0, review_desc0


# In[22]:


#reviewer name and business name
def get_review_names(content_arr):
    reviewer_name0, business_name0 = [], []
    for c in content_arr:
        match = re.findall(r'Google review of (.*?) by (.*)', c)
        if match != []:
            reviewer_name0.append(match[0][0])
            business_name0.append(match[0][1])
    return reviewer_name0[0], business_name0[0]


# In[23]:


def GoogleReviewScraper(urls):
    star_rating, review_desc, reviewer_name, business_name = [], [], [], []
    for url in urls:
        content = get_metacontent(url)
        review, names = get_review(content), get_review_names(content)
        star_rating.append(review[0])
        review_desc.append(review[1])
        business_name.append(names[0])
        reviewer_name.append(names[1])
    review_data = {'business_name2': business_name, 'reviewer_name': reviewer_name,'star_rating': star_rating,                    'review_desc': review_desc, 'review_platform': 'Google', 'reviewurl':urls}
    return pd.DataFrame(review_data)


# In[24]:


reviews_df0 = GoogleReviewScraper(google_df['reviewurl'])
reviews_df0.head()


# In[25]:


reviews_df = google_df.merge(reviews_df0, on="reviewurl")[['form_timestamp','full_name', 'reviewer_name','email','group_name',
                                                           'business_name1', 'business_name2','visit_date1',
                                                           'review_platform','reviewurl','review_desc', 'star_rating',
                                                           'cocoapreneursubmit','pledge']]
reviews_df


# In[26]:


reviews_df.to_csv('googlereviews_df.csv', index=False)


# In[ ]:
