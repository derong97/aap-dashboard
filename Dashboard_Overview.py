import streamlit as st

st.set_page_config(
    page_title="Neurodevelopmental Prediction Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Neurodevelopmental Prediction Dashboard 👶")

st.subheader("📄 Summary", divider=True)
st.markdown(
    """
    This dashboard integrates EHR data and provides real-time insights into patient information at both population and individual levels at a glance. 
    It predicts the probability of **autism** and **ADHD** diagnoses at different ages for each patient, which may help with your clinical management. 
    """
)

st.subheader("🤖 Model Facts", divider=True)
st.markdown(
    """
    **Outcome**: diagnosis of autism/ADHD within the prediction timeline\n
    **Output**: predicted probabilities for specific age ranges
    - ASD: 0-3, 3-4, 4-5, 5-6, 6-7, 7-8, 8-9, ≥9 years old
    - ADHD: 0-4, 4-5, 5-6, 6-7, 7-8, 8-9.2, ≥9.2  years old\n
    **Target population**: all children within Duke University Health System (DUHS)\n
    **Input data source**: Electronic Health Record (EHR)\n
    **Input data type**: diagnoses, medications, procedures, lab tests before 15 months (autism) and 3 years (ADHD)\n
    **Training data location and time-period**: DUHS, 09/2023 - 01/2024\n
    **Model type**: Discrete-time neural network
    """
)

st.subheader("↗️ Uses and directions", divider=True)
st.markdown(
    """
    **Benefits**: Early identification and management of autism/ADHD can improve patient's quality of life.\n
    **Target population and use case**: Every week, data is pulled from the EHR to calculate the likelihood of diagnosis 
    for every child within DUHS. Clinicians reviews high-risk patients and decide on follow-up plans.\n
    **General use**: This model is intended to assist clinicians in identifying at-risk patients for further
    assessment. The model is not diagnostic, and is not meant to drive or guide clinical care.
    """
)

st.subheader("⚠️ Warnings", divider=True)
st.markdown(
    """
    **Risks**: Even if used appropriately, clinicians using this model can misdiagnose autism/ADHD. Delays in diagnosis can 
    lead to missed opportunities for timely intervention and contribute to poorer patient outcomes. Patients who are 
    incorrectly diagnosed are unnecessarily subjected to inappropriate management, associated stigma and anxiety.\n
    **Clinical rationale**: The model is not interpretable and does not provide explanations for the predicted probabilities. 
    Clinicians are expected to consider the model outputs in context with other clinical information to make final determination 
    of diagnosis.\n
    **Generalizability**: This model was primarily evaluated within the local setting of DUHS. Do not use this model in an 
    external setting without further evaluation.\n
    **Discontinue use if**: There are concerns regarding the utility of the model for the indicated use case or large, 
    systemic changes occur at the data level that necessitates re-training of the model.
    """
)

st.subheader("⚡️ Other information", divider=True)
st.markdown(
    """
    **Model development and validation**: <publication link>\n
    **Model implementation**: <publication link>\n
    **Clinical trial**: <publication link>\n
    **Clinical impact evaluation**: <publication link>\n
    **For inquiries and additional information**: please email derong@u.duke.nus.edu
    """
)
