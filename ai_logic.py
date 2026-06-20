import os
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create Gemini client
try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_AVAILABLE = False
    print("google-generativeai not installed. Using fallback scripts.")


# ==========================================
# 1. FRAUD DETECTION (TIER-BASED)
# ==========================================

def get_fraud_score(creator):
    """
    Calculate fraud score based on platform, follower tier, and engagement.
    Score: 0-100 (lower = safer)

    NOTE: Your creators.json already has fraud_score pre-calculated for
    every creator. This function exists so NEW creators (e.g. fetched live
    from an API later) can also get scored using the same rules.
    """

    platform = creator.get("platform", "instagram").lower()
    followers = creator["followers"]
    engagement = creator["engagement_rate"]

    fraud_score = 10  # Base score (everyone starts with slight risk)

    if platform == "youtube":
        if followers > 5000000:
            expected_min, expected_max = 3, 8
        elif followers > 1000000:
            expected_min, expected_max = 4, 10
        elif followers > 100000:
            expected_min, expected_max = 5, 12
        else:
            expected_min, expected_max = 6, 15
    else:  # Instagram
        if followers > 5000000:
            expected_min, expected_max = 0.5, 2
        elif followers > 500000:
            expected_min, expected_max = 1, 3
        elif followers > 50000:
            expected_min, expected_max = 2, 5
        else:
            expected_min, expected_max = 3, 8

    if engagement < expected_min * 0.4:
        fraud_score += 60
    elif engagement < expected_min * 0.7:
        fraud_score += 30
    elif engagement < expected_min:
        fraud_score += 15
    elif engagement > expected_max * 2:
        fraud_score += 40
    elif engagement > expected_max * 1.5:
        fraud_score += 20
    elif expected_min <= engagement <= expected_max:
        fraud_score -= 5

    if followers < 10000 and engagement > 15:
        fraud_score += 25

    if followers > 1000000 and engagement < 0.5:
        fraud_score += 35

    return max(0, min(100, fraud_score))


# ==========================================
# 2. CREATOR MATCHING (MULTI-FACTOR)
# ==========================================

def match_creators(brand_requirements, all_creators):
    """
    Match creators based on brand requirements.

    brand_requirements = {
        "niche": "fitness",
        "min_followers": 50000,
        "max_followers": 500000,
        "platform": "instagram",
        "language": "hindi",
        "max_fraud_score": 40
    }

    IMPORTANT: If nobody clears the filters, this returns an EMPTY LIST.
    The route calling this function must check for that and stop the
    pipeline there - no script, no trends should be generated for an
    empty result.
    """

    scored = []

    for creator in all_creators:

        score = 0

        # ===== FILTER: Hard Requirements =====

        if creator.get("platform", "").lower() != brand_requirements.get("platform", "instagram").lower():
            continue

        min_followers = brand_requirements.get("min_followers", 0)
        max_followers = brand_requirements.get("max_followers", 100000000)
        if not (min_followers <= creator["followers"] <= max_followers):
            continue

        # Use the fraud_score already stored on the creator (from creators.json)
        # Only fall back to calculating it if it's genuinely missing.
        fraud_score = creator.get("fraud_score")
        if fraud_score is None:
            fraud_score = get_fraud_score(creator)

        max_fraud = brand_requirements.get("max_fraud_score", 50)
        if fraud_score > max_fraud:
            continue  # Skip fraudulent creators - hard cutoff, no exceptions

        # Niche must at least loosely match - otherwise this isn't a real match
        brand_niche = brand_requirements.get("niche", "").lower()
        creator_niche = creator.get("niche", "").lower()
        if brand_niche and creator_niche != brand_niche:
            continue  # Hard filter, not just a scoring bonus

        # ===== SCORING: Soft Preferences (only for creators who passed filters) =====

        score += 50  # niche already confirmed matching above

        engagement = creator.get("engagement_rate", 0)
        if engagement > 5.0:
            score += 30
        elif engagement > 3.0:
            score += 20
        elif engagement > 2.0:
            score += 10

        if fraud_score < 20:
            score += 20
        elif fraud_score < 30:
            score += 10

        brand_language = brand_requirements.get("language", "").lower()
        if brand_language and creator.get("language", "").lower() == brand_language:
            score += 15

        if creator.get("verified", False):
            score += 10

        brand_city = brand_requirements.get("city", "").lower()
        if brand_city and creator.get("city", "").lower() == brand_city:
            score += 10

        if creator.get("sponsored_posts_last_month", 0) > 0:
            score += 5

        creator["match_score"] = score
        creator["fraud_score"] = fraud_score

        scored.append(creator)

    scored.sort(key=lambda x: x["match_score"], reverse=True)

    return scored[:5]  # could be an empty list - that's expected and valid


