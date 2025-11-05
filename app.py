import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import plotly.graph_objects as go
import statsmodels.api as sm
import helper
import os,sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

df = pd.read_csv(resource_path('Students Social Media Addiction.csv'))

st.sidebar.title("Student Social Media Analytics")
# use width='stretch' instead of deprecated use_container_width
st.sidebar.image("image.png", caption="Student Social Media Analytics Image", width='stretch')
user_menu=st.sidebar.radio(
    'Select an Option',('Overview','Usage & Demographics','Behavioral & Lifestyle Impact','Psychological & Academic Outcomes')
)

# Overview Page
if user_menu=='Overview':
    st.title("Overview")
    st.markdown("""
    This application provides insights into the social media addiction patterns among students. 
    It includes various analyses and visualizations to help understand the impact of social media on students' lives.
    """)
    # use width='stretch' instead of deprecated use_container_width
    st.image("image.png", caption="Social Media Addiction Overview", width='stretch')

# Usage & Demographics
#Average Daily Social Media Usage by Age Group -- Bar Chart / Line Chart
#Most Popular Social Media Platforms -- Pie Chart / Bar Chart
#Platform Preference by Gender  -- Stacked Bar Chart
#Top Countries With Highest Average Usage -- Choropleth Map

elif user_menu=='Usage & Demographics':
    st.title("Usage & Demographics")
    st.subheader("Average Daily Social Media Usage by Age Group")
    # CSV uses 'Avg_Daily_Usage_Hours' for average daily usage
    age_usage = df.groupby('Age')['Avg_Daily_Usage_Hours'].mean().reset_index()
    fig1 = px.bar(age_usage, x='Age', y='Avg_Daily_Usage_Hours', title='Average Daily Social Media Usage by Age Group')
    st.plotly_chart(fig1)

    st.subheader("Most Popular Social Media Platforms")
    # CSV column for platform is 'Most_Used_Platform'
    platform_counts = df['Most_Used_Platform'].value_counts().reset_index()
    platform_counts.columns = ['Platform', 'Count']
    fig2 = px.pie(platform_counts, names='Platform', values='Count', title='Most Popular Social Media Platforms')
    st.plotly_chart(fig2)

    st.subheader("Platform Preference by Gender")
    gender_platform = df.groupby(['Gender', 'Most_Used_Platform']).size().unstack().fillna(0)
    fig3 = px.bar(gender_platform, barmode='stack', title='Platform Preference by Gender')
    st.plotly_chart(fig3)   

    st.subheader("Top Countries With Highest Average Usage")
    # Use 'Avg_Daily_Usage_Hours' for country-level averages as well
    country_usage = df.groupby('Country')['Avg_Daily_Usage_Hours'].mean().reset_index()
    fig4 = px.choropleth(country_usage, locations='Country', locationmode='country names', color='Avg_Daily_Usage_Hours',
                         title='Top Countries With Highest Average Usage')
    st.plotly_chart(fig4)   

# Behavioral & Lifestyle Impact
#Usage vs Sleep Duration Relationship -- Scatter Plot
#Conflicts Due to Social Media Across Relationship Status -- Box Plot
#Addiction Score Distribution -- Histogram
#Sleep Hours Comparison Based on ‘Affects Academic Performance’ -- Violin Plot

elif user_menu=='Behavioral & Lifestyle Impact':
    st.title("Behavioral & Lifestyle Impact")
    st.subheader("Usage vs Sleep Duration Relationship")
    # CSV uses 'Sleep_Hours_Per_Night' for sleep duration
    fig1 = px.scatter(df, x='Avg_Daily_Usage_Hours', y='Sleep_Hours_Per_Night', trendline='ols',
                      title='Usage vs Sleep Duration Relationship')
    st.plotly_chart(fig1)

    st.subheader("Conflicts Due to Social Media Across Relationship Status")
    # CSV uses 'Conflicts_Over_Social_Media'
    fig2 = px.box(df, x='Relationship_Status', y='Conflicts_Over_Social_Media',
                  title='Conflicts Due to Social Media Across Relationship Status')
    st.plotly_chart(fig2)

    st.subheader("Addiction Score Distribution")
    # CSV column name is 'Addicted_Score'
    fig3 = px.histogram(df, x='Addicted_Score', nbins=30,
                        title='Addiction Score Distribution')
    st.plotly_chart(fig3)

    st.subheader("Sleep Hours Comparison Based on ‘Affects Academic Performance’")
    fig4 = px.violin(df, x='Affects_Academic_Performance', y='Sleep_Hours_Per_Night', box=True,
                     title='Sleep Hours Comparison Based on Affects Academic Performance')
    st.plotly_chart(fig4)
# Psychological & Academic Outcomes
#Social Media Usage Impact on Academic Performance -- Grouped Bar Chart
#User Mental Health Score vs Addicted Score -- Heatmap
#Mental Health Score by Platform -- Bar Chart
elif user_menu=='Psychological & Academic Outcomes':
    st.title("Psychological & Academic Outcomes")
    st.subheader("Usage vs Sleep Duration Relationship")
    # CSV uses 'Sleep_Hours_Per_Night' for sleep duration
    fig1 = px.scatter(df, x='Avg_Daily_Usage_Hours', y='Sleep_Hours_Per_Night', trendline='ols',
                     title='Usage vs Sleep Duration Relationship')
    st.plotly_chart(fig1)

    st.subheader("Conflicts Due to Social Media Across Relationship Status")
    # CSV uses 'Conflicts_Over_Social_Media'
    fig2 = px.box(df, x='Relationship_Status', y='Conflicts_Over_Social_Media',
                 title='Conflicts Due to Social Media Across Relationship Status')
    st.plotly_chart(fig2)

    st.subheader("Addiction Score Distribution")
    # CSV column name is 'Addicted_Score'
    fig3 = px.histogram(df, x='Addicted_Score', nbins=30,
                     title='Addiction Score Distribution')
    st.plotly_chart(fig3)