import os
import anthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create Claude client
client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)



def get_fraud_score(creator):

    followers = creator["followers"]
    engagement = creator["engagement_rate"]

    fraud_score = 0

    # Rule 1: Low engagement is suspicious
    if engagement < 1.0:
        fraud_score += 50

    elif engagement < 2.0:
        fraud_score += 25

    elif engagement > 4.0:
        fraud_score -= 10

    # Rule 2: Huge followers + low engagement
    if followers > 1000000 and engagement < 1.5:
        fraud_score += 30

    # Rule 3: Small creators with good engagement
    if followers < 100000 and engagement > 3.0:
        fraud_score -= 20

    # Keep score between 0 and 100
    fraud_score = max(0, min(100, fraud_score))

    return fraud_score



def match_creators(brand_niche, all_creators):

    scored = []

    for creator in all_creators:

        score = 0

        # Niche Match
        if creator["niche"].lower() == brand_niche.lower():
            score += 50

        # Engagement Score
        if creator["engagement_rate"] > 3.0:
            score += 30

        elif creator["engagement_rate"] > 2.0:
            score += 15

        # Authenticity Score
        fraud = creator.get("fraud_score", 50)

        if fraud < 30:
            score += 20

        elif fraud > 60:
            score -= 20

        creator["match_score"] = score

        scored.append(creator)

    # Sort creators by match score
    scored.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )

    # Return top 3 creators
    return scored[:3]




def generate_script(
        brand_name,
        creator_name,
        language):

    """
    Mock script generator.

    Replace this with Claude API call when
    API credits are available.
    """

    script = f"""
HOOK:

Hey guys! I recently discovered {brand_name}
and honestly it's amazing!

MAIN MESSAGE:

Hi, I'm {creator_name}.

I've been using {brand_name}
and wanted to share it with you all.

The experience has been simple,
convenient and worth trying.

CALL TO ACTION:

Go check out {brand_name}
and let me know what you think!

Language: {language}
"""

    return script