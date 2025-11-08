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
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

df =pd.read_csv(resource_path('Students Social Media Addiction.csv'))

st.sidebar.title("DashBoard")
# use width='stretch' instead of deprecated use_container_width
# st.sidebar.image("image.png", caption="Student Social Media Analytics Image", width='stretch')
user_menu=st.sidebar.radio(
    'Select an Option',('Overview','Predict Your Score','Usage & Demographics','Behavioral & Lifestyle Impact','Psychological & Academic Outcomes')
)

# Sidebar option to preview/download the raw dataframe
show_data = st.sidebar.checkbox("Show raw dataset", value=False)
if show_data:
    st.subheader("Dataset preview")
    st.dataframe(df)
    csv = df.to_csv(index=False)
    st.download_button("Download dataset (CSV)", data=csv, file_name="Students_Social_Media_Addiction.csv", mime="text/csv")

# Overview Page
if user_menu=='Overview':
    st.title("Social Media Addiction Overview")
    st.image("image.png", caption="Social Media Addiction Overview", width='stretch')

    
    st.markdown("""
    This application provides insights into the social media addiction patterns among students. 
    It includes various analyses and visualizations to help understand the impact of social media on students' lives.
    """)

elif user_menu=='Predict Your Score':

    st.title("📊 Social Media Analytics — Linear Regression Dashboard")
    st.write(
        "This dashboard trains **Linear Regression** models to predict **Addicted_Score** and **Mental_Health_Score** from demographic and behavior features."
    )

    # ----------------------------
    # Dataset Already Loaded in df
    # ----------------------------

    FEATURES = [
        "Age",
        "Gender",
        "Academic_Level",
        "Most_Used_Platform",
        "Sleep_Hours_Per_Night",
        "Relationship_Status",
        "Conflicts_Over_Social_Media",
    ]

    TARGETS = ["Addicted_Score", "Mental_Health_Score"]

    num_features = ["Age", "Sleep_Hours_Per_Night", "Conflicts_Over_Social_Media"]
    cat_features = ["Gender", "Academic_Level", "Most_Used_Platform", "Relationship_Status"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", "passthrough", num_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_features),
        ]
    )

    random_state = 42
    X = df[FEATURES]

    X_train, X_test, y_train_A, y_test_A = train_test_split(
        X, df["Addicted_Score"], test_size=0.25, random_state=random_state
    )
    X_train2, X_test2, y_train_M, y_test_M = train_test_split(
        X, df["Mental_Health_Score"], test_size=0.25, random_state=random_state
    )

    pipe_A = Pipeline(steps=[("prep", preprocessor), ("lr", LinearRegression())])
    pipe_M = Pipeline(steps=[("prep", preprocessor), ("lr", LinearRegression())])

    pipe_A.fit(X_train, y_train_A)
    pipe_M.fit(X_train2, y_train_M)

    pred_A = pipe_A.predict(X_test)
    pred_M = pipe_M.predict(X_test2)

    def compute_metrics(y_true, y_pred):
        r2 = r2_score(y_true, y_pred)
        mae = mean_absolute_error(y_true, y_pred)
        # Some sklearn versions don't accept the `squared` kwarg; compute RMSE explicitly
        mse = mean_squared_error(y_true, y_pred)
        rmse = mse ** 0.5
        return r2, mae, rmse

    r2_A, mae_A, rmse_A = compute_metrics(y_test_A, pred_A)
    r2_M, mae_M, rmse_M = compute_metrics(y_test_M, pred_M)

    kf = KFold(n_splits=5, shuffle=True, random_state=random_state)
    cv_A = cross_val_score(pipe_A, X, df["Addicted_Score"], cv=kf, scoring="r2")
    cv_M = cross_val_score(pipe_M, X, df["Mental_Health_Score"], cv=kf, scoring="r2")

    st.subheader("📈 Model Performance")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Test R² (Addiction)", f"{r2_A:.3f}")
        st.metric("MAE", f"{mae_A:.3f}")
        st.metric("RMSE", f"{rmse_A:.3f}")
        st.caption(f"CV R² Mean: {cv_A.mean():.3f}")

    with col2:
        st.metric("Test R² (Mental Health)", f"{r2_M:.3f}")
        st.metric("MAE", f"{mae_M:.3f}")
        st.metric("RMSE", f"{rmse_M:.3f}")
        st.caption(f"CV R² Mean: {cv_M.mean():.3f}")

    st.divider()
    st.subheader("🧮 Predict Your Own Scores")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        age = st.number_input("Age", min_value=13, max_value=80, value=int(df["Age"].median()))
        gender = st.selectbox("Gender", sorted(df["Gender"].unique()))
    with c2:
        acad = st.selectbox("Academic Level", sorted(df["Academic_Level"].unique()))
        platform = st.selectbox("Most Used Platform", sorted(df["Most_Used_Platform"].unique()))
    with c3:
        sleep = st.number_input("Sleep Hours per Night", min_value=0.0, max_value=12.0, step=0.1, value=float(df["Sleep_Hours_Per_Night"].median()))
        rel = st.selectbox("Relationship Status", sorted(df["Relationship_Status"].unique()))
    with c4:
        conflicts = st.number_input("Conflicts Over Social Media (0-5)", min_value=0, max_value=10, value=int(df["Conflicts_Over_Social_Media"].median()))

    user_row = pd.DataFrame({
        "Age": [age],
        "Gender": [gender],
        "Academic_Level": [acad],
        "Most_Used_Platform": [platform],
        "Sleep_Hours_Per_Night": [sleep],
        "Relationship_Status": [rel],
        "Conflicts_Over_Social_Media": [conflicts],
    })

    pred_user_A = pipe_A.predict(user_row)[0]
    pred_user_M = pipe_M.predict(user_row)[0]

    st.metric("Predicted Addicted Score", f"{pred_user_A:.2f}")
    st.metric("Predicted Mental Health Score", f"{pred_user_M:.2f}")



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
    st.subheader("Social Media Usage Impact on Academic Performance")
    usage_academic = df.groupby(['Avg_Daily_Usage_Hours', 'Affects_Academic_Performance']).size().reset_index(name='Count')
    fig1 = px.bar(usage_academic, x='Avg_Daily_Usage_Hours', y='Count', color='Affects_Academic_Performance',
                  title='Social Media Usage Impact on Academic Performance', barmode='group')
    st.plotly_chart(fig1)

    st.subheader("User Mental Health Score vs Addicted Score")
    heatmap_data = df.pivot_table(index='Mental_Health_Score', columns='Addicted_Score', aggfunc='size', fill_value=0)
    fig2 = px.imshow(heatmap_data, labels=dict(x="Addicted Score", y="Mental Health Score", color="Count"),
                     title='User Mental Health Score vs Addicted Score')
    st.plotly_chart(fig2)

    st.subheader("Mental Health Score by Platform")
    mental_health_platform = df.groupby('Most_Used_Platform')['Mental_Health_Score'].mean().reset_index()
    fig3 = px.bar(mental_health_platform, x='Most_Used_Platform', y='Mental_Health_Score',
                  title='Mental Health Score by Platform')
    st.plotly_chart(fig3)