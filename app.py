import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
from urlextract import URLExtract
import pandas as pd


from urllib.parse import urlparse
import numpy as np

st.sidebar.title("Whatsapp chat analyzer")

st.title("WhatsApp Chat Analysis")

st.components.v1.iframe("https://lively-gingersnap-32b3a2.netlify.app/", width=800, height=500, scrolling=True)



uploaded_file = st.sidebar.file_uploader("Choose a file")

st.write(" [How to export WhatsApp chat](https://faq.whatsapp.com/android/chats/how-to-save-your-chat-history/?lang=en)")

st.write(f'''To download sample whatsapp chat text file, please click above. 
Insert the downloaded file into 'Browse Files' option.
You can perform analysis on your WhatsApp chats as well, just 
make sure that the system time format is set to 24-Hrs.
''')


mon_num = st.sidebar.text_input('Enter month name for topic modelling ','January')
if mon_num=="":
    mon_num='January'


if uploaded_file is not None:

    bytes_data = uploaded_file.getvalue()
    data=bytes_data.decode("utf-8")
    df=preprocessor.preprocess(data)

    st.title("Dataframe")
    st.dataframe(df)


    #fetch unique users
    user_list=df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0,"Overall")
    selected_user = st.sidebar.selectbox("Show analysis",user_list)

    if st.sidebar.button("Show Analysis"):
        num_messages, words, num_media_messages, num_links=helper.fetch_stats(selected_user, df)
        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)

        with col3:
            st.header("Total Media")
            st.title(num_media_messages)

        with col4:
            st.header("Total Links")
            st.title(num_links)

        #Links
        st.header("Links")
        extractor = URLExtract()
        links = []
        for message in df['message']:
            links.extend(extractor.find_urls(message))
        st.dataframe(links,width=1350)
        st.header("Link's Domain and Domain Count")
        col1, col2 = st.columns(2)
        with col1:
            domains=[]
            for link in links:
                domains.append(urlparse(link).netloc)
            st.dataframe(domains)

        with col2:
            domn_cnt=pd.value_counts(np.array(domains))
            st.dataframe(domn_cnt)


        #timeline monthly
        st.title("Monthly Timeline")
        timeline=helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'],color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)


        #timeline daily
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'],color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)


        #finding the most active user(Group only)
        if selected_user == 'Overall':
            st.title("Most Active User")
            x, new_df= helper.most_active_users(df)
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)
            with col1:
                ax.bar(x.index, x.values)
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

        #WordCloud
        st.title("Word-cloud")
        df_wc = helper.create_wordcloud(selected_user,df)
        fig,ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        #most common words
        most_common_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots()
        ax.barh(most_common_df[0], most_common_df[1])
        plt.xticks(rotation='vertical')
        st.title("Most Common Words")
        st.pyplot(fig)


        #emoji analysis
        emoji_df  = helper.emoji_helper(selected_user, df)
        st.title("Emoji Analysis")
        st.dataframe(emoji_df)


        # activity map
        st.title('Activity Map')
        col1, col2 = st.columns(2)


        with col1:
            st.header("Most busy day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='purple')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.header("Most busy month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)


        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)


        st.title("Monthly Activity Map")
        data_by_date = df.groupby(['month', 'day']).count()
        data_heat = data_by_date.pivot_table(values='hour', index='month', columns='day')
        fig, ax = plt.subplots()
        ax = sns.heatmap(data_heat, cmap='rainbow').set(title='Message Density of Each Day')
        st.pyplot(fig)


        topic_final = helper.topic_per_month(selected_user, df, mon_num)
        st.title("Possible topics discussed in group: ")
        st.header(topic_final)
