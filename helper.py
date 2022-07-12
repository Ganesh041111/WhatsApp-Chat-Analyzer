from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji
import yake
from gensim.parsing.preprocessing import remove_stopwords
import streamlit as st

extractor = URLExtract()


def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    #fetch the number of messages
    num_messages = df.shape[0]

    #fetch the number of words
    words=[]
    for message in df['message']:
        words.extend(message.split())

    #fetch the number of media messages
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    #fetch number of links shared
    links = []
    for message in df['message']:
        links.extend(extractor.find_urls(message))


    return num_messages, len(words), num_media_messages, len(links)


def most_active_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts()/df.shape[0])*100,2).reset_index().rename(columns={'index':'name','user':'percent'})
    return x,df

def create_wordcloud(selected_user,df):
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']



    def remove_stop_words(message):
        y=[]
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    temp['message'] = temp['message'].apply(remove_stop_words)
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc

def most_common_words(selected_user, df):
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']
    words = []
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)
    most_common_df= pd.DataFrame(Counter(words).most_common(20))
    return most_common_df

def emoji_helper(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.UNICODE_EMOJI['en']])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    return  emoji_df

def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    time = []
    for i in range(timeline.shape[0]):
        time.append((timeline['month'][i] + '-' + str(timeline['year'][i])))
    timeline['time'] = time
    return timeline

def daily_timeline(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    daily_timeline = df.groupby('only_date').count()['message'].reset_index()
    return daily_timeline

def week_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap


def topic_per_month(selected_user,df,mon_num):
    promotions = []
    iii=0
    monthslist=[]
    for month in df['month']:
        monthslist.append(month)
    
    for message in df['message']:
        if len(message) > 45 and monthslist[iii] == mon_num:
            promotions.append(message)
        iii+=1
    promotion_df = pd.DataFrame({'Promotion_message': promotions})
    
    kw_extractor = yake.KeywordExtractor()
    language = "en"
    max_ngram_size = 3
    deduplication_threshold = 0.9
    numOfKeywords = 10
    custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_threshold,
                                                top=numOfKeywords, features=None)
    li = []

    
    for message in promotion_df['Promotion_message']:
        message = message.lower()
        message = remove_stopwords(message)
        keywords = custom_kw_extractor.extract_keywords(message)
        for kw in keywords:
            li.append(kw[0])
    

    ans = []
    setli = list(set(li))
    for i in range(0, len(setli)):
        n = li.count(setli[i])
        temp = []
        temp.append(n)
        temp.append(setli[i])
        ans.append(temp)
    ans.sort(reverse=True)

    topic = ""
    i = 0
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    mon_topic=""
    try:
        count=0
        while (mon_topic.count(" ") < 8):
            mon_topic+=ans[count][1]+" - " 
            count+=1
    except:
        mon_topic='''Invalid month selection\n
        These might be the possible reasons:\n
        1. Chats for the selected month, are not available or very less for prediction.\n
        2. Invalid format. Valid Format: eg. January, May, June.'''
        return mon_topic

    return mon_topic

