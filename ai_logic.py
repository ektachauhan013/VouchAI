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
    """
    platform = creator.get("platform", "instagram").lower()
    followers = creator.get("followers", 0)
    engagement = creator.get("engagement_rate", 0.0)

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
    Match creators based on brand requirements dictionary structure.
    """
    scored = []

    for creator in all_creators:
        score = 0

        # ===== FILTER: Hard Requirements =====
        if creator.get("platform", "").lower() != brand_requirements.get("platform", "instagram").lower():
            continue

        min_followers = brand_requirements.get("min_followers", 0)
        max_followers = brand_requirements.get("max_followers", 100000000)
        if not (min_followers <= creator.get("followers", 0) <= max_followers):
            continue

        # Check safety scoring limits
        fraud_score = creator.get("fraud_score")
        if fraud_score is None:
            fraud_score = get_fraud_score(creator)

        max_fraud = brand_requirements.get("max_fraud_score", 50)
        if fraud_score > max_fraud:
            continue  # Hard cutoff

        # Niche verification
        brand_niche = brand_requirements.get("niche", "").lower()
        creator_niche = creator.get("niche", "").lower()
        if brand_niche and creator_niche != brand_niche:
            continue  # Hard filter

        # ===== SCORING: Soft Preferences =====
        score += 50  # Niche already matched

        engagement = creator.get("engagement_rate", 0.0)
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
    return scored[:5]


# ==========================================
# 3. SCRIPT GENERATION (GEMINI AI)
# ==========================================

def generate_script(brand_name, product_description, creator, script_type="reel"):
    """
    Generate custom contextual marketing script via Gemini.
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
7. Naturally mention 1-2 concrete visual or audio details

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
# 4. TREND ANALYTICS
# ==========================================

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
    "fashion":  ["#OOTD", "#FashionReel", "#StyleInspo", "#TrendAlert", "#Haul"],
    "fitness":  ["#FitnessMotivation", "#GymReel", "#WorkoutTips", "#FitFam", "#Transformation"],
    "skincare": ["#SkincareRoutine", "#GlowUp", "#SkinTok", "#ProductReview", "#SelfCare"],
    "food":     ["#FoodieReel", "#RecipeOfTheDay", "#HomeCooking", "#Yummy", "#FoodLover"],
    "tech":     ["#TechReview", "#Unboxing", "#GadgetAlert", "#TechTok", "#NewLaunch"],
    "travel":   ["#TravelReel", "#Wanderlust", "#ExploreIndia", "#TravelTips", "#Bucketlist"],
}

_HOOK_STYLES = {
    "comedy":      "Start with a punchline before anyone realizes it's an ad.",
    "calm":        "Open with a soft, honest confession - 'I wasn't expecting this to work, but...'",
    "energetic":   "Open loud and fast - 'Wait, you NEED to see this before you buy anything else.'",
    "educational": "Open with a myth-busting line - 'Everyone gets this wrong about...'",
    "aesthetic":   "Open with a slow visual pan and a soft voiceover before any words appear.",
}


def _detect_mood_from_script(script_text):
    text = script_text.lower()
    scores = {mood: 0 for mood in _MOOD_KEYWORDS}

    for mood, keywords in _MOOD_KEYWORDS.items():
        for kw in keywords:
            scores[mood] += len(re.findall(r"\b" + re.escape(kw) + r"\b", text))

    best_mood = max(scores, key=scores.get)
    if scores[best_mood] == 0:
        best_mood = "educational"
    return best_mood


def get_trend_analytics(script_text, creator):
    if not script_text or creator is None:
        return None

    niche = creator.get("niche", "lifestyle").lower()
    mood = _detect_mood_from_script(script_text)
    audio = _MOOD_AUDIO.get(mood, "Trending Mix Vol.1")
    hashtags = _NICHE_HASHTAG_POOL.get(niche, ["#Trending", "#Reel", "#MustWatch"])[:5]
    hook_line = _HOOK_STYLES.get(mood, _HOOK_STYLES["educational"])

    return {
        "creator_name": creator.get("name"),
        "detected_mood": mood,
        "recommended_audio": audio,
        "hashtag_cloud": hashtags,
        "optimal_hook": hook_line,
    }


# ==========================================
# 5. INTEGRATED FULL PIPELINE EXECUTOR
# ==========================================

def run_campaign_pipeline(brand_requirements, brand_name, product_description, all_creators, script_type="reel"):
    """
    Executes filtering logic, triggers AI generation engines, and structures analytic data models.
    """
    top_matches = match_creators(brand_requirements, all_creators)

    if not top_matches:
        return {
            "matched": False,
            "creator": None,
            "all_matches": [],
            "script": None,
            "trends": None,
            "message": "No suitable creator found for these requirements. Widen filter scopes."
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