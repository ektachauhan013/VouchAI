# VouchAI ✦ AI-Powered Influencer Auditing & Campaign Strategy Engine



VouchAI is an advanced, full-stack marketing intelligence web application built to streamline brand-influencer collaborations. The platform leverages artificial intelligence to screen content creators for fraud metrics, assess target audience brand alignment dynamically, and instantly generate highly contextual viral video script frameworks matched alongside real-time trend analytics extraction algorithms.



---



## 🔄 Core Platform Workflow



1. **Identity Portal:** Brands authenticate their profiles and choose their distinct corporate market sector vertical (Tech, Fitness, Skincare, Fashion, Food, Travel).

2. **Dynamic Campaign Filtering:** Users pass distinct parameter constraints including overall budget limits, targeting languages, and location scopes.

3. **Automated Fraud Screening Audit:** The application processes backend records directly from a dataset to identify anomaly distribution patterns, flag deceptive engagement profiles, and calculate dynamic safety tiers (*Clear*, *Caution*, *Blocked*).

4. **Tailored Script & Trends Workbench:** Selecting an authorized candidate locks in your profile criteria. The backend routes details through the Gemini AI API engine to return an optimized video script alongside matching trend recommendations (hashtags, visual hooks, audio tracks).



---



## 🛠️ Technology Stack



### Frontend Architecture

* **Markup & Structure:** HTML5 (Semantic Structure)

* **Design & Experience System:** CSS3 (Premium Ultra-Dark Neo-SaaS theme with translucent components and smartphone preview framing viewport simulators)

* **Client Pacing Logic:** Modern Asynchronous JavaScript (ES6+ `Fetch API`, `Local Storage`, `DOM Mutation Handlers`)



### Backend Architecture

* **Core Application Server Framework:** FastAPI (High Performance, Asynchronous Python Gateway Web Framework)

* **Machine Intelligence Core Engine:**  Google Gemini 1.5 Flash API (Optimized, High-Speed multimodal LLM pipeline)

* **Environment Configuration Protections:** Python Dotenv & Pydantic Validation Schemas

* **Database Layer Mockup:** Native Static JSON (`creators.json`)



---



## 📂 Project Architecture Tree



```text

├── backend/

│   ├── main.py              # FastAPI core server, endpoints mapping & lifecycle hooks

│   ├── ai_logic.py          # Gemini API integrations & text parameter parsing engines

│   ├── creators.json        # Influencer records containing raw performance metrics

│   ├── .env                 # Private configuration variables (Excluded from git tracking)

│   └── .gitignore           # File tracking parameters configuration settings

│

└── frontend/

    ├── index.html           # Brand onboarding credentials screen interface

    ├── campaign.html        # Dynamic filters configuration & evaluation space

    ├── dashboard.html       # Automated workspace layout script dashboard prompter

    ├── page1.js             # Identity handling validations script code

    ├── page2.js             # Server API pipelines orchestration wrapper code

    ├── page3.js             # Telemetry presentation interface rendering controller

    └── style.css            # Unified production-grade dark design layout styles