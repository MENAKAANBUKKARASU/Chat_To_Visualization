import streamlit as st
import pandas as pd
import google.generativeai as genai
import matplotlib.pyplot as plt
import seaborn as sns

# Streamlit must start with set_page_config
st.set_page_config(page_title="AI-Powered Visualization Tool", page_icon="📊", layout="wide")

# Configure Google Generative AI API key securely
api_key = "AIzaSyDnfsg0VZivglg7vROEHZcyB5D176dpo7c"  # Replace with your API key
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

# Suggest visualizations
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
       # st.error(f"Error generating visualization suggestions: {e}")
        return suggest_visualizations_manually(data)

# Manual fallback
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

# Visualization generation with code display
def create_visualization(data, prompt):
    code_snippet = ""
    try:
        fig, ax = plt.subplots(figsize=(7,5))
        sns.set(style="whitegrid")
        if "scatter plot" in prompt.lower():
            x_col, y_col = data.select_dtypes(include=["number"]).columns[:2]
            sns.scatterplot(data=data, x=x_col, y=y_col, ax=ax)
            ax.set_title(f"Scatter Plot: {x_col} vs {y_col}")
            code_snippet = f"""
import seaborn as sns
sns.scatterplot(data=data, x='{x_col}', y='{y_col}')
"""
        elif "line chart" in prompt.lower():
            x_col, y_col = data.select_dtypes(include=["number"]).columns[:2]
            sns.lineplot(data=data, x=x_col, y=y_col, ax=ax)
            ax.set_title(f"Line Chart: {y_col} over {x_col}")
            code_snippet = f"""
import seaborn as sns
sns.lineplot(data=data, x='{x_col}', y='{y_col}')
"""
        elif "area chart" in prompt.lower():
            x_col, y_col = data.select_dtypes(include=["number"]).columns[:2]
            data_sorted = data.sort_values(by=x_col)
            ax.fill_between(data_sorted[x_col], data_sorted[y_col], color="skyblue", alpha=0.5)
            ax.plot(data_sorted[x_col], data_sorted[y_col], color="Slateblue", alpha=0.6, linewidth=2)
            ax.set_title(f"Area Chart: {y_col} over {x_col}")
            code_snippet = f"""
data_sorted = data.sort_values(by='{x_col}')
plt.fill_between(data_sorted['{x_col}'], data_sorted['{y_col}'], color="skyblue", alpha=0.5)
plt.plot(data_sorted['{x_col}'], data_sorted['{y_col}'], color="Slateblue", alpha=0.6, linewidth=2)
"""
        elif "bar chart" in prompt.lower():
            col = data.select_dtypes(include=["object"]).columns[0]
            sns.countplot(data=data, x=col, ax=ax)
            ax.set_title(f"Bar Chart: Counts of {col}")
            code_snippet = f"""
import seaborn as sns
sns.countplot(data=data, x='{col}')
"""
        elif "pie chart" in prompt.lower():
            col = data.select_dtypes(include=["object"]).columns[0]
            pie_data = data[col].value_counts()
            ax.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=90)
            ax.set_title(f"Pie Chart: Distribution of {col}")
            code_snippet = f"""
pie_data = data['{col}'].value_counts()
plt.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=90)
"""
        elif "histogram" in prompt.lower():
            col = data.select_dtypes(include=["number"]).columns[0]
            sns.histplot(data=data, x=col, kde=True, ax=ax)
            ax.set_title(f"Histogram: Distribution of {col}")
            code_snippet = f"""
import seaborn as sns
sns.histplot(data=data, x='{col}', kde=True)
"""
        elif "time series" in prompt.lower():
            datetime_col = data.select_dtypes(include=["datetime"]).columns[0]
            numeric_col = data.select_dtypes(include=["number"]).columns[0]
            sns.lineplot(data=data, x=datetime_col, y=numeric_col, ax=ax)
            ax.set_title(f"Time Series: {numeric_col} over {datetime_col}")
            code_snippet = f"""
import seaborn as sns
sns.lineplot(data=data, x='{datetime_col}', y='{numeric_col}')
"""
        else:
            st.error("Unable to match the visualization prompt.")
            return None, None
        st.pyplot(fig)
        return code_snippet
    except Exception as e:
        st.error(f"Error creating visualization: {e}")
        return None
# Sidebar: Code display
st.sidebar.title("📂 Code Display")
st.sidebar.write("### Generated Code")
generated_code_placeholder = st.sidebar.empty()

# Main App
st.title("📊 AI-Powered Visualization Tool")
st.markdown("""
Upload an Excel file, explore your data, and generate insightful visualizations dynamically!
""")

# File uploader
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
if uploaded_file:
    data = load_excel_data(uploaded_file)
    if data is not None:
        with st.expander("Click to view data preview"):
            st.dataframe(data)
        suggestions = suggest_visualizations(data)
        st.write("### Visualization Suggestions")
        st.write(suggestions)
        selected_prompt = st.selectbox("Choose a visualization prompt:", suggestions.split("\n"))
        user_prompt = st.text_input("Or, enter a custom prompt:")
        if selected_prompt:
            st.write("### Generated Visualization")
            generated_code = create_visualization(data, selected_prompt)
            if generated_code:
                generated_code_placeholder.code(generated_code, language="python")
        elif user_prompt:
            st.write("### Generated Visualization")
            generated_code = create_visualization(data, user_prompt)
            if generated_code:
                generated_code_placeholder.code(generated_code, language="python")
        else:
            st.warning("Please select or enter a visualization prompt.")
else:
    st.info("Upload a file to start.")
