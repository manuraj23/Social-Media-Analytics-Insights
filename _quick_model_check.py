import pandas as pd
import numpy as np
import preprocessor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

print('Starting quick model check...')

# Load and preprocess (same as app1.py preprocessing step)
df = pd.read_csv('Students Social Media Addiction.csv')
df = preprocessor.preprocess(df)

features = [
    'Age', 'Gender', 'Academic_Level', 'Avg_Daily_Usage_Hours',
    'Most_Used_Platform', 'Affects_Academic_Performance',
    'Sleep_Hours_Per_Night', 'Relationship_Status',
    'Conflicts_Over_Social_Media'
]

target_addiction = 'Addicted_Score'
target_mental = 'Mental_Health_Score'

# Drop rows where targets are missing
initial_rows = len(df)
df_model = df.dropna(subset=[target_addiction, target_mental])
print('Rows before drop (targets):', initial_rows, 'after drop:', len(df_model))

X = df_model[features]
print('Feature missing counts before imputation:\n', X.isnull().sum())

y_add = df_model[target_addiction]
y_mh = df_model[target_mental]

# split
X_train, X_test, y_train_add, y_test_add = train_test_split(X, y_add, test_size=0.2, random_state=42)
_, _, y_train_mh, y_test_mh = train_test_split(X, y_mh, test_size=0.2, random_state=42)

numeric_features = ['Age', 'Avg_Daily_Usage_Hours', 'Sleep_Hours_Per_Night']
categorical_features = [f for f in features if f not in numeric_features]

numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='mean')),
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

preprocessor_ct = ColumnTransformer(transformers=[
    ('num', numeric_transformer, numeric_features),
    ('cat', categorical_transformer, categorical_features)
])

# Quick check: ensure transformer removes NaNs after fit_transform on train
transformed = preprocessor_ct.fit_transform(X_train)
# Convert to dense array if sparse
try:
    arr = transformed.toarray()
except Exception:
    arr = np.asarray(transformed)

print('Transformed train shape:', arr.shape)
print('Any NaNs in transformed train?:', np.isnan(arr).any())

# Fit model
model = Pipeline(steps=[('preprocessor', preprocessor_ct), ('regressor', LinearRegression())])
model.fit(X_train, y_train_add)

# Predict
y_pred = model.predict(X_test)

mse = mean_squared_error(y_test_add, y_pred)
rmse = mse ** 0.5
r2 = r2_score(y_test_add, y_pred)
print(f"Addicted Score model → RMSE: {rmse:.4f}, R2: {r2:.4f}")

print('Quick model check completed successfully.')
