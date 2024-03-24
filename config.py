from pydantic import BaseModel
from pathlib import Path
from typing import List

class Diagnoses(BaseModel):
    name: str
    bin_boundaries: List
    testset_results: Path

class Autism(Diagnoses):
    pass

class ADHD(Diagnoses):
    pass


class Config(BaseModel):
    patient_data: Path
    autism: Diagnoses
    adhd: Diagnoses