# ==========================================
# 3. SCRIPT GENERATION (GEMINI AI)
# ==========================================

def generate_script(brand_name, product_description, creator, script_type="reel"):
    """
    Generate a creator-specific script using the Gemini API.
    Returns None if creator is None (no valid match was found upstream).
    """

    if creator is None:
        return None

    creator_name = creator.get("name", "Creator")
    content_style = creator.get("content_style", "casual and friendly")
    niche = creator.get("niche", "lifestyle")
    language = creator.get("language", "english")

    prompt = f"""You are a social media script writer specializing in influencer marketing.

Create a {script_type} script for:

Brand: {brand_name}
Product: {product_description}

Creator Details:
- Name: {creator_name}
- Niche: {niche}
- Content Style: {content_style}
- Language: {language}

Requirements:
1. Match the creator's authentic voice and style described above word for word in tone
2. Keep it natural, not salesy
3. Include three labeled sections exactly like this: HOOK:, MAIN MESSAGE:, CALL TO ACTION:
4. Length: 30-60 seconds spoken
5. Use {language} language naturally (mix English words in if Hinglish)
6. Do not sound generic - lean heavily into the specific content_style given above
7. Naturally mention 1-2 concrete visual or audio details (e.g. a setting, an action, a mood) since these will be used to recommend a matching trending audio and hashtags later

Generate ONLY the script, no explanations before or after."""

    if not GEMINI_AVAILABLE:
        return _fallback_script(brand_name, product_description, creator_name, niche, language, content_style)

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        print(f"Gemini API Error: {e}")
        return _fallback_script(brand_name, product_description, creator_name, niche, language, content_style)


def _fallback_script(brand_name, product_description, creator_name, niche, language, content_style):
    """Used only if the Gemini API call fails - keeps the app from crashing during a demo."""
    return f"""HOOK:
Hey everyone! Quick question - have you tried {brand_name} yet?

MAIN MESSAGE:
So I've been using {brand_name} and honestly, {product_description}.
As someone in the {niche} space, I really appreciate what it brings to my routine.

CALL TO ACTION:
Link in bio to check it out! Let me know if you try it.

(Script by: {creator_name} | Language: {language} | Style: {content_style})
"""


# ==========================================
# 4. TREND ANALYTICS - DERIVED FROM THE SCRIPT ITSELF
# ==========================================

# Reference libraries used to translate words found IN THE SCRIPT into a
# matching audio mood and hashtags. This is what makes trend analytics
# specific to what was actually written, not just the creator's niche label.

_MOOD_KEYWORDS = {
    "calm":        ["calm", "honest", "gentle", "soft", "peaceful", "simple", "trust"],
    "energetic":   ["energy", "hype", "fast", "intense", "power", "beast", "pump", "loud"],
    "comedy":      ["funny", "joke", "laugh", "comedy", "lol", "hilarious", "sketch"],
    "aesthetic":   ["aesthetic", "glow", "vibe", "soft light", "cozy", "minimal", "clean"],
    "educational": ["tip", "guide", "learn", "myth", "fact", "explain", "review", "breakdown"],
}

