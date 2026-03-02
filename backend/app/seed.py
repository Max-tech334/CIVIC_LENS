import os
import sys
import pandas as pd

# 1. Add the 'backend' directory to the Python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# 2. Using absolute imports from the 'app' folder
from app.database import SessionLocal, engine
from app import models

# Define where the CSV files live
DATA_DIR = os.path.join(BASE_DIR, "data")

def clean_df(df):
    """Replaces pandas NaN values with Python None for PostgreSQL compatibility."""
    return df.where(pd.notnull(df), None)

def load_csv_safely(filename):
    """Smart loader: Attempts strict UTF-8, falls back to Latin-1, and bulldozes broken rows."""
    filepath = os.path.join(DATA_DIR, filename)
    try:
        # on_bad_lines='skip' will completely ignore rows with extra/missing commas
        return pd.read_csv(filepath, encoding='utf-8-sig', on_bad_lines='skip')
    except UnicodeDecodeError:
        return pd.read_csv(filepath, encoding='latin1', on_bad_lines='skip')

def seed_database():
    db = SessionLocal()
    print("🌱 Starting the database seeding process...")

    try:
        # 1. Seed Election Cycles
        print("Loading Election Cycles...")
        df_cycles = clean_df(load_csv_safely("ELECTION_CYCLE.csv"))
        for _, row in df_cycles.iterrows():
            db.merge(models.ElectionCycle(**row.to_dict()))
        db.commit()

        # 2. Seed Counties
        print("Loading Counties...")
        df_counties = clean_df(load_csv_safely("COUNTIES.csv"))
        for _, row in df_counties.iterrows():
            db.merge(models.County(**row.to_dict()))
        db.commit()

        # 3. Seed Candidates
        print("Loading Candidates...")
        df_candidates = clean_df(load_csv_safely("Candidates.csv"))
        for _, row in df_candidates.iterrows():
            candidate_data = row.to_dict()
            # Map CSV column names to model field names
            if 'full_name' in candidate_data:
                candidate_data['name'] = candidate_data.pop('full_name')
            if 'position' in candidate_data:
                candidate_data['office_sought'] = candidate_data.pop('position')
            db.merge(models.Candidate(**candidate_data))
        db.commit()

        # 4. Seed Donors
        print("Loading Donors...")
        df_donors = clean_df(load_csv_safely("DONORS.csv"))
        for _, row in df_donors.iterrows():
            db.merge(models.Donor(**row.to_dict()))
        db.commit()

        # 5. Seed Donations
        print("Loading Donations...")
        df_donations = clean_df(load_csv_safely("DONATIONS.csv"))
        for _, row in df_donations.iterrows():
            db.merge(models.Donation(**row.to_dict()))
        db.commit()
        
        # 6. Seed Simulation Parameters
        print("Loading Simulation Parameters...")
        df_params = clean_df(load_csv_safely("SIMULATION_PARAMETERS.csv"))
        for _, row in df_params.iterrows():
            db.merge(models.SimulationParameter(**row.to_dict()))
        db.commit()

        print("✅ Success! The database is fully populated and ready for the laboratory.")

    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Ensuring tables exist just in case someone forgot to run Alembic
    models.Base.metadata.create_all(bind=engine)
    seed_database()