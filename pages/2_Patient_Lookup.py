import streamlit as st
from toml import load as toml_load
from scipy import stats
import pandas as pd
import plotly.graph_objs as go

from config import Config

st.set_page_config(
    page_title="Patient Lookup",
    layout="wide",
    initial_sidebar_state="expanded",
)

config = Config(**toml_load("config.toml"))
ALL_DF = pd.read_csv(config.patient_data)

def render_demographics(df):
    demographics = ["Name", "Date of Birth", "Patient Status", "Sex", "Race", "Insurance", "Primary Care Provider", "Emergency Contact Name", "Emergency Contact Relationship", "Emergency Contact Home Phone", "Email Address", "Address"]

    st.header("📝 Demographics", divider=True)
    with st.container(height=300, border=False):
        for column in demographics:
            st.write(f"**{column}**: {df.iloc[0][column]}")


def render_pmhx(mrn_df):
    active_pmhx = eval(mrn_df["Active Medical History"].iloc[0])
    resolved_pmhx = eval(mrn_df["Resolved Medical History"].iloc[0])

    st.header("🦠 Problem List", divider=True)
    if active_pmhx:
        st.subheader("Active Problems")
        active_df = pd.DataFrame(active_pmhx)
        active_df.index = active_df.index + 1
        st.dataframe(active_df, use_container_width=True)
    if resolved_pmhx:
        st.subheader("Resolved Problems")
        resolved_df = pd.DataFrame(resolved_pmhx)
        resolved_df.index = resolved_df.index + 1
        st.dataframe(resolved_df, use_container_width=True)
    if not active_pmhx and not resolved_pmhx:
        st.write("NIL")

def render_events(mrn_df):
    clinical_encounters = eval(mrn_df["Clinical Encounters"].iloc[0])
    st.header("🏥 Clinical Encounters", divider=True)
    
    print(clinical_encounters)
    with st.container(height=500, border=False):
        for index, (encounter_date, events) in enumerate(clinical_encounters.items(), start=1):
            st.subheader(f"{index}. {events['Encounter Type']} ({encounter_date})")
            diagnosis = events["Diagnosis"]
            medication = events["Medication"]
            procedure = events["Procedure"]
            lab_test = events["Lab Test"]
            
            # create a df with the largest array length as the number of rows, and fill in with values from the arrays
            max_length = max(len(diagnosis), len(medication), len(procedure), len(lab_test))
            event_df = pd.DataFrame(index=range(max_length), columns=['Diagnosis', 'Medication', 'Procedure', 'Lab Test'])
            event_df['Diagnosis'][:len(diagnosis)] = diagnosis
            event_df['Medication'][:len(medication)] = medication
            event_df['Procedure'][:len(procedure)] = procedure
            event_df['Lab Test'][:len(lab_test)] = lab_test
            st.dataframe(
                event_df,
                hide_index=True,
                use_container_width=True,
            )

def format_bins(bin_boundaries):
    """
    Ex: If bin boundaries = [0.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.2],
    return ['0-4', '4-5', '5-6', '6-7', '7-8', '8-9.2', '≥9.2']
    """
    ranges = []
    for i in range(len(bin_boundaries) - 1):
        start_value = (
            int(bin_boundaries[i])
            if bin_boundaries[i].is_integer()
            else bin_boundaries[i]
        )
        end_value = (
            int(bin_boundaries[i + 1])
            if bin_boundaries[i + 1].is_integer()
            else bin_boundaries[i + 1]
        )

        ranges.append(f"{start_value}-{end_value}")

    last_range = (
        f"≥{int(bin_boundaries[-1])}"
        if bin_boundaries[-1].is_integer()
        else f"≥{bin_boundaries[-1]}"
    )
    ranges.append(last_range)
    return ranges


