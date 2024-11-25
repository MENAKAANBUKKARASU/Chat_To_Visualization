import streamlit as st
import pandas as pd
import google.generativeai as genai
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configure Google Generative AI API key securely
api_key = "AIzaSyDnfsg0VZivglg7vROEHZcyB5D176dpo7c" # Set your API key in an environment variable
if api_key:
    genai.configure(api_key=api_key)
else:
    st.warning("Google Generative AI API key is not set. Falling back to manual suggestions.")

# Load Excel data
def load_excel_data(file):
    try:
        return pd.read_excel(file)
    except Exception as e:
        st.error(f"Error loading the Excel file: {e}")
        return None

# Suggest visualizations using Gemini API
def suggest_visualizations(data):
    if not api_key:
        return suggest_visualizations_manually(data)

    column_info = {
        "columns": data.columns.tolist(),
        "dtypes": data.dtypes.apply(str).tolist()
    }
    try:
        response = genai.chat(
            model="gemini-1.0",
            messages=[
                {"role": "system", "content": "You are an AI that provides visualization suggestions based on dataset structure."},
                {"role": "user", "content": f"The dataset has columns: {column_info['columns']} with data types: {column_info['dtypes']}. Suggest 3-5 visualization ideas."}
            ]
        )
        return response["candidates"][0]["content"]
    except Exception as e:
        st.error(f"Error generating visualization suggestions: {e}")
        return suggest_visualizations_manually(data)

# Manual fallback for visualization suggestions
def suggest_visualizations_manually(data):
    numeric_columns = data.select_dtypes(include=["number"]).columns.tolist()
    categorical_columns = data.select_dtypes(include=["object"]).columns.tolist()
    datetime_columns = data.select_dtypes(include=["datetime"]).columns.tolist()

    suggestions = []

    if len(numeric_columns) >= 2:
        suggestions.append(f"Scatter plot of {numeric_columns[0]} vs {numeric_columns[1]}.")
        suggestions.append(f"Line chart of {numeric_columns[0]} over time.")
        suggestions.append(f"Area chart of {numeric_columns[0]} over time.")
        suggestions.append(f"Histogram of {numeric_columns[0]}.")

    if categorical_columns:
        suggestions.append(f"Bar chart of counts for {categorical_columns[0]}.")
        suggestions.append(f"Pie chart of counts for {categorical_columns[0]}.")

    if datetime_columns:
        suggestions.append(f"Time series plot for {datetime_columns[0]}.")

    if not suggestions:
        suggestions.append("No suitable visualization suggestions for this dataset.")

    return "\n".join(suggestions)

# Visualization generation
def create_visualization(data, prompt):
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.set(style="whitegrid")

        if "scatter plot" in prompt.lower():
            x_col, y_col = data.select_dtypes(include=["number"]).columns[:2]
            sns.scatterplot(data=data, x=x_col, y=y_col, ax=ax)
            ax.set_title(f"Scatter Plot: {x_col} vs {y_col}")

        elif "line chart" in prompt.lower():
            x_col, y_col = data.select_dtypes(include=["number"]).columns[:2]
            sns.lineplot(data=data, x=x_col, y=y_col, ax=ax)
            ax.set_title(f"Line Chart: {y_col} over {x_col}")

        elif "area chart" in prompt.lower():
            x_col, y_col = data.select_dtypes(include=["number"]).columns[:2]
            data_sorted = data.sort_values(by=x_col)
            ax.fill_between(data_sorted[x_col], data_sorted[y_col], color="skyblue", alpha=0.5)
            ax.plot(data_sorted[x_col], data_sorted[y_col], color="Slateblue", alpha=0.6, linewidth=2)
            ax.set_title(f"Area Chart: {y_col} over {x_col}")

        elif "bar chart" in prompt.lower():
            col = data.select_dtypes(include=["object"]).columns[0]
            sns.countplot(data=data, x=col, ax=ax)
            ax.set_title(f"Bar Chart: Counts of {col}")

        elif "pie chart" in prompt.lower():
            col = data.select_dtypes(include=["object"]).columns[0]
            pie_data = data[col].value_counts()
            ax.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=90)
            ax.set_title(f"Pie Chart: Distribution of {col}")

        elif "histogram" in prompt.lower():
            col = data.select_dtypes(include=["number"]).columns[0]
            sns.histplot(data=data, x=col, kde=True, ax=ax)
            ax.set_title(f"Histogram: Distribution of {col}")

        elif "time series" in prompt.lower():
            datetime_col = data.select_dtypes(include=["datetime"]).columns[0]
            numeric_col = data.select_dtypes(include=["number"]).columns[0]
            sns.lineplot(data=data, x=datetime_col, y=numeric_col, ax=ax)
            ax.set_title(f"Time Series: {numeric_col} over {datetime_col}")

        else:
            st.error("Unable to match the visualization prompt.")
            return

        st.pyplot(fig)

    except Exception as e:
        st.error(f"Error creating visualization: {e}")

# Streamlit App
st.title("📊 AI-Powered Visualization Tool")
st.write("Upload an Excel file to generate visualizations dynamically using AI or manual suggestions!")

# File uploader
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    data = load_excel_data(uploaded_file)
    if data is not None:
        st.write("### Data Preview")
        st.dataframe(data)

        suggestions = suggest_visualizations(data)
        st.write("### Visualization Suggestions")
        st.write(suggestions)

        selected_prompt = st.selectbox("Choose a visualization prompt:", suggestions.split("\n"))
        user_prompt = st.text_input("Or, enter a custom prompt:")

        if selected_prompt:
            st.write("### Generated Visualization")
            create_visualization(data, selected_prompt)
        elif user_prompt:
            st.write("### Generated Visualization")
            create_visualization(data, user_prompt)
        else:
            st.warning("Please select or enter a visualization prompt.")
else:
    st.info("Upload a file to start.")
