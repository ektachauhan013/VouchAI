// Function 1: submitForm() runs when the user clicks 'Find Creators' on index.html
function submitForm() {
    // Reading user choices via specified element IDs
    var brandName = document.getElementById('brandName').value.trim();
    var niche = document.getElementById('niche').value;
    var budget = document.getElementById('budget').value.trim();
    var language = document.getElementById('language').value;

    // Check if any form fields are blank before saving
    if (brandName === "" || niche === "" || budget === "" || language === "") {
        alert("Please completely fill out all fields before hitting submit!");
        return;
    }

    // Pack values into an object structure and commit to browser cache storage
    var dataPayload = {
        brandName: brandName,
        niche: niche,
        budget: budget,
        language: language
    };

    localStorage.setItem('brandData', JSON.stringify(dataPayload));

    // Change window routing views over to the results display page
    window.location.href = 'results.html';
}

// Function 2: loadResults() running asynchronously automatically on results.html load execution loops
async function loadResults() {
    // Unpack data variables cache string stored from our index form screen
    var rawCache = localStorage.getItem('brandData');
    
    if (!rawCache) {
        document.getElementById('creatorsContainer').innerHTML = 
            "<p class='fraud-score-high'>Validation Exception: Search dataset criteria missing from cache memory streams.</p>";
        return;
    }

    var brandData = JSON.parse(rawCache);

    try {
        // Send a POST network transaction query containing our data packet out to Ekta's FastAPI server
        var response = await fetch('http://localhost:8000/match', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json' 
            },
            body: JSON.stringify(brandData)
        });

        if (!response.ok) {
            throw new Error("HTTP connection error status code returned.");
        }

        // Convert the returned raw network body response stream over into JSON 
        var data = await response.json();

        var container = document.getElementById('creatorsContainer');
        var scriptBox = document.getElementById('campaignScript');

        // Clear out placeholder loading text elements
        container.innerHTML = "";

        // Loop through creator elements array objects returned from backend queries
        data.creators.forEach(function(creator) {
            var fraudClass = "";

            // Evaluate conditional styles flags depending on score thresholds
            if (creator.fraud_score > 50) {
                fraudClass = "fraud-score-high";
            } else if (creator.fraud_score < 20) {
                fraudClass = "fraud-score-low";
            } else {
                fraudClass = "fraud-score-mid";
            }

            // Build structural templates containing server variables parameters smoothly
            var cardHTML = `
                <div class="creator-card">
                    <div>
                        <div class="flex items-center justify-between mb-4">
                            <h4 class="text-lg font-bold text-slate-800">${creator.name}</h4>
                            <span class="text-xs font-semibold px-2.5 py-1 bg-indigo-50 text-indigo-600 rounded-full capitalize">${creator.niche}</span>
                        </div>
                        <div class="space-y-2 text-sm text-slate-600">
                            <p><span class="font-medium text-slate-500">Followers:</span> ${creator.followers.toLocaleString()}</p>
                            <p><span class="font-medium text-slate-500">Engagement Rate:</span> ${creator.engagement_rate}%</p>
                        </div>
                    </div>
                    <div class="mt-5 pt-4 border-t border-slate-100 flex justify-between items-center text-sm">
                        <span class="text-slate-400 font-medium">Fraud Rating:</span>
                        <span class="${fraudClass}">${creator.fraud_score}/100</span>
                    </div>
                </div>
            `;
            container.innerHTML += cardHTML;
        });

        // Set the text output content safely inside script elements box wrapper
        scriptBox.innerText = data.script;

    } catch (error) {
        console.error("Fetch API error trace logging context:", error);
        document.getElementById('creatorsContainer').innerHTML = 
            "<p class='fraud-score-high text-center col-span-3'>AJAX Request Interrupted: Could not connect to the FastAPI server. Ensure main.py is running on port 8000.</p>";
    }
}