from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
from ai_logic import get_fraud_score, run_campaign_pipeline

app = FastAPI()

# Configure Application Level CORS for Frontend decoupling
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    
    allow_credentials=True,
    allow_methods=["*"],    
    allow_headers=["*"],    
)

# Pydantic schema mirroring validation inputs from User Forms
class BrandInput(BaseModel):
    brandName: str
    niche: str
    budget: float
    language: str

SPONSORSHIP_SATURATION_LIMIT = 10  

def calculate_campaign_score(creator):
    """
    Calculates operational deployment fitness ratings.
    """
    engagement = creator.get("engagement_rate", 0.0)
    fraud_score = creator.get("fraud_score", 0)
    sponsored_posts = creator.get("sponsored_posts_last_month", 0)
    
    base_score = engagement * 10
    fraud_penalty = (fraud_score / 100) * 20
    
    saturation_penalty = 0
    if sponsored_posts > SPONSORSHIP_SATURATION_LIMIT:
        saturation_penalty = (sponsored_posts - SPONSORSHIP_SATURATION_LIMIT) * 1.5
        
    final_score = max(0, base_score - fraud_penalty - saturation_penalty)
    return round(final_score, 2)


@app.post("/match")
def match(brand: BrandInput):
    """
    Main API operational handler. Connects front-end telemetry to the backend scoring pipeline.
    """
    filepath = "creators.json"
    if not os.path.exists(filepath):
        return {"error": f"Database file '{filepath}' not found on server."}
        
    with open(filepath, "r", encoding="utf-8") as f:
        all_creators = json.load(f)
    
    # 1. Backfill fraud indices for matching verification loops
    for creator in all_creators:
        creator["fraud_score"] = get_fraud_score(creator)
        
    # 2. Re-map inbound values into system pipeline definitions
    brand_requirements = {
        "niche": brand.niche.strip().lower(),
        "platform": "instagram",  # Default baseline target anchor
        "min_followers": 0,
        "max_followers": 100000000,
        "language": brand.language.strip().lower(),
        "max_fraud_score": 100   # Max scope threshold (Filter logic handles pruning)
    }
    
    # 3. Call the fully centralized multi-factor generation pipeline
    pipeline_result = run_campaign_pipeline(
        brand_requirements=brand_requirements,
        brand_name=brand.brandName,
        product_description=f"Premium scaling optimization tailored within the targeted {brand.niche} domain space.",
        all_creators=all_creators,
        script_type="reel"
    )
    
    # 4. Handle negative returns elegantly
    if not pipeline_result["matched"]:
        return {
            "success": False,
            "creators": [],
            "script": "No creators matching this niche configuration were successfully isolated.",
            "trends": None
        }
    
    # 5. Extract top-tier recommendations and map customization fits
    top_matches = pipeline_result["all_matches"][:3] # Pull top 3 candidates
    for creator in top_matches:
        creator["campaign_fit_score"] = calculate_campaign_score(creator)
        
    # Re-sort match lists based on specialized core fit formulas
    top_matches.sort(key=lambda x: x.get("campaign_fit_score", 0), reverse=True)
    
    # 6. Dispatch operational payload structures to front-end page engines
    return {
        "success": True,
        "creators": top_matches,
        "script": pipeline_result["script"],
        "trends": pipeline_result["trends"] # Sending over real audio metrics, tags and hooks!
    }