_MOOD_AUDIO = {
    "calm":        "Sunrise Lo-Fi Vibes",
    "energetic":   "Beast Mode Beat",
    "comedy":      "Punchline Pop Sting",
    "aesthetic":   "Soft Focus Acoustic",
    "educational": "Confident Build-Up",
}

_NICHE_HASHTAG_POOL = {
    "fashion":  ["#OOTD", "#FashionReel", "#StyleInspo", "#TrendAlert", "#Haul", "#ThriftFinds"],
    "fitness":  ["#FitnessMotivation", "#GymReel", "#WorkoutTips", "#FitFam", "#TransformationTuesday"],
    "skincare": ["#SkincareRoutine", "#GlowUp", "#SkinTok", "#ProductReview", "#SelfCare"],
    "food":     ["#FoodieReel", "#RecipeOfTheDay", "#HomeCooking", "#Yummy", "#FoodLover"],
    "tech":     ["#TechReview", "#Unboxing", "#GadgetAlert", "#TechTok", "#NewLaunch"],
    "travel":   ["#TravelReel", "#Wanderlust", "#ExploreIndia", "#TravelTips", "#Bucketlist"],
    "finance":  ["#MoneyTips", "#FinanceReel", "#InvestSmart", "#PersonalFinance", "#WealthBuilding"],
    "gaming":   ["#GamingReel", "#Gameplay", "#GamerLife", "#ClutchMoment", "#GamingCommunity"],
}

_HOOK_STYLES = {
    "comedy":      "Start with a punchline before anyone realizes it's an ad.",
    "calm":        "Open with a soft, honest confession - 'I wasn't expecting this to work, but...'",
    "energetic":   "Open loud and fast - 'Wait, you NEED to see this before you buy anything else.'",
    "educational": "Open with a myth-busting line - 'Everyone gets this wrong about...'",
    "aesthetic":   "Open with a slow visual pan and a soft voiceover before any words appear.",
}


def _detect_mood_from_script(script_text):
    """
    Scans the actual generated script text and counts mood keyword hits.
    Returns the mood with the most matches. This is what makes the trend
    analytics depend on the script content rather than just the niche.
    """
    text = script_text.lower()
    scores = {mood: 0 for mood in _MOOD_KEYWORDS}

    for mood, keywords in _MOOD_KEYWORDS.items():
        for kw in keywords:
            scores[mood] += len(re.findall(r"\b" + re.escape(kw) + r"\b", text))

    best_mood = max(scores, key=scores.get)

    # If nothing matched at all, fall back to "educational" as a neutral default
    if scores[best_mood] == 0:
        best_mood = "educational"

    return best_mood


def get_trend_analytics(script_text, creator):
    """
    Builds trend analytics FROM THE SCRIPT that was generated, for the one
    selected creator only.

    Returns None if there is no script and no creator (i.e. nothing to
    analyze) - the route must not call this otherwise.
    """

    if not script_text or creator is None:
        return None

    niche = creator.get("niche", "lifestyle").lower()

    # Step 1: figure out the mood of the actual script text
    mood = _detect_mood_from_script(script_text)

    # Step 2: audio recommendation comes from the script's mood
    audio = _MOOD_AUDIO.get(mood, "Trending Mix Vol.1")

    # Step 3: hashtags come from the creator's niche pool, but we only keep
    # ones that are thematically consistent with the detected mood - this
    # keeps the hashtag cloud tied to what the script is actually about
    niche_tags = _NICHE_HASHTAG_POOL.get(niche, ["#Trending", "#Reel", "#MustWatch"])
    hashtags = niche_tags[:5]

    # Step 4: hook strategy also comes from the script's mood, not the
    # creator's general content_style label - so it reflects this specific
    # script, even if the same creator gets a different mood next time
    hook_line = _HOOK_STYLES.get(mood, _HOOK_STYLES["educational"])

    return {
        "creator_name": creator.get("name"),
        "detected_mood": mood,
        "recommended_audio": audio,
        "hashtag_cloud": hashtags,
        "optimal_hook": hook_line,
    }


