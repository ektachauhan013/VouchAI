from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
from ai_logic import get_fraud_score, match_creators, generate_script


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    
    allow_credentials=True,
    allow_methods=["*"],    
    allow_headers=["*"],    
)


class BrandInput(BaseModel):
    brandName: str
    niche: str
    budget: float
    language: str


SPONSORSHIP_SATURATION_LIMIT = 10  

def calculate_campaign_score(creator):
    """
    Custom scoring algorithm to rank influencers for a brand MVP.
    Balances engagement efficiency with fraud score metrics and ad saturation.
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

# 5. Core Server matching pipeline route
@app.post("/match")
def match(brand: BrandInput):
    """
    Main API endpoint. Receives brand payload, loads database entries,
    processes anomaly verification, and yields top matches along with AI copy.
    """
    
    filepath = "creators.json"
    if not os.path.exists(filepath):
        return {"error": f"Database file '{filepath}' not found on server."}
        
    with open(filepath, "r", encoding="utf-8") as f:
        all_creators = json.load(f)
    
    
    for creator in all_creators:
        creator["fraud_score"] = get_fraud_score(creator)
        
    
    top3 = match_creators(brand.niche, all_creators)
    
   
    for creator in top3:
        creator["campaign_fit_score"] = calculate_campaign_score(creator)
    
    
    top3.sort(key=lambda x: x.get("campaign_fit_score", 0), reverse=True)
    
   
    if not top3:
        return {"creators": [], "script": "No creators matching this niche were found."}
        
    
    script = generate_script(brand.brandName, top3[0]["name"], brand.language)
    

    return {
        "creators": top3,
        "script": script
    }