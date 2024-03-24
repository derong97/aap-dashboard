import streamlit as st
import pandas as pd
from datetime import datetime
from toml import load as toml_load
import re
import socket
from config import Config

st.set_page_config(
    page_title="All Patients",
    layout="wide",
    initial_sidebar_state="expanded",
)

def format_age(age_in_years):
    years = int(age_in_years)
    months = int((age_in_years - years) * 12)
    return f"{years}y {months}m"


def format_age_in_datetime(age_in_datetime):
    years = age_in_datetime // pd.Timedelta(days=365.25)
    months = (age_in_datetime % pd.Timedelta(days=365.25)) // pd.Timedelta(days=30.44)
    return f"{years}y {months}m"


def format_hyperlink(url, mrn):
    return f"{url}/Patient_Lookup?mrn={mrn}"

config = Config(**toml_load("config.toml"))

PORT = 8501
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip_address = s.getsockname()[0]
s.close()

df = pd.read_csv(config.patient_data)

for label in ["Autism", "ADHD"]:
    # Convert label probability to percentage
    df[f"{label} Likelihood"] = df[f"{label} Likelihood"] * 100

    # Reformatting
    diagnosed_indices = df[f"{label} Label"] == 1
    df.loc[diagnosed_indices, f"{label} Diagnosis Age"] = df.loc[
        diagnosed_indices, f"{label} Diagnosis Age"
    ].apply(format_age)


df["MRN"] = df["MRN"].apply(
    lambda MRN: format_hyperlink("http://" + ip_address + f":{PORT}", MRN)
)
df["Censoring Age"] = df["Censoring Age"].apply(format_age)
df["Date of Birth"] = pd.to_datetime(df["Date of Birth"])
age_in_datetime = datetime.now() - df["Date of Birth"]
df["Current Age"] = age_in_datetime.apply(format_age_in_datetime)
df["Date of Birth"] = df["Date of Birth"].dt.date

search_query = st.sidebar.text_input("Search Patient Name")
df = df[df["Name"].str.contains(search_query, case=False)]

st.sidebar.write("Filter Options")

# Show patients with Autism and/or ADHD diagnosis
show_autism = st.sidebar.checkbox("Show Autism Patients", value=False)
show_adhd = st.sidebar.checkbox("Show ADHD Patients", value=False)
df_filtered = df[(df["Autism Label"] == show_autism) & (df["ADHD Label"] == show_adhd)]

# Show columns in final dataframe
default_columns = [
    "Name",
    "Date of Birth",
]
optional_columns = ["Name", "Date of Birth", "Current Age", "Censoring Age", "Sex", "Race", "Insurance", "Autism Diagnosis Age", "Autism Likelihood", "ADHD Diagnosis Age", "ADHD Likelihood"]
columns_to_hide = ["MRN"]

if show_autism:
    default_columns.append("Autism Diagnosis Age")
else:
    default_columns.append("Autism Likelihood")
if show_adhd:
    default_columns.append("ADHD Diagnosis Age")
else:
    default_columns.append("ADHD Likelihood")

# don't allow user to deselect mrn column, else there will be no more dataframe
columns_to_show = ["MRN"] + st.sidebar.multiselect(
    "Show table columns",
    options=optional_columns,
    default=default_columns,
)

st.header("EHR Dataset 🏥")
st.markdown("**Number of patients: {}**".format(len(df_filtered[columns_to_show])))
st.caption(
    "**Directions**: You can use the search and filter functions on the left menu, and click on the column headers to reorder the rows."
)
st.dataframe(
    df_filtered[columns_to_show].sort_values(by="MRN", ascending=False),
    column_config={
        "MRN": st.column_config.LinkColumn(
            max_chars=100,
            display_text=f"http://{re.escape(ip_address)}:{PORT}/Patient_Lookup\?mrn=([\w\d]+)",
        ),
        "Censoring Age": st.column_config.TextColumn(help="Age at last follow-up"),
        "Autism Likelihood": st.column_config.NumberColumn(
            format="%.1f%%",
            help="Probability of Autism diagnosis (%) by 9 years old",
        ),
        "ADHD Likelihood": st.column_config.NumberColumn(
            format="%.1f%%",
            help="Probability of ADHD diagnosis (%) by 9.2 years old",
        ),
    },
    hide_index=True,
    use_container_width=True,
)
st.caption(
    "**Note**: Predictions are updated weekly and may not capture patients' most recent information."
)
