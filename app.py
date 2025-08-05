import streamlit as st
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
import matplotlib.pyplot as plt
import seaborn as sns

# Load data and models
data = pd.read_csv("nba_success_dataset_2010-2019.csv")
predictors = ["stops", "bpm", "Rec Rank", "GP", "ftr", "Efficient usage", "points per minute", "impact per usage", "two way impact", "versatility score"]
target = "Highest_WS"

# Calculate new predictors if not present
if "Efficient usage" not in data.columns:
    data['Efficient usage'] = data['usg'] * data['TS_per'] / 100
if "points per minute" not in data.columns:
    data['points per minute'] = data['pts'] / (data['Min_per'] + 0.1)
if "impact per usage" not in data.columns:
    data['impact per usage'] = data['bpm'] / (data['usg'] + 0.1)
if "two way impact" not in data.columns:
    data['two way impact'] = data['obpm'] + data['dbpm']
if "versatility score" not in data.columns:
    data['versatility score'] = data['AST_per'] + data['ORB_per'] + data['blk_per']

data = data.replace([np.inf, -np.inf], np.nan).fillna(0)

# Train models (or load pre-trained models if available)
scaler = StandardScaler()
X = data[predictors]
y = data[target]
X_scaled = scaler.fit_transform(X)

linreg = LinearRegression()
linreg.fit(X_scaled, y)

dtree = DecisionTreeRegressor(max_depth=3, random_state=42)
dtree.fit(X, y)

# Predefined NBA players
player_options = data["PLAYER"].unique().tolist()

st.title("NBA Success Prediction Dashboard")

# Model selection
model_choice = st.radio("Select Model", ["Linear Regression", "Decision Tree"])

# Player selection or manual entry
input_mode = st.radio("Choose Input Mode", ["Select NBA Player", "Enter Stats Manually"])

if input_mode == "Select NBA Player":
    player_name = st.selectbox("Choose a player", player_options)
    player_row = data[data["PLAYER"] == player_name][predictors].iloc[0]
    input_stats = player_row
else:
    input_stats = []
    st.write("Enter player stats:")
    for col in predictors:
        val = st.number_input(col, value=float(data[col].mean()))
        input_stats.append(val)
    input_stats = pd.Series(input_stats, index=predictors)

# Prepare input for prediction
if model_choice == "Linear Regression":
    input_scaled = scaler.transform([input_stats])
    prediction = linreg.predict(input_scaled)[0]
else:
    prediction = dtree.predict([input_stats])[0]

st.subheader("Predicted Win Shares")
st.metric(label="Win Shares", value=f"{prediction:.2f}")

# Show feature distribution and input location
st.subheader("Feature Distributions")
for col in predictors:
    fig, ax = plt.subplots()
    sns.histplot(data[col], bins=30, kde=True, ax=ax, color="skyblue")
    ax.axvline(input_stats[col], color="red", linestyle="--", label="Input Value")
    ax.set_title(f"{col} Distribution")
    ax.legend()
    st.pyplot(fig)

# Show model performance metrics
st.subheader("Model Performance")
if model_choice == "Linear Regression":
    y_pred = linreg.predict(X_scaled)
else:
    y_pred = dtree.predict(X)
rmse = np.sqrt(np.mean((y_pred - y) ** 2))
r2 = 1 - np.sum((y_pred - y) ** 2) / np.sum((y - y.mean()) ** 2)
st.write(f"RMSE: {rmse:.2f}")
st.write(f"R2 Score: {r2:.2f}")

st.write("Select a player or enter stats to see predicted NBA success. Red lines in the plots show your input compared to the dataset.")
