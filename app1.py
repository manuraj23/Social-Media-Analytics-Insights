import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import plotly.graph_objects as go
import statsmodels.api as sm
import preprocessor
import helper
import os,sys
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.impute import SimpleImputer
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

df =pd.read_csv(resource_path('Students Social Media Addiction.csv'))
df=preprocessor.preprocess(df)
# df.to_csv("Processed_Students_Social_Media_Addiction.csv", index=False)

# print("✅ File saved as: Processed_Students_Social_Media_Addiction.csv")
# print(df) 
# display df

st.sidebar.title("DashBoard")
user_menu=st.sidebar.radio(
    'Select an Option',('Overview','Predict Your Score','Usage & Demographics','Behavioral & Lifestyle Impact','Psychological & Academic Outcomes')
)
if user_menu=='Overview':
    st.title("Social Media Addiction Overview")
    st.image("image.png", caption="Social Media Addiction Overview", width='stretch')

    st.write("""
    This application provides insights into the social media addiction patterns among students. 
    """)
    st.write("""
    It includes various analyses and visualizations to help understand the impact of social media on students' lives.
    """)
    st.write("""
    You can also predict your social media addiction score based on your usage patterns using the 'Predict Your Score' section.
    """)

elif user_menu=='Predict Your Score':
    st.title("📊 Predict Your Social Media Addiction Score")
    st.write(
        "This dashboard trains **Linear Regression** models to predict **Addicted_Score** and **Mental_Health_Score** from demographic and behavior features."
    )
    st.write("""
    You can input your details below to predict your social media addiction score based on the trained model.
    """)
    st.write(
        "This dashboard trains **Linear Regression** models to predict:"
        "\n- **Addicted_Score** (How addictive the usage is)"
        "\n- **Mental_Health_Score** (Wellbeing measure)"
    )

    
    
