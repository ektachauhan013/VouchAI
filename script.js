// Function 1: Packages raw state fields and paths seamlessly across HTML windows
function submitForm() {
    const brandName = document.getElementById('brandname').value.trim();
    const niche = document.getElementById('niche').value;
    const budget = document.getElementById('budget').value.trim();
    const language = document.getElementById('language').value;

    // Direct validation preventing empty submissions
    if (!brandName || !niche || !budget || !language) {
        alert("Please fill out all fields before matching creators.");
        return;
    }

    // Encoding form data into safe browser URL parameter strings to avoid local tracking block errors
    const queryParams = new URLSearchParams({
        brand: brandName,
        niche: niche,
        budget: budget,
        lang: language
    });

    // Navigate to results page passing arguments cleanly via URL bar
    window.location.href = 'result.html?' + queryParams.toString();
}

// Function 2: Decodes runtime string inputs and parses response content logic
function loadResults() {
    // Read string parameters directly from the browser's URL location bar 
    const urlParams = new URLSearchParams(window.location.search);
    
    const brandName = urlParams.get('brand');
    const niche = urlParams.get('niche');
    const budget = urlParams.get('budget');
    const language = urlParams.get('lang');

    // Structural recovery if data link was disconnected
    if (!brandName || !niche || !budget || !language) {
        document.getElementById('creatorsContainer').innerHTML = `
            <p class="fraud-score-high" style="text-align: center; grid-column: span 3; width: 100%;">
                Error: Missing search criteria. Please return to the homepage and fill out the form.
            </p>`;
        return;
    }

    const requestPayload = { brandName, niche, budget, language };

    // Standard live web fetch execution loop
    fetch('https://jsonplaceholder.typicode.com/posts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestPayload)
    })
    .then(response => {
        // Intercepts structural network promises and processes mock schema instantly
        return getMockCreatorsResponse(brandName, niche, language);
    })
    .then(data => {
        const container = document.getElementById('creatorsContainer');
        const scriptBox = document.getElementById('campaignScript');
        
        container.innerHTML = ''; // Expel loaders
        
        data.creators.forEach(creator => {
            let fraudClass = ''; 
            if (creator.fraudScore > 50) {
                fraudClass = 'fraud-score-high';
            } else if (creator.fraudScore < 20) {
                fraudClass = 'fraud-score-low';
            } else {
                fraudClass = 'fraud-score-mid';
            }

            const cardHTML = `
                <div class="creator-card">
                    <div>
                        <div class="card-header">
                            <h4 class="creator-name">${creator.name}</h4>
                            <span class="creator-badge">${creator.niche}</span>
                        </div>
                        <div class="card-metrics">
                            <p class="metric-row"><span class="metric-label">Followers:</span> ${creator.followers}</p>
                            <p class="metric-row"><span class="metric-label">Engagement:</span> ${creator.engagementRate}</p>
                        </div>
                    </div>
                    <div class="card-footer">
                        <span class="footer-label">Audience Fraud Score:</span>
                        <span class="${fraudClass}">${creator.fraudScore}%</span>
                    </div>
                </div>
            `;
            container.innerHTML += cardHTML;
        });

        scriptBox.innerHTML = data.campaignScript;
    })
    .catch(err => {
        console.error("Networking Engine Interruption Exception:", err);
        document.getElementById('creatorsContainer').innerHTML = `
            <p class="fraud-score-high" style="text-align: center; grid-column: span 3; width: 100%;">
                Data ingestion failure. Check connection settings.
            </p>`;
    });
}

// Generates local mock context datasets mirroring live remote responses
function getMockCreatorsResponse(brand, niche, language) {
    return {
        creators: [
            { name: "Aanya Sharma", niche: niche, followers: "450K", engagementRate: "4.8%", fraudScore: 12 },
            { name: "Kabir Malhotra", niche: niche, followers: "1.2M", engagementRate: "3.2%", fraudScore: 54 },
            { name: "Rohan Verma", niche: niche, followers: "88K", engagementRate: "7.1%", fraudScore: 28 }
        ],
        campaignScript: `[Hook: Visual starts tracking closely onto dynamic user macro-shot]\n\n"Honestly, I am very picky about what matches my lifestyle. But since ${brand} dropped their latest line, things changed. For everyone watching who speaks ${language}, you absolute need this. No fluff, just pure results. Check out my exclusive bio link to grab yours now!"`
    };
}