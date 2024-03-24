# EHR Neurodevelopmental Dashboard
This is a dashboard hosted in PACE to assist clinicians with autism and ADHD diagnoses. Due to patient confidentiality, we have removed the EHR data pipeline and simulated the dashboard using synthetic patient data.

## Pre-requisites
1. `python3 -m venv myenv`
2. `source myenv/bin/activate`
3. `pip install -r requirements.txt`

## Start the application
`streamlit run Dashboard_Overview.py`

## Content of each page

1. Dashboard Overview
    - Summary
    - Model Facts
    - Uses and directions
    - Warnings
    - Other information
2. All Patients
	- Search patient name
	- Filter function (includes drop-down menu) to add or remove columns
	- Clickable MRN hyperlink
	- Reorder rows (in ascending/descending order)
3. Patient Lookup
	- Search patient MRN
	- Demographics
	- Problem list (active and resolved)
	- Clinical encounters (organized by type and length of encounter, with associated diagnosis, medication, procedure, lab test)
	- individual's ASD and ADHD likelihood of diagnosis over lifetime
    - individual's ASD and ADHD likelihood of diagnosis (relative to others with similar demographics)
	- interactive graphs

4. Model Performance
	- AUCt
    - APt
    - cumulative predicted probability curve

