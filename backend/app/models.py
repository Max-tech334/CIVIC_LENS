from sqlalchemy import Column, Integer, String, Numeric, Date
from .database import Base

class Donation(Base):
    __tablename__ = "donations"
    
    donation_id = Column(Integer, primary_key=True, index=True)
    donor_id = Column(String(50))
    candidate_id = Column(String(50))
    amount = Column(Numeric)
    date = Column(Date)
    election_year = Column(Integer)

class Donor(Base):
    __tablename__ = "donors"
    
    donor_id = Column(String(50), primary_key=True, index=True)
    name = Column(String(255))
    type = Column(String(50))
    industry = Column(String(100))
    home_county = Column(String(100))
    tier = Column(Integer)


class Candidate(Base):
    __tablename__ = "candidates"
    
    candidate_id = Column(String(50), primary_key=True, index=True)
    name = Column(String(255))
    party = Column(String(100))
    office_sought = Column(String(100))
    county = Column(String(100))
    election_year = Column(Integer)

class County(Base):
    __tablename__ = "counties"
    
    county_name = Column(String(100), primary_key=True, index=True)
    registered_voters = Column(Integer)

class ElectionCycle(Base):
    __tablename__ = "election_cycles"
    
    election_year = Column(Integer, primary_key=True, index=True)

class SimulationParameter(Base):
    __tablename__ = "simulation_parameters"
    
    parameter = Column(String(100), primary_key=True, index=True)
    default_value = Column(String(100))

