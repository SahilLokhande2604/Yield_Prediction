# -*- coding: utf-8 -*-
"""Crop_Yield_UI_Updated_3_final.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1zWCy3oyK8DoAcXUKbMX3URLU6S0Xu4fl
"""

import os

# Install required libraries
os.system("pip install gradio pandas numpy")

"""# Random Forest Regressor Model"""

import gradio as gr
import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestRegressor

# Load dataset
file_path = './crop_yield.csv'
data = pd.read_csv(file_path)

# Extract unique values for dropdowns
crops = sorted(data['Crop'].dropna().unique().tolist())
seasons = sorted(data['Season'].dropna().unique().tolist())
states = sorted(data['State'].dropna().unique().tolist())

# Prepare the dataset for model training
X = data[['Crop', 'Crop_Year', 'Season', 'State', 'Area', 'Annual_Rainfall', 'Fertilizer', 'Pesticide']]
y = data['Yield']

# Define numeric and categorical features
numeric_features = ['Crop_Year', 'Area', 'Annual_Rainfall', 'Fertilizer', 'Pesticide']
categorical_features = ['Crop', 'Season', 'State']

# Preprocessor for numeric and categorical data
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])

# Random Forest Regressor pipeline
model_rf = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
])

# Train-test split
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Fit the model
model_rf.fit(X_train, y_train)

"""# User Interface for Crop Yield Prediction

# Below is responsive UI
"""

import gradio as gr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
import joblib
import requests

# Load dataset
file_path = './crop_yield.csv'
data = pd.read_csv(file_path)

# Extract unique values for dropdowns
crops = sorted(data['Crop'].dropna().unique().tolist())
seasons = sorted(data['Season'].dropna().unique().tolist())
states = sorted(data['State'].dropna().unique().tolist())

# Load the crop-related info for recommendations
df = pd.read_csv('./crop_info.csv')  # Adjust the path accordingly

# Map states to cities for weather data
state_to_city = {
    "Andhra Pradesh": "Amaravati",
    "Arunachal Pradesh": "Itanagar",
    "Assam": "Guwahati",
    "Bihar": "Patna",
    "Chhattisgarh": "Raipur",
    "Goa": "Panaji",
    "Gujarat": "Gandhinagar",
    "Haryana": "Chandigarh",
    "Himachal Pradesh": "Shimla",
    "Jharkhand": "Ranchi",
    "Karnataka": "Bengaluru",
    "Kerala": "Thiruvananthapuram",
    "Madhya Pradesh": "Bhopal",
    "Maharashtra": "Mumbai",
    "Manipur": "Imphal",
    "Meghalaya": "Shillong",
    "Mizoram": "Aizawl",
    "Nagaland": "Kohima",
    "Odisha": "Bhubaneswar",
    "Punjab": "Chandigarh",
    "Rajasthan": "Jaipur",
    "Sikkim": "Gangtok",
    "Tamil Nadu": "Chennai",
    "Telangana": "Hyderabad",
    "Tripura": "Agartala",
    "Uttar Pradesh": "Lucknow",
    "Uttarakhand": "Dehradun",
    "West Bengal": "Kolkata",
    "Delhi": "New Delhi"
}

# Weather API Setup
def get_weather_data(state):
    api_key = "a1de691dcdfe4ad7dafe1a29a8ad2227"  # Replace with your API key
    city = state_to_city.get(state, "Mumbai")  # Default to Mumbai if no mapping exists
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(url)
    data = response.json()
    if data.get("cod") == 200:
        temp = data["main"]["temp"] - 273.15  # Convert from Kelvin to Celsius
        weather_description = data["weather"][0]["description"]
        return f"Temperature: {temp:.2f}°C, Weather: {weather_description}"
    else:
        return "Weather data not available."

