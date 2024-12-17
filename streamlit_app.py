import streamlit as st
import pandas as pd


st.set_page_config(page_title='Logs Report',
page_icon=r"C:\Users\dmc86\Desktop\Logs\pics\1631346597752.png",
layout="wide"
)

st.title('Daily logs report')

def get_data_from_excel():
    try:
        # Load the Excel file
        df = pd.read_excel(
            io='master_file.xlsx',
            engine='openpyxl',
            sheet_name='Sheet1',
            usecols='A:D',
            nrows=9999
        )
        # Rename the first column for clarity (if needed)
        df.rename(columns={df.columns[0]: "Timestamp"}, inplace=True)

        # Ensure the Timestamp column is in datetime format
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
        if df["Timestamp"].isna().any():
            st.warning("Some timestamps could not be parsed. Please check the data.")

        # Create the TimeCreated column with hours and minutes
        df["Time"] = df["Timestamp"].dt.strftime("%H:%M")
        # Create the Day column in DD-MM-YYYY format
        df["Day"] = df["Timestamp"].dt.strftime("%d-%m-%Y")
        # Remove "BARKERROSS\" from User column
        if "User" in df.columns:
            df["User"] = df["User"].str.replace(r'^BARKERROSS\\', '', regex=True)
        return df
    except Exception as e:
        st.error(f"Error loading data from Excel: {e}")
        return pd.DataFrame()  # Return an empty DataFrame if there's an error

# Load the data
df = get_data_from_excel()