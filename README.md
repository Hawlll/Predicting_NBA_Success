# 🏀 AI4ALL Project: Predicting NBA Success with Pre-Draft Data

**Curated by:** Alec Borque & Franklin Collazo  
**Affiliation:** AI4ALL 2025

## 📌 Research Question

**Which pre-draft college performance metrics best predict long-term NBA success, and how accurately can we forecast a player's future performance using machine learning?**

---

## 🎯 Problem Statement & Motivation

Despite significant resources spent on scouting and drafting, NBA teams continue to struggle with identifying future star players. According to reports like:

- _"More than 50% of First Round Picks are Busts"_ — The Riot Report  
- _"NBA Teams Are Drafting Worse - Why?"_ — Michael MacKelvie

…draft efficiency has declined, leading to costly mistakes and missed opportunities. With millions of dollars and team reputations at stake, there's an urgent need for data-driven tools to inform decision-making.

This project aims to develop a machine learning model to forecast a college player's NBA success and highlight inefficiencies in historical drafts by comparing model predictions to actual outcomes.

---

## 🧪 Methodology

### 📊 Data Sources

- **Predictors (Pre-Draft College Stats):**  
  - [College Basketball Statistics (Kaggle)](https://www.kaggle.com/datasets/adityak2003/college-basketball-players-20092021?select=CollegeBasketballPlayers2009-2021.csv) (2009–2021)

- **Targets (NBA Performance Metrics):**  
  - [NBA Player Statistics (Kaggle)](https://www.kaggle.com/code/robertsunderhaft/predicting-the-nba-mvp/input) (1982–2022)  
  - [NBA All-Star Appearances (Kaggle)](https://www.kaggle.com/datasets/rodneycarroll78/nba-stats-1980-2024?select=All-Star+Selections.csv) (1980–2024)

---

### 🔍 Features

**Independent Variables (Inputs):**

- Free Throw Percentage  
- Assist-to-Turnover Ratio  
- Age at Draft  
- Height & Wingspan  
- Additional Pre-Draft College Stats

**Dependent Variables (Outputs / Targets):**

- Win Shares (WS)  
- Box Plus-Minus (BPM)  
- Player Impact Estimate (PIE)  
- All-Star Appearances  
- Composite NBA Success Score (custom)

---

### 🤖 Machine Learning Models

- **Linear Regression**  
  - Interpretable baseline  
  - Suitable for linear trends  

- **Random Forest Regressor**  
  - Handles non-linearity well  
  - Useful for determining feature importance  

We may also explore other models (e.g., Ridge, Lasso, XGBoost) depending on performance.

---

## ⚠️ Bias & Limitations

We are aware of the following potential biases in our study:

- **Survivor Bias:**  
  Data includes mostly drafted players, ignoring undrafted success stories.
  
- **Measurement Bias:**  
  College stats may not perfectly map to pro performance due to different competition levels and roles.
  
- **Omitted Variables Bias:**  
  Longevity, injury history, and character traits are hard to quantify but can significantly affect careers.

---

## 📚 Citations & Inspirations

- SuperAnnotate. "Bias in machine learning: Types and examples"
- Michael MacKelvie. *NBA Teams Are Drafting Worse - Why?* (YouTube Analysis)
- *Moneyball* (Film inspiring sports analytics)
- The Riot Report. *More Than 50% Of First Round Picks Are Busts*
- Danielle Elliot, CLDigital. *The Cost Of Bad Drafting*
- CLDigital. *Applying Risk and Resilience to the 2023 NBA Draft*

---

## 📈 Goals

- Build a predictive model for NBA success based on college stats  
- Analyze misalignment between model predictions and actual NBA performance 
- Identify undervalued players and potential draft inefficiencies  

> *This project combines the love for basketball with the power of machine learning—bringing data science to the draft war room.*

---

## 🚀 Stay Tuned

We’ll be updating this repo with:

- Data preprocessing notebooks  
- Feature engineering scripts  
- Model training and evaluation results  
- Visualizations and insights  

---

🧠 _Questions, suggestions, or want to collaborate? Feel free to reach out or open an issue!_