# Crop-related information retrieval function
def get_crop_details(crop):
    # Filter the DataFrame to get the row where the crop matches
    crop_details = df[df['Crop'] == crop]

    # If crop details are found, extract the information
    if not crop_details.empty:
        growth_conditions = crop_details['Growth_Conditions'].values[0]
        diseases = crop_details['Diseases'].values[0]
        fertilizer = crop_details['Fertilizer'].values[0]
        pesticides = crop_details['Pesticides'].values[0]
        return f"Growth Conditions: {growth_conditions} \n Diseases: {diseases} \n Recommended Fertilizer: {fertilizer} \n Recommended Pesticides: {pesticides}"

        # return f"""
        #   **Crop Growth Conditions:**
        #   {growth_conditions}

        #   **Common Diseases and Pests:**
        #   {', '.join(diseases) if crop_details['diseases'] else 'No data available'}

        #    **Recommended Fertilizers:**
        #   {fertilizer}

        #    **Recommended Pesticides:**
        #   {pesticides}
        #   """
    else:
        return "No detailed information available for this crop."

# Define feature names for predictions
features = ['Crop', 'Crop_Year', 'Season', 'State', 'Area', 'Annual_Rainfall', 'Fertilizer', 'Pesticide']

# Visualization functions

def plot_historical_trends(crop, state):
    """Plot historical yield trends with additional statistical insights (mean, median, mode)."""
    # Filter data for the given crop and state
    filtered_data = data[(data['Crop'] == crop) & (data['State'] == state)]

    # Check if any data exists for the selected crop and state
    if filtered_data.empty:
        return "No data available for the selected crop and state combination."

    # Calculate mean, median, and mode of the yields
    mean_yield = filtered_data['Yield'].mean()
    median_yield = filtered_data['Yield'].median()
    mode_yield = filtered_data['Yield'].mode()[0]  # Mode may have multiple values, take the first one

    # Create a line plot for historical yield trends
    fig = px.line(filtered_data, x='Crop_Year', y='Yield', title=f'Historical Yield Trends for {crop} in {state}')

    # Add statistical lines for mean, median, and mode
    fig.add_hline(y=mean_yield, line=dict(color='green', dash='dash'), annotation_text=f"Mean: {mean_yield:.2f}", annotation_position="top right")
    fig.add_hline(y=median_yield, line=dict(color='blue', dash='dash'), annotation_text=f"Median: {median_yield:.2f}", annotation_position="top right")
    fig.add_hline(y=mode_yield, line=dict(color='red', dash='dash'), annotation_text=f"Mode: {mode_yield:.2f}", annotation_position="top right")

    # Update layout for UI optimization
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Yield (Tons)",
        height=400,  # Adjust the height for better fit on UI
        margin={"r": 40, "t": 40, "l": 40, "b": 40},  # Ensure tight margins
        template="plotly_white"  # Optional: Clean background for better visibility
    )

    return fig


def plot_feature_importance_for_crop_state(crop, state):
    """Plot top 5-6 most important features based on a model trained for the specific crop and state, excluding Crop_Year and Area."""
    # Filter the dataset for the selected crop and state
    filtered_data = data[(data['Crop'] == crop) & (data['State'] == state)]

    # Check if filtered data has enough data for training
    if filtered_data.empty:
        return "No data available for the selected crop and state combination."

    # Define features (excluding Crop_Year and Area) and target
    features = ['Season', 'Annual_Rainfall', 'Fertilizer', 'Pesticide']
    target = 'Yield'

    # Prepare the features and target
    X = filtered_data[features]
    y = filtered_data[target]

    # Encode categorical features using OneHotEncoder
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(), ['Season']),  # Example: only encoding 'Season' for now
            ('num', StandardScaler(), ['Annual_Rainfall', 'Fertilizer', 'Pesticide'])  # Numeric features
        ]
    )

    # Define the pipeline with a RandomForestRegressor
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
    ])

    # Train the model on the filtered data
    pipeline.fit(X, y)

    # Extract feature importance
    importances = pipeline.named_steps['regressor'].feature_importances_
    feature_names = pipeline.named_steps['preprocessor'].get_feature_names_out()

    # Create a DataFrame with feature names and their importance
    importance_df = pd.DataFrame({'Feature': feature_names, 'Importance': importances}).sort_values(by='Importance', ascending=False)

    # Select the top 5-6 most important features
    top_features = importance_df.head(6)

    # Create a bar chart for the top features
    fig = px.bar(top_features, x='Feature', y='Importance', title=f'Top 5-6 Feature Importance for {crop} in {state}', text='Importance')
    fig.update_layout(height=400)  # Adjust the height for better fit on UI
    return fig





