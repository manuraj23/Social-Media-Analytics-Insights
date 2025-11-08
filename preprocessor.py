import pandas as pd

def preprocess(df):
    df = df.dropna()
    df["Academic_Level"] = df["Academic_Level"].str.lower()
    df["Gender"] = df["Gender"].str.lower()
    df["Relationship_Status"] = df["Relationship_Status"].str.lower()
    df["Most_Used_Platform"] = df["Most_Used_Platform"].str.lower()
    df["Affects_Academic_Performance"]= df["Affects_Academic_Performance"].str.lower()


    df["Academic_Level"] = df["Academic_Level"].map({
        "high school": 0,
        "undergraduate": 1,
        "graduate": 2
    })

    df["Gender"] = df["Gender"].map({
        "male": 0,
        "female": 1
    })

    df["Relationship_Status"] = df["Relationship_Status"].map({
        "complicated": 0,
        "single": 1,
        "in relationship": 2
    })

    df["Most_Used_Platform"] = df["Most_Used_Platform"].map({
        "instagram": 1,
        "twitter": 2,
        "tiktok": 3,
        "youtube": 4,
        "facebook": 5,
        "linkedin": 6,
        "snapchat": 7,
        "line": 8,
        "kakaotalk": 9,
        "vkontakte (vk)": 10,
        "whatsapp": 11,
        "wechat": 12
    })
    df["Affects_Academic_Performance"] = df["Affects_Academic_Performance"].map({
        "no": 0,
        "yes": 1
    })

    return df