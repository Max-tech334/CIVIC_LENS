from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import networkx as nx
import community.community_louvain as community_louvain
import geopandas as gpd
import json
import os
import pandas as pd
from datetime import date  # Added for timestamping new donations
from typing import Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# Load the environment variables my API key
load_dotenv()

# Import my database connections and models
from .database import get_db
from . import models

app = FastAPI(title="Civic Lens API")

# --- SECURITY & CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# PHASE 1: BASIC ENDPOINTS
# ==========================================

@app.get("/api/candidates")
def get_candidates(db: Session = Depends(get_db)):
    return db.query(models.Candidate).all()

@app.get("/api/donors")
def get_donors(db: Session = Depends(get_db)):
    return db.query(models.Donor).all()

# ==========================================
# PHASE 2: GRAPH MATH ENGINE
# ==========================================

@app.get("/api/network-metrics")
def get_network_metrics(db: Session = Depends(get_db)):
    candidates = db.query(models.Candidate).all()
    donors = db.query(models.Donor).all()
    donations = db.query(models.Donation).all()

    G = nx.Graph()

    for c in candidates:
        name = getattr(c, 'full_name', getattr(c, 'name', 'Unknown'))
        G.add_node(c.candidate_id, name=name, node_type="Candidate") 
        
    for d in donors:
        name = getattr(d, 'name', getattr(d, 'full_name', 'Unknown'))
        G.add_node(d.donor_id, name=name, node_type="Donor")

    for don in donations:
        if G.has_node(don.donor_id) and G.has_node(don.candidate_id):
            amount_float = float(don.amount) 
            if G.has_edge(don.donor_id, don.candidate_id):
                G[don.donor_id][don.candidate_id]['weight'] += amount_float
            else:
                G.add_edge(don.donor_id, don.candidate_id, weight=amount_float)        

    centrality = {}
    partition = {}
    
    if len(G.nodes) > 0:
        centrality = nx.degree_centrality(G)
        if len(G.edges) > 0:
            partition = community_louvain.best_partition(G, weight='weight')
        else:
            partition = {node: 0 for node in G.nodes()}

    nodes_list = []
    for node_id in G.nodes():
        node_data = G.nodes[node_id]
        nodes_list.append({
            "id": node_id,
            "name": node_data.get("name", "Unknown"),
            "group": node_data.get("node_type", "Unknown"),
            "centrality_score": centrality.get(node_id, 0),
            "community_id": partition.get(node_id, 0)
        })

    links_list = []
    for u, v, data in G.edges(data=True):
        links_list.append({
            "source": u, "target": v, "amount": data.get("weight", 0)
        })

    return {"nodes": nodes_list, "links": links_list}

# ==========================================
# PHASE 3: GEOGRAPHIC INFLUENCE (THE MISSING LINK)
# ==========================================