def compare_yield(area, rainfall, fertilizer, pesticide, predicted_yield):
    """Generate pie chart to compare contributions of key factors."""
    factors = {'Area': area, 'Rainfall': rainfall, 'Fertilizer': fertilizer, 'Pesticide': pesticide}
    factors['Predicted Yield'] = predicted_yield
    fig = px.pie(names=factors.keys(), values=factors.values(), title='Contribution to Yield')
    fig.update_layout(height=400)  # Adjust the height for better fit on UI
    return fig



import pandas as pd
import plotly.express as px

def get_optimal_season(crop, state):
    """
    Identify the best season for a crop in a state based on weighted average yield and dominance.
    """
    # Filter the dataset for the selected crop and state
    filtered_data = data[(data['Crop'] == crop) & (data['State'] == state)]

    # Check if filtered data has enough records
    if filtered_data.empty:
        return "No data available for the selected crop and state combination.", None

    # Calculate total yield and area for each season
    season_stats = (
        filtered_data.groupby('Season')
        .agg(Total_Yield=('Yield', 'sum'), Total_Area=('Area', 'sum'))
        .reset_index()
    )

    # Calculate total area for the crop in the state
    total_area = season_stats['Total_Area'].sum()

    # Add area proportion and weighted yield
    season_stats['Area_Proportion'] = season_stats['Total_Area'] / total_area
    season_stats['Weighted_Yield'] = (
        season_stats['Total_Yield'] * season_stats['Area_Proportion']
    )

    # Sort by weighted yield to identify the best season
    season_stats = season_stats.sort_values(by='Weighted_Yield', ascending=False)

    # Apply dominance rule
    dominant_season = season_stats[season_stats['Area_Proportion'] > 0.6]
    if not dominant_season.empty:
        best_season_row = dominant_season.iloc[0]
    else:
        best_season_row = season_stats.iloc[0]

    best_season = best_season_row['Season']
    best_weighted_yield = best_season_row['Weighted_Yield']

    # Create a bar chart for weighted yields per season
    fig = px.bar(
        season_stats,
        x='Season',
        y='Weighted_Yield',
        title=f"Weighted Yield Per Season for {crop} in {state}",
        labels={'Weighted_Yield': 'Weighted Yield (Tons)'},
        text='Weighted_Yield'
    )
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig.update_layout(height=400)  # Adjust the height for better fit on UI

    return (
        f"The best season for {crop} in {state} is **{best_season} season** with a weighted yield of **{best_weighted_yield:.2f} tons**.",
        fig
    )



def optimal_season_handler(crop, state):
    """Handle the optimal season button click."""
    result, fig = get_optimal_season(crop, state)
    return result, fig

    optimal_season_btn.click(
    optimal_season_handler,
    inputs=[crop, state],
    outputs=[optimal_season_text, optimal_season_plot]
    )







def predict_and_visualize(crop, season, state, crop_year, area, annual_rainfall, fertilizer, pesticide):
    # Prepare input data for prediction
    input_data = pd.DataFrame([{
        'Crop': crop,
        'Crop_Year': crop_year,
        'Season': season,
        'State': state,
        'Area': area,
        'Annual_Rainfall': annual_rainfall,
        'Fertilizer': fertilizer,
        'Pesticide': pesticide
    }])

    # Predict yield (assuming the model_rf is trained already or is loaded)
    predicted_yield = model_rf.predict(input_data)[0]

    # Fetch additional recommendations (weather and crop details)
    weather_info = get_weather_data(state)
    crop_info = get_crop_details(crop)

    # # Generate visualizations
    trends_fig = plot_historical_trends(crop, state)
    importance_fig = plot_feature_importance_for_crop_state(crop, state)
    comparison_fig = compare_yield(area, annual_rainfall, fertilizer, pesticide, predicted_yield)

    return f"""
    **Prediction Results:**
    - Crop: {crop}
    - Season: {season}
    - State: {state}
    - Crop Year: {crop_year}
    - Area: {area} hectares
    - Annual Rainfall: {annual_rainfall} mm
    - Fertilizer Used: {fertilizer} kg
    - Pesticide Used: {pesticide} kg
    - **Predicted Yield**: {predicted_yield:.2f} tons""", weather_info, crop_info, trends_fig, importance_fig, comparison_fig