def render_likelihood(mrn, label):
    config_diagnosis = getattr(config, label)
    st.header(f"🩺 Likelihood of {config_diagnosis.name} diagnosis", divider=True)

    mrn_df = ALL_DF[ALL_DF["MRN"] == mrn]
    diagnosed = mrn_df[f"{config_diagnosis.name} Label"].iloc[0]
    patient_name = mrn_df["Name"].iloc[0]

    if diagnosed:
        age_diagnosed = mrn_df[f"{config_diagnosis.name} Diagnosis Age"]
        years = int(age_diagnosed)
        months = int((age_diagnosed - years) * 12)
        st.write(f"First diagnosed at {years}y {months}m")

    else:
        # Predicted probability for each bin
        indiv_probability = mrn_df[f"{config_diagnosis.name} Likelihood"].iloc[0]
        all_probability = ALL_DF[f"{config_diagnosis.name} Likelihood"]

        percentile = stats.percentileofscore(all_probability, indiv_probability)

        if percentile > 50:
            st.markdown(
                f"Predicted probability* of {config_diagnosis.name} diagnosis is :red[**{indiv_probability*100:.1f}%**].\n \
                This is higher than :red[**{percentile:.1f}%**] of the entire population."
            )
        else:
            st.markdown(
                f"Predicted probability* of {config_diagnosis.name} diagnosis is :green[**{indiv_probability*100:.1f}%**].\n \
                This is lower than :green[**{100-percentile:.1f}%**] of the entire population."
            )

        st.caption(
            f"*cumulative predicted probability until t={config_diagnosis.bin_boundaries[-1]}y"
        )

        binned_predictions = eval(mrn_df[f"{config_diagnosis.name} Predictions"].iloc[0])

        ranges = format_bins(config_diagnosis.bin_boundaries)
        binned_prob_data = {
            "Years": ranges,
            "Probability": binned_predictions,
        }
        st.markdown("###### Binned Probabilities")
        st.bar_chart(
            binned_prob_data, x="Years", y="Probability", use_container_width=True
        )
        st.caption(
            f"""
            The predicted probability in each time bucket represents the likelihood of {config_diagnosis.name} diagnosis within that specific age range. 
            The last bucket represents the predicted probability of no-diagnosis before {config_diagnosis.bin_boundaries[-1]} year old.
            """
        )

        # Subgroup analysis
        year = pd.to_datetime(mrn_df["Date of Birth"]).dt.year.iloc[0]
        sex = mrn_df["Sex"].iloc[0]
        race = mrn_df["Race"].iloc[0]

        fig = go.Figure()
        fig.add_trace(
            go.Box(
                y=all_probability,
                boxpoints=False,
                name="Population",
                showlegend=False,
                line_color="blue",
            )
        )
        fig.add_trace(
            go.Box(
                y=ALL_DF.loc[
                    pd.to_datetime(ALL_DF["Date of Birth"]).dt.year == year,
                    f"{config_diagnosis.name} Likelihood",
                ],
                boxpoints=False,
                name=f"YOB ({year})",
                showlegend=False,
                line_color="blue",
            )
        )
        fig.add_trace(
            go.Box(
                y=ALL_DF.loc[ALL_DF["Sex"] == sex, f"{config_diagnosis.name} Likelihood"],
                boxpoints=False,
                name=f"Sex ({sex})",
                showlegend=False,
                line_color="blue",
            )
        )
        fig.add_trace(
            go.Box(
                y=ALL_DF.loc[ALL_DF["Race"] == race, f"{config_diagnosis.name} Likelihood"],
                boxpoints=False,
                name=f"Race ({race})",
                showlegend=False,
                line_color="blue",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=["Population", f"YOB ({year})", f"Sex ({sex})", f"Race ({race})"],
                y=[
                    indiv_probability,
                    indiv_probability,
                    indiv_probability,
                    indiv_probability,
                ],
                mode="markers",
                marker=dict(size=8, color="red"),
                name=f"{patient_name}",
            )
        )

        fig.update_layout(
            title="Sub-group Analysis",
            yaxis_title="Predicted Probabilities",
            xaxis_title="Sub-Groups",
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=1.1,
                xanchor="right",
                x=1,
            ),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption(
            f"The patient's predicted probability for {config_diagnosis.name} is being compared to the whole dataset, and individuals of the same birth year, sex and race."
        )

st.title("Search by MRN 👇")

query_params = st.query_params.to_dict()

query_mrn = st.text_input(
    label="Enter mrn",
    value=query_params.get("mrn"),
    placeholder="e.g. Z827898",
    label_visibility="collapsed",
)

if query_mrn:
    mrn_df = ALL_DF[ALL_DF["MRN"] == query_mrn].reset_index(drop=True)
    if mrn_df.empty:
        st.write("No matching records found.")

    else:
        render_demographics(mrn_df)
        render_pmhx(mrn_df)
        render_events(mrn_df)
        render_likelihood(query_mrn, "autism")
        render_likelihood(query_mrn, "adhd")