@app.get("/api/geographic-influence")
def get_geographic_influence(db: Session = Depends(get_db)):
    try:
        # 1. Fetch raw data
        donations = db.query(models.Donation).all()
        candidates = db.query(models.Candidate).all()
        
        # Create lookup for county by candidate_id
        # FIXED: Normalize database names to Title Case (e.g., "Nairobi")
        candidate_county_map = {c.candidate_id: str(c.county).strip().title() for c in candidates}
        
        # 2. Aggregation Math
        county_funds = {}
        total_national_funds = 0

        for don in donations:
            county_name = candidate_county_map.get(don.candidate_id, "Unknown")
            amount = float(don.amount)
            
            county_funds[county_name] = county_funds.get(county_name, 0) + amount
            total_national_funds += amount

        # 3. Load Kenya GeoJSON
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        geojson_path = os.path.join(base_path, "data", "kenya_counties.geojson")
        
        if not os.path.exists(geojson_path):
            raise FileNotFoundError(f"GeoJSON file missing at {geojson_path}")

        gdf = gpd.read_file(geojson_path)
        
        # 4. Inject Math into Map
        def calculate_metrics(row):
            # FIXED: Handle all possible GeoJSON naming keys and normalize to Title Case
            raw_name = row.get('COUNTY_NAM', row.get('COUNTY', row.get('name', 'Unknown')))
            c_name = str(raw_name).strip().title()
            
            amount_raised = county_funds.get(c_name, 0)
            fci = (amount_raised / total_national_funds * 100) if total_national_funds > 0 else 0
            
            return pd.Series([float(amount_raised), round(float(fci), 2)])

        gdf[['total_raised', 'fci_score']] = gdf.apply(calculate_metrics, axis=1)

        # 5. Return JSON
        return json.loads(gdf.to_json())

    except Exception as e:
        print(f"Error in Geographic Engine: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# PHASE 5: AI CAMPAIGN FINANCE EXPLAINER
# ==========================================

@app.get("/api/ai-explainer/{candidate_id}")
def get_ai_explanation(candidate_id: str, db: Session = Depends(get_db)):
    try:
        # 1. Fetch Candidate Data
        candidate = db.query(models.Candidate).filter(models.Candidate.candidate_id == candidate_id).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # 2. Fetch Donations & Calculate Math for the Prompt
        donations = db.query(models.Donation).filter(models.Donation.candidate_id == candidate_id).all()
        
        total_raised = sum(float(d.amount) for d in donations)
        
        # Find the top donor to calculate dependency percentage
        donor_totals = {}
        for d in donations:
            donor_totals[d.donor_id] = donor_totals.get(d.donor_id, 0) + float(d.amount)
        
        if not donor_totals:
            return {
                "english": f"{candidate.full_name} has no recorded financial data.",
                "swahili": f"{candidate.full_name} hana data ya kifedha iliyorekodiwa.",
                "infographic": ["No funds raised", "No donors found"]
            }
            
        top_donor_id = max(donor_totals, key=donor_totals.get)
        top_donor_amount = donor_totals[top_donor_id]
        top_donor_pct = (top_donor_amount / total_raised) * 100 if total_raised > 0 else 0

        # 3. Initialize OpenAI via LangChain
        llm = ChatOpenAI(temperature=0.3, model="gpt-3.5-turbo")

        # 4. Construct the Prompt Template
        prompt_template = PromptTemplate(
            input_variables=["candidate_name", "total", "top_pct"],
            template="""
            You are a political financial analyst for the Civic Lens laboratory in Kenya.
            Analyze this campaign finance data:
            - Candidate: {candidate_name}
            - Total Raised: KSh {total}
            - Highest Donor Concentration: {top_pct}% of total funds comes from a single top donor/cluster.

            Provide a response strictly in this JSON format. Do not use markdown blocks like ```json. Just output the raw JSON object:
            {{
                "english": "A one sentence plain English summary of their funding concentration.",
                "swahili": "The exact Kiswahili translation of the summary.",
                "infographic": [
                    "Bullet point 1 about the total war chest",
                    "Bullet point 2 about the reliance on the top donor",
                    "Bullet point 3 assessing their overall financial network health"
                ]
            }}
            """
        )
        
        # 5. Execute the AI Chain
        formatted_prompt = prompt_template.format(
            candidate_name=getattr(candidate, 'full_name', getattr(candidate, 'name', 'Unknown')),
            total=f"{total_raised:,.0f}",
            top_pct=f"{top_donor_pct:.1f}"
        )
        
        response = llm.invoke(formatted_prompt)
        
        # 6. Parse the LLM output into actual JSON
        clean_text = response.content.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)

    except Exception as e:
        print(f"AI Engine Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# PHASE 4: POLICY SIMULATION ENGINE (Pruning Algorithm)
# ==========================================

@app.post("/api/simulate-policy")
def simulate_policy(
    corporate_ban: bool = False,
    donation_cap: Optional[float] = None,
    public_funding_percent: float = 0,
    db: Session = Depends(get_db)
):
    """
    Simulate regulatory impact by pruning the donation network.
    
    Parameters:
    - corporate_ban: If true, remove all Corporate donor edges
    - donation_cap: If set, cap individual donations at this amount
    - public_funding_percent: Inject synthetic small-dollar donations (0-20%)
    """
    try:
        # 1. Load baseline data
        candidates = db.query(models.Candidate).all()
        donors = db.query(models.Donor).all()
        donations = db.query(models.Donation).all()

        # Helper: Build graph from donation list
        def build_graph(donation_list):
            G = nx.Graph()
            for c in candidates:
                name = getattr(c, 'full_name', getattr(c, 'name', 'Unknown'))
                G.add_node(c.candidate_id, name=name, node_type="Candidate")
            for d in donors:
                name = getattr(d, 'name', getattr(d, 'full_name', 'Unknown'))
                G.add_node(d.donor_id, name=name, node_type="Donor")
            for don in donation_list:
                if G.has_node(don.donor_id) and G.has_node(don.candidate_id):
                    amount_float = float(don.amount)
                    if G.has_edge(don.donor_id, don.candidate_id):
                        G[don.donor_id][don.candidate_id]['weight'] += amount_float
                    else:
                        G.add_edge(don.donor_id, don.candidate_id, weight=amount_float)
            return G

        # 2. Build BASELINE network (original state)
        baseline_graph = build_graph(donations)
        
        # 3. Apply regulations to create FILTERED list
        filtered_donations = []
        for don in donations:
            donor = next((d for d in donors if d.donor_id == don.donor_id), None)
            if not donor:
                continue
            
            # Rule 1: Corporate Ban
            if corporate_ban and donor.type == "Corporate":
                continue
            
            # Rule 2: Donation Cap
            if donation_cap is not None and float(don.amount) > donation_cap:
                # Cap the donation, don't exclude it
                capped_don = models.Donation(
                    donation_id=don.donation_id,
                    donor_id=don.donor_id,
                    candidate_id=don.candidate_id,
                    amount=donation_cap,
                    date=don.date,
                    election_year=don.election_year
                )
                filtered_donations.append(capped_don)
            else:
                filtered_donations.append(don)
        
        # 4. Apply public funding injection
        if public_funding_percent > 0 and public_funding_percent <= 20:
            total_funds = sum(float(d.amount) for d in filtered_donations)
            injection_per_candidate = (total_funds * public_funding_percent / 100) / len(candidates) if len(candidates) > 0 else 0
            
            # Create synthetic donations from a "Public Fund" donor
            fake_donor_id = "PUBLIC_FUND"
            for c in candidates:
                synthetic_don = models.Donation(
                    donation_id=999999,  # placeholder
                    donor_id=fake_donor_id,
                    candidate_id=c.candidate_id,
                    amount=injection_per_candidate,
                    date=date.today(),
                    election_year=2022 if len(candidates) > 0 else 2022
                )
                filtered_donations.append(synthetic_don)
        
        # 5. Build SIMULATED network from filtered donations
        simulated_graph = build_graph(filtered_donations)
        
        # 6. Calculate centrality for both graphs
        baseline_centrality = {}
        simulated_centrality = {}
        
        if len(baseline_graph.nodes) > 0:
            baseline_centrality = nx.degree_centrality(baseline_graph)
        if len(simulated_graph.nodes) > 0:
            simulated_centrality = nx.degree_centrality(simulated_graph)
        
        # 7. Community detection for both
        baseline_partition = {}
        simulated_partition = {}
        
        if len(baseline_graph.edges) > 0:
            baseline_partition = community_louvain.best_partition(baseline_graph, weight='weight')
        else:
            baseline_partition = {node: 0 for node in baseline_graph.nodes()}
        
        if len(simulated_graph.edges) > 0:
            simulated_partition = community_louvain.best_partition(simulated_graph, weight='weight')
        else:
            simulated_partition = {node: 0 for node in simulated_graph.nodes()}
        
        # 8. Format BASELINE nodes/links
        baseline_nodes = []
        for node_id in baseline_graph.nodes():
            node_data = baseline_graph.nodes[node_id]
            baseline_nodes.append({
                "id": node_id,
                "name": node_data.get("name", "Unknown"),
                "group": node_data.get("node_type", "Unknown"),
                "centrality_score": baseline_centrality.get(node_id, 0),
                "community_id": baseline_partition.get(node_id, 0)
            })
        
        baseline_links = []
        for u, v, data in baseline_graph.edges(data=True):
            baseline_links.append({
                "source": u,
                "target": v,
                "amount": data.get("weight", 0)
            })
        
        # 9. Format SIMULATED nodes/links
        simulated_nodes = []
        for node_id in simulated_graph.nodes():
            node_data = simulated_graph.nodes[node_id]
            simulated_nodes.append({
                "id": node_id,
                "name": node_data.get("name", "Unknown"),
                "group": node_data.get("node_type", "Unknown"),
                "centrality_score": simulated_centrality.get(node_id, 0),
                "community_id": simulated_partition.get(node_id, 0)
            })
        
        simulated_links = []
        for u, v, data in simulated_graph.edges(data=True):
            simulated_links.append({
                "source": u,
                "target": v,
                "amount": data.get("weight", 0)
            })
        
        # 10. Calculate comparison metrics
        baseline_total = sum(float(d.amount) for d in donations)
        simulated_total = sum(float(d.amount) for d in filtered_donations)
        funds_removed = baseline_total - simulated_total
        
        # Top 5 candidates comparison
        candidate_baseline = {}
        candidate_simulated = {}
        
        for c in candidates:
            candidate_baseline[c.candidate_id] = baseline_centrality.get(c.candidate_id, 0)
            candidate_simulated[c.candidate_id] = simulated_centrality.get(c.candidate_id, 0)
        
        top_5_comparison = []
        for cand_id in sorted(candidate_baseline.keys(), key=lambda x: candidate_baseline[x], reverse=True)[:5]:
            cand = next((c for c in candidates if c.candidate_id == cand_id), None)
            if cand:
                centrality_change = candidate_simulated.get(cand_id, 0) - candidate_baseline.get(cand_id, 0)
                top_5_comparison.append({
                    "candidate": getattr(cand, 'full_name', getattr(cand, 'name', 'Unknown')),
                    "baseline_centrality": round(candidate_baseline.get(cand_id, 0), 4),
                    "simulated_centrality": round(candidate_simulated.get(cand_id, 0), 4),
                    "centrality_change": round(centrality_change, 4)
                })
        
        # 11. Return comprehensive response
        return {
            "baseline": {
                "nodes": baseline_nodes,
                "links": baseline_links,
                "total_funds": baseline_total,
                "node_count": len(baseline_graph.nodes),
                "edge_count": len(baseline_graph.edges)
            },
            "simulated": {
                "nodes": simulated_nodes,
                "links": simulated_links,
                "total_funds": simulated_total,
                "node_count": len(simulated_graph.nodes),
                "edge_count": len(simulated_graph.edges)
            },
            "impact": {
                "funds_removed": funds_removed,
                "funds_removed_pct": round((funds_removed / baseline_total * 100) if baseline_total > 0 else 0, 2),
                "network_density_change": round((len(simulated_graph.edges) / len(baseline_graph.edges)) if len(baseline_graph.edges) > 0 else 0, 2),
                "top_5_candidates": top_5_comparison
            },
            "regulations_applied": {
                "corporate_ban": corporate_ban,
                "donation_cap": donation_cap,
                "public_funding_percent": public_funding_percent
            }
        }
        
    except Exception as e:
        print(f"Policy Simulation Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# PHASE 6: DATA INTAKE PIPELINE (AI to DB)
# ==========================================

@app.post("/api/upload")
async def upload_financial_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # 1. Read the uploaded file
        contents = await file.read()
        document_text = contents.decode("utf-8")
        
        # 2. Set up the LLM to act as a Data Engineer
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
        
        extraction_prompt = PromptTemplate(
            input_variables=["text"],
            template="""
            You are an expert financial data extraction AI. 
            Read the following raw text and extract all political campaign donations.
            
            Return the data STRICTLY as a valid JSON object with a single key "donations" 
            containing a list of objects. Each object must have:
            - "donor_name" (string)
            - "candidate_name" (string)
            - "amount" (integer, remove currency symbols and commas)
            
            Do not include any markdown formatting, backticks, or other text. Just the JSON.
            
            RAW TEXT:
            {text}
            """
        )
        
        # 3. Ask the AI to extract the data
        chain = extraction_prompt | llm
        response = chain.invoke({"text": document_text})
        
        # 4. Parse the AI's response and inject to PostgreSQL
        try:
            extracted_data = json.loads(response.content)
            
            # Extract the list of donations
            donations_list = extracted_data.get("donations", [])
            
            #  FIX: Manually calculate the next donation_id to prevent UniqueViolation 
            last_donation = db.query(models.Donation).order_by(models.Donation.donation_id.desc()).first()
            current_max_id = last_donation.donation_id if last_donation else 0

            for item in donations_list:
                cand_name = item.get("candidate_name", "Unknown Candidate")
                donor_name = item.get("donor_name", "Unknown Donor")
                amount = item.get("amount", 0)

                # Generate safe database IDs (e.g., "Peter Otieno" -> "peter_otieno")
                cand_id = cand_name.lower().replace(" ", "_")[:50]
                don_id = donor_name.lower().replace(" ", "_")[:50]

                # A. Check if Candidate exists, if not, create them
                existing_candidate = db.query(models.Candidate).filter(models.Candidate.candidate_id == cand_id).first()
                if not existing_candidate:
                    new_candidate = models.Candidate(candidate_id=cand_id, name=cand_name)
                    # db.add(new_candidate)  <-- COMMENTED OUT FOR SANDBOX

                # B. Check if Donor exists, if not, create them
                existing_donor = db.query(models.Donor).filter(models.Donor.donor_id == don_id).first()
                if not existing_donor:
                    new_donor = models.Donor(donor_id=don_id, name=donor_name)
                    # db.add(new_donor)  <-- COMMENTED OUT FOR SANDBOX

                # C. Log the actual Donation transfer with safe IDs
                current_max_id += 1 # Increment our manual counter

                new_donation = models.Donation(
                    donation_id=current_max_id, # Explictly overriding Postgres counter
                    donor_id=don_id,
                    candidate_id=cand_id,
                    amount=amount,
                    date=date.today(), # Stamps it with today's date
                    election_year=2027 # Default to the upcoming cycle
                )
                # db.add(new_donation)  <-- COMMENTED OUT FOR SANDBOX

            # Commit all the new records to PostgreSQL at once!
            # db.commit()  <-- COMMENTED OUT FOR SANDBOX
            
            return {
                "message": "Document successfully processed and sent to isolated sandbox.",
                "filename": file.filename,
                "extracted_data": extracted_data
            }
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="AI failed to return valid JSON.")
            
    except Exception as e:
        # db.rollback() # Protects the database from corruption if something fails <-- COMMENTED OUT
        raise HTTPException(status_code=500, detail=f"File processing error: {str(e)}")