def validate_and_predict(crop, season, state, crop_year, area, annual_rainfall, fertilizer, pesticide):
    # Check if any field is empty or invalid
    if not all([crop, season, state, crop_year, area, annual_rainfall, fertilizer, pesticide]):
        return "All fields are required. Please fill in all fields.", None, None, None, None, None

    # Ensure numeric fields are positive numbers
    try:
        crop_year = int(crop_year)
        area = float(area)
        annual_rainfall = float(annual_rainfall)
        fertilizer = float(fertilizer)
        pesticide = float(pesticide)
        if crop_year <= 0 or area <= 0 or annual_rainfall <= 0 or fertilizer <= 0 or pesticide <= 0:
            raise ValueError
    except ValueError:
        return "Numeric fields must be positive numbers.", None, None, None, None, None

    # If all validations pass, call the main prediction function
    return predict_and_visualize(crop, season, state, crop_year, area, annual_rainfall, fertilizer, pesticide)

# Gradio Interface for Crop Yield Prediction and Crop Recommendation
with gr.Blocks(theme=gr.themes.Soft(primary_hue="green"),
               css=".block-container { max-width: 80%; margin: auto; }") as demo:
    gr.Markdown("# 🌾 Crop Yield Prediction Tool")
    gr.Markdown("Predict crop yield and visualize important trends and insights. 🌱")

    # Input Section for Yield Prediction
    gr.Markdown("### Enter the Details:")
    with gr.Row():
        with gr.Column():
            crop = gr.Dropdown(label="Select Crop", choices=crops, interactive=True)
            season = gr.Dropdown(label="Select Season", choices=seasons, interactive=True)
            state = gr.Dropdown(label="Select State", choices=states, interactive=True)
        with gr.Column():
            crop_year = gr.Number(label="Crop Year (e.g., 2020)", value=2020)
            area = gr.Number(label="Area (hectares)", value=5.0)
            annual_rainfall = gr.Number(label="Annual Rainfall (mm)", value=600.0)
        with gr.Column():
            fertilizer = gr.Number(label="Fertilizer Used (kg)", value=50.0)
            pesticide = gr.Number(label="Pesticide Used (kg)", value=10.0)

    # Button for Yield Prediction
    with gr.Row():
        submit_btn = gr.Button("Predict Yield")

    # Output Section for Yield Prediction
    with gr.Row():
        output_text = gr.Markdown()
    with gr.Row():
        weather_info = gr.Markdown(label="Weather Information")
    with gr.Row():
        crop_info = gr.Markdown(label="Crop Information")

    # Visualization Section for Yield Prediction
    gr.Markdown("### Visualization Results:")
    with gr.Row():
        trends_plot = gr.Plot(label="Historical Trends")
    with gr.Row():
        importance_plot = gr.Plot(label="Feature Importance")
    with gr.Row():
        comparison_plot = gr.Plot(label="Factor Contributions")

    # Button Action for Prediction
    submit_btn.click(
        validate_and_predict,
        inputs=[crop, season, state, crop_year, area, annual_rainfall, fertilizer, pesticide],
        outputs=[output_text, weather_info, crop_info, trends_plot, importance_plot, comparison_plot]
    )

    # Optimal Season Section
    gr.Markdown("### Find the Optimal Season:")
    with gr.Row():
        optimal_season_btn = gr.Button("Find Optimal Season")
    with gr.Row():
        optimal_season_text = gr.Markdown(label="Optimal Season Information")
    with gr.Row():
        optimal_season_plot = gr.Plot()

    # Button Action for Optimal Season Prediction
    optimal_season_btn.click(
        optimal_season_handler,
        inputs=[crop, state],
        outputs=[optimal_season_text, optimal_season_plot]
    )

# Launch the Gradio app
demo.launch(server_name="0.0.0.0", server_port=8080)
