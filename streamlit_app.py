import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import glob

st.set_page_config(page_title='Logs Report',
page_icon=r"C:\Users\dmc86\Desktop\Logs\pics\1631346597752.png",
layout="wide"
)

st.title('Daily logs report')

# Function to load and process the Excel file
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


st.sidebar.header("Please Filter Here:")

# Add date filters: From and Until
start_day = st.sidebar.date_input(
    "From:",
    value=pd.to_datetime(df["Timestamp"].min()).date(),  # Default to the earliest date
    min_value=pd.to_datetime(df["Timestamp"].min()).date(),
    max_value=pd.to_datetime(df["Timestamp"].max()).date()
)

end_day = st.sidebar.date_input(
    "Until:",
    value=pd.to_datetime(df["Timestamp"].max()).date(),  # Default to the latest date
    min_value=pd.to_datetime(df["Timestamp"].min()).date(),
    max_value=pd.to_datetime(df["Timestamp"].max()).date()
)

# Ensure valid date range
if start_day > end_day:
    st.sidebar.error("The 'From' date cannot be later than the 'Until' date.")
else:
    # Apply the date range filter
    df = df[(df["Timestamp"].dt.date >= start_day) & (df["Timestamp"].dt.date <= end_day)]

User = st.sidebar.multiselect(
    "Select User",
    options=df["User"].unique(),
)

Action = st.sidebar.multiselect(
    "Select Action",
    options=df["Action"].unique(),
)

IPAddress = st.sidebar.multiselect(
    "Select IP Address",
    options=df["IPAddress"].unique(),
)

if User or Action or IPAddress:
    df_selection = df[
        (df["User"].isin(User) if User else True) &
        (df["IPAddress"].isin(IPAddress) if IPAddress else True) &
        (df["Action"].isin(Action) if Action else True)
    ]
else:
    df_selection = df



st.dataframe(df_selection)


if not df_selection.empty:
    # Calculate total actions per user
    actions_by_user = (
        df_selection.groupby(by=["User"], as_index=False).size()
    )
    actions_by_user.rename(columns={"size": "Total Actions"}, inplace=True)
    actions_by_user = actions_by_user.sort_values(by="Total Actions", ascending=False)

    # Calculate total hours for each user per day
    daily_hours = (
        df_selection.groupby(["User", "Day"])["Timestamp"].agg(
            earliest="min",
            latest="max"
        ).reset_index()
    )
    # Calculate hours per day for each user
    daily_hours["Daily Total Hours"] = ((daily_hours["latest"] - daily_hours["earliest"]).dt.total_seconds() / 3600).round(2)

    # Sum daily total hours across all days for each user
    total_hours_by_user = (
        daily_hours.groupby("User")["Daily Total Hours"].sum().reset_index()
    )
    total_hours_by_user.rename(columns={"Daily Total Hours": "Total Hours"}, inplace=True)

    # Merge total actions and total hours into a single table
    user_summary = pd.merge(
        actions_by_user,
        total_hours_by_user,
        on="User",
        how="left"
    )

    # Display the summary
    st.write("User Summary (Total Actions and Hours):")
    st.dataframe(user_summary)


if not df_selection.empty:
    # Calculate earliest start time for each user
    user_start_times = df_selection.groupby("User")["Timestamp"].min().reset_index()
    user_start_times.rename(columns={"Timestamp": "Earliest Start"}, inplace=True)

    # Merge start times back into the main data
    df_selection = df_selection.merge(user_start_times, on="User", how="left")

    # Count actions by User and Action
    actions_by_user = df_selection.groupby(["User", "Action"]).size().reset_index(name="Count")

    # Sort users by earliest start time
    actions_by_user = actions_by_user.merge(user_start_times, on="User", how="left")
    actions_by_user = actions_by_user.sort_values(by="Earliest Start", ascending=True)

    # Create a stacked bar chart
    fig_actions = px.bar(
    actions_by_user,
    x="Count",
    y="User",
    color="Action",
    orientation="h",
    template="plotly_white",
    title="Action Breakdown by User",
    hover_data=["Earliest Start"],  # Include start time in hover info
    labels={"Count": "Total Actions", "User": "User", "Action": "Action Type"}
)

    # Show the chart in Streamlit
    st.plotly_chart(fig_actions)

if not df_selection.empty:
    # Calculate total actions per user
    actions_by_user = (
        df_selection.groupby(by=["User"], as_index=False).size()
    )
    actions_by_user.rename(columns={"size": "Total Actions"}, inplace=True)
    actions_by_user = actions_by_user.sort_values(by="Total Actions", ascending=False)

    # Calculate earliest start time for each user
    user_start_times = df_selection.groupby("User")["Timestamp"].min().reset_index()
    user_start_times.rename(columns={"Timestamp": "Earliest Start Time"}, inplace=True)

    # Merge actions and earliest start time into a single table
    user_summary = pd.merge(
        actions_by_user,
        user_start_times,
        on="User",
        how="left"
    )


    # Create a dot chart for earliest start time
    fig_earliest_start = px.scatter(
        user_start_times,
        x="Earliest Start Time",
        y="User",
        size_max=10,  # Adjust the size of the dots
        template="plotly_white",
        title="Start Time Per User",
        labels={"Earliest Start Time": "Earliest Start Time", "User": "User"},
    )

    # Show the chart in Streamlit
    st.plotly_chart(fig_earliest_start)


















