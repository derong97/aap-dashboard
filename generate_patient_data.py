import csv
from faker import Faker
import numpy as np
import random
from toml import load as toml_load
from datetime import datetime
from config import Config

config = Config(**toml_load("config.toml"))
fake = Faker()

def generate_predictions(num_bins, min_age, mean_age, std, censoring_age):
    diagnosis_age = None
    diagnosed = 1 if random.random() <= 0.20 else 0  # randomly select 20% of people to be diagnosed

    likelihood = np.clip(np.random.normal(loc=0.2, scale=0.1), 0, 1)
    probs = [random.random() for _ in range(num_bins-1)]
    total_prob = sum(probs)
    scaled_probs = [prob * likelihood / total_prob for prob in probs]
    last_prob = 1 - likelihood
    scaled_probs.append(last_prob)
    
    if diagnosed == 1:
        diagnosis_age = np.random.normal(loc=mean_age, scale=std)
        diagnosis_age = random.uniform(min_age, censoring_age)
   
    return diagnosed, diagnosis_age, scaled_probs, likelihood

def generate_pmhx(dob, last_follow_up_date, resolved=False):
    pmhx = []
    num_issues = random.randint(0, 10)
    for _ in range(num_issues):
        noted_date = fake.date_between(start_date=dob, end_date=last_follow_up_date)
        issue = {
            "Diagnosis Name": fake.word(),
            "ICD-10": generate_icd10(),
            "Noted Date": noted_date.strftime("%Y-%m-%d"),
        }
        if resolved:
            issue["Resolved Date"] = fake.date_between(start_date=noted_date, end_date=last_follow_up_date).strftime("%Y-%m-%d")
        pmhx.append(issue)
    
    return pmhx

def generate_icd10():
    letter = random.choice('ABCDEFGHIJKL')
    category = random.randint(0, 99)
    subcategory = random.randint(0, 99)
    extension = random.choice('ABCDEFGHIJKL')
    return f"{letter}{category:02d}.{subcategory:02d}{extension}"

def generate_event_list(max_num):
    return [fake.word() for _ in range(random.randint(0,max_num))]

def generate_clinical_encounters(dob, last_follow_up_date):
    clinical_encounters = {}
    num_encounters = random.randint(1, 10)
    
    # generate events for each encounter
    for _ in range(num_encounters):
        encounter_date = fake.date_time_between_dates(dob, last_follow_up_date).strftime("%Y-%m-%d %H:%M")
        if encounter_date not in clinical_encounters:
            clinical_encounters[encounter_date] = {}
        
        clinical_encounters[encounter_date]['Encounter Type'] = random.choice(["Hospital Encounter", "Office Visit"])
        clinical_encounters[encounter_date]['Diagnosis'] = generate_event_list(10)
        clinical_encounters[encounter_date]['Medication'] = generate_event_list(5)
        clinical_encounters[encounter_date]['Procedure'] = generate_event_list(5)
        clinical_encounters[encounter_date]['Lab Test'] = generate_event_list(10)

    sorted_encounters = dict(sorted(clinical_encounters.items(), key=lambda item: item[0]))

    return sorted_encounters

patient_data = []
for _ in range(10000):
    dob = fake.date_time_between_dates(datetime(2014, 1, 1), datetime(2022, 10, 29))
    last_follow_up_date = fake.date_time_between_dates(dob, datetime(2023, 6, 2))
    censoring_age = (last_follow_up_date - dob).days // 365
    
    autism_label, autism_diagnosis_age, autism_binned_probs, autism_likelihood = generate_predictions(len(config.autism.bin_boundaries), 1.5, 5, 2, censoring_age)
    adhd_label, adhd_diagnosis_age, adhd_binned_probs, adhd_likelihood = generate_predictions(len(config.adhd.bin_boundaries), 2, 7, 3, censoring_age)

    patient = {
        "MRN": random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') + str(fake.unique.random_int(min=100000, max=999999)),
        "Name": f"{fake.first_name()} {fake.last_name()}",
        "Date of Birth": dob.strftime("%Y-%m-%d"),
        "Patient Status": random.choices(["Alive", "Dead"], weights=[9, 1])[0],
        "Last Follow-up Date": last_follow_up_date.strftime("%Y-%m-%d"),
        "Censoring Age": censoring_age,
        "Sex": fake.random_element(elements=["Male", "Female"]),
        "Race": fake.random_element(elements=("White/Caucasian", "Black/African American", "Asian", "Hispanic", "Unavailable", "Others")),
        "Insurance": fake.random_element(elements=("Medicare", "Other Government", "Managed Care", "Blue Cross", "Commercial", "Self-pay", "Others")),
        "Primary Care Provider": fake.name(),
        "Emergency Contact Name": fake.name(),
        "Emergency Contact Relationship": fake.random_element(elements=("Father", "Mother", "Guardian")),
        "Emergency Contact Home Phone": fake.phone_number(),
        "Email Address": fake.email(),
        "Address": fake.address(),
        "Autism Label": autism_label,
        "Autism Diagnosis Age": autism_diagnosis_age,
        "Autism Predictions": autism_binned_probs,
        "Autism Likelihood": autism_likelihood,
        "ADHD Label": adhd_label,
        "ADHD Diagnosis Age": adhd_diagnosis_age,
        "ADHD Predictions": adhd_binned_probs,
        "ADHD Likelihood": adhd_likelihood,
        "Active Medical History": generate_pmhx(dob, last_follow_up_date, False),
        "Resolved Medical History": generate_pmhx(dob, last_follow_up_date, True),
        "Clinical Encounters": generate_clinical_encounters(dob, last_follow_up_date)
    }
    patient_data.append(patient)

# Write data to CSV file
with open(config.patient_data, 'w', newline='') as csvfile:
    fieldnames = patient_data[0].keys() if patient_data else []
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(patient_data)

print("CSV file generated successfully.")
