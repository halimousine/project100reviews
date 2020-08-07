#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sklearn
import numpy as np
import datetime as dt
#from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import plotly.graph_objects as go


# In[2]:


greviews = pd.read_csv('googlereviews_df.csv')
yreviews = pd.read_csv('yelpreviews_df.csv')
mergedf = yreviews.merge(greviews, how='outer')
mergedf['form_timestamp'] = pd.to_datetime(mergedf['form_timestamp'])
mergedf['visit_date1'] = pd.to_datetime(mergedf['visit_date1']).dt.date
mergedf['review_date'] = pd.to_datetime(mergedf['review_date']).dt.date
mergedf.head()


# In[3]:


#visualizations : top 5 reviewers, top 5 businesses, google maps api location of businesses, visit_date time series,
#review_desc word cloud, overall star rating, current pledge count, total cocoapreneur providers.


# In[4]:


def top5reviewers(df, group):
    top5ppl = df.groupby("full_name").count().iloc[:,:1].reset_index().rename(columns={'form_timestamp':'count',    'full_name':'name'}).sort_values('count', ascending=False).head(5)
    ax = sns.barplot(top5ppl['name'], top5ppl['count'])
    ax.set(xlabel="Reviewer Name", ylabel="Count", title="Top 5 Reviewers of "+str(group))
    ax.plot()
    plt.show()


# In[5]:


def top5businesses(df, group):
    top5bus = df.groupby("business_name1").count().iloc[:,:1].reset_index().rename(columns={'form_timestamp':'count',    'business_name1':'name'}).sort_values('count', ascending=False).head(5)
    plt.figure(figsize=(10,6))
    ax = sns.barplot(top5bus['name'], top5bus['count'])
    ax.set(xlabel="Business Name", ylabel="Count", title="Top 5 Businesses Visited By "+str(group))
    plt.xticks(rotation=45)
    ax.plot()
    plt.show()


# In[ ]:


def dashboardtop5(merge_df):
    for group in list(mergedf['group_name'].unique()):
        print(group)
        groupdf = mergedf[mergedf['group_name']==group]
        top5reviewers(groupdf, group)
        top5businesses(groupdf, group)


# In[355]:


def timeseries(df, group):
    dates = df.groupby("visit_date1").count().iloc[:,:1].reset_index().rename(columns={'form_timestamp':'count',    'visit_date1':'visit_date'}).sort_values('count', ascending=False).head(5)
    ax = sns.lineplot(dates['visit_date'], dates['count'])
    ax.plot()
    ax.locator_params(axis='y', integer=True)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.set(xlabel="Date", ylabel="Count", title=str(group)+" Review Activity")
    plt.ylim(0)
    plt.xticks(rotation=60)
    plt.show()


# In[6]:


def dashboardtimeseries(merge_df):
    for group in list(mergedf['group_name'].unique()):
        print(group)
        groupdf = mergedf[mergedf['group_name']==group]
        timeseries(groupdf, group)


# In[356]:

'''
def review_wordcloud(df, group):
    words1 = ""
    for s in df[df['group_name']==group]['review_desc']:
        words1 += s
    plt.figure(figsize=(8,8))
    wordcloud = WordCloud(stopwords=STOPWORDS, max_font_size=30, max_words=100, background_color="white").generate(words1)
    plt.imshow(wordcloud, interpolation='bilinear')
'''

# In[7]:

'''
def dashboardwordcloud(merge_df):
    for group in list(mergedf['group_name'].unique()):
        print(group)
        groupdf = mergedf[mergedf['group_name']==group]
        review_wordcloud(groupdf, group)
'''

# In[357]:


def avgrating(df, group):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = np.mean(df['star_rating']),
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Star Rating"}
    ))
    fig.show()


# In[8]:


def dashboardstars(merge_df):
    for group in list(mergedf['group_name'].unique()):
        print(group)
        groupdf = mergedf[mergedf['group_name']==group]
        avgrating(groupdf, group)


# In[ ]:
dashboardtop5(mergedf)
dashboardtimeseries(mergedf)