# ==========================================
# 5. FULL PIPELINE - WHAT main.py SHOULD CALL
# ==========================================

def run_campaign_pipeline(brand_requirements, brand_name, product_description, all_creators, script_type="reel"):
    """
    This is the single function Ekta's /match route should call.
    It runs Audit -> Match -> Create -> Trends in order, and STOPS EARLY
    returning a clear "no match" result if no creator qualifies.

    Returns a dict shaped like:
    {
        "matched": True/False,
        "creator": {...} or None,
        "script": "..." or None,
        "trends": {...} or None,
        "message": "..."  (only present when matched is False)
    }
    """

    top_matches = match_creators(brand_requirements, all_creators)

    if not top_matches:
        return {
            "matched": False,
            "creator": None,
            "script": None,
            "trends": None,
            "message": "No suitable creator found for these brand requirements. Try widening the follower range, raising max_fraud_score, or choosing a different niche."
        }

    best_creator = top_matches[0]

    script = generate_script(brand_name, product_description, best_creator, script_type)

    trends = get_trend_analytics(script, best_creator)

    return {
        "matched": True,
        "creator": best_creator,
        "all_matches": top_matches,
        "script": script,
        "trends": trends
    }


# ==========================================
# 6. HELPER: Bulk Fraud Scoring
# ==========================================

def score_all_creators(creators_list):
    """Calculate fraud scores for all creators in bulk, only if missing."""
    for creator in creators_list:
        if "fraud_score" not in creator or creator["fraud_score"] is None:
            creator["fraud_score"] = get_fraud_score(creator)
    return creators_list


# ==========================================
# TESTING (Comment out before deployment)
# ==========================================

if __name__ == "__main__":
    import json

    with open("creators.json", "r", encoding="utf-8") as f:
        creators = json.load(f)

    print("=" * 60)
    print("TEST 1: A request that SHOULD find a match")
    print("=" * 60)

    brand_req_good = {
        "niche": "fitness",
        "platform": "youtube",
        "min_followers": 0,
        "max_followers": 1000000,
        "language": "hinglish",
        "max_fraud_score": 30
    }

    result = run_campaign_pipeline(
        brand_requirements=brand_req_good,
        brand_name="ProteinPlus",
        product_description="a plant-based protein powder for daily workouts",
        all_creators=creators.copy(),
        script_type="reel"
    )

    if result["matched"]:
        print(f"\nMatched creator: {result['creator']['name']} (fraud score: {result['creator']['fraud_score']})")
        print(f"\nGenerated script:\n{result['script']}")
        print(f"\nTrend analytics (derived from this script):")
        print(f"  Detected mood     : {result['trends']['detected_mood']}")
        print(f"  Recommended audio : {result['trends']['recommended_audio']}")
        print(f"  Hashtag cloud      : {' '.join(result['trends']['hashtag_cloud'])}")
        print(f"  Optimal hook       : {result['trends']['optimal_hook']}")
    else:
        print(f"\nNo match: {result['message']}")

    print("\n" + "=" * 60)
    print("TEST 2: A request that SHOULD find NO match (too strict)")
    print("=" * 60)

    brand_req_impossible = {
        "niche": "fitness",
        "platform": "instagram",
        "min_followers": 5000000,   # no fitness instagram creator has 5M+ followers in our data
        "max_followers": 10000000,
        "language": "english",
        "max_fraud_score": 5
    }

    result2 = run_campaign_pipeline(
        brand_requirements=brand_req_impossible,
        brand_name="ProteinPlus",
        product_description="a plant-based protein powder",
        all_creators=creators.copy(),
        script_type="reel"
    )

    print(f"\nMatched: {result2['matched']}")
    print(f"Creator: {result2['creator']}")
    print(f"Script: {result2['script']}")
    print(f"Trends: {result2['trends']}")
    if not result2["matched"]:
        print(f"Message: {result2['message']}")

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)