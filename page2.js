// Dynamic Slider Value Real-time Updater
const budgetSlider = document.getElementById('budget-slider');
const budgetDisplay = document.getElementById('budget-display');

if (budgetSlider && budgetDisplay) {
    // Function to set text in the mandatory format: ( min - slider value )
    const updateSliderDisplay = () => {
        budgetDisplay.innerText = `(${budgetSlider.min} - ${budgetSlider.value})`;
    };

    // Listen for drag interactions to update immediately
    budgetSlider.addEventListener('input', updateSliderDisplay);
    // Initialize current default threshold visual layout on page render
    updateSliderDisplay();
}

document.getElementById('analyze').addEventListener('click', async function(e) {
    e.preventDefault();

    const styleElement = document.getElementById('style-select');
    const selectedStyle = styleElement ? styleElement.value : 'educational';
    localStorage.setItem('selectedStyle', selectedStyle);
    
    const languageElement = document.getElementById('language-select');
    const selectedLanguage = languageElement ? languageElement.value.toLowerCase() : 'english';
    
    const selectedBudget = budgetSlider ? parseFloat(budgetSlider.value) : 10000;

    const companyName = localStorage.getItem('companyName') || 'My Brand';
    const corporateNiche = localStorage.getItem('corporateNiche') || 'tech';

    // Construct unified parameters model matching Python Pydantic structures
    const payload = {
        brandName: companyName,
        niche: corporateNiche.toLowerCase(),
        budget: selectedBudget,
        language: selectedLanguage
    };

    const gridContainer = document.getElementById('grid');
    const resultsWorkspace = document.getElementById('results-workspace');
    const instructionHeading = document.getElementById('results-instruction');
    
    if (!gridContainer || !resultsWorkspace) return;

    // Reveal container and show crisp loading state indicators
    resultsWorkspace.style.display = 'block';
    if (instructionHeading) instructionHeading.style.display = 'none';
    gridContainer.innerHTML = '<p style="color: white; padding: 20px; text-align: center; width: 100%;">Auditing live backend profiles and running fraud detection filters...</p>';

    try {
        // Fetching real matching calculations from FastAPI on Port 8000
        const response = await fetch('http://127.0.0.1:8000/match', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!data.success || !data.creators || data.creators.length === 0) {
            if (instructionHeading) instructionHeading.style.display = 'none';
            gridContainer.innerHTML = '<p style="color: #ff4a4a; padding: 20px; text-align: center; width: 100%;">No creator profiles in database match these thresholds.</p>';
            return;
        }

        // Clean out workspace and display clear interactive message instructions
        gridContainer.innerHTML = '';
        if (instructionHeading) {
            instructionHeading.style.display = 'block';
            instructionHeading.innerText = "✨ AI Audit Complete! Click any creator below to build their custom script profile.";
        }

        // Mapping true backend parameters data sets inside dynamic nodes
        data.creators.forEach(creator => {
            let statusClass = 'badge-green';
            let statusText = 'Clear';
            const fraudScore = creator.fraud_score || 0;

            if (fraudScore > 30 && fraudScore <= 60) {
                statusClass = 'badge-yellow';
                statusText = 'Caution';
            } else if (fraudScore > 60) {
                statusClass = 'badge-red';
                statusText = 'Blocked';
            }

            const card = document.createElement('div');
            card.className = 'card real-data-card';
            
            card.innerHTML = `
                <h3>${creator.name}</h3>
                <p>Platform: ${creator.platform || 'Instagram'}</p>
                <p>Fraud Score: ${fraudScore}</p>
                <p>Fit Match Score: ${creator.campaign_fit_score || '90'}/100</p>
                <span class="badge ${statusClass}">${statusText}</span>
            `;

            // EVENT PASSING ROUTE: Send properties cleanly into browser runtime allocations
            card.addEventListener('click', () => {
                localStorage.setItem('selectedCreatorName', creator.name);
                localStorage.setItem('selectedCreatorStyle', creator.content_style || selectedStyle);
                localStorage.setItem('selectedCreatorNiche', creator.niche || corporateNiche);
                localStorage.setItem('globalScriptOutput', data.script);
                localStorage.setItem('globalTrendsOutput', JSON.stringify(data.trends));

                window.location.href = 'dashboard.html';
            });

            gridContainer.appendChild(card);
        });

    } catch (err) {
        console.error(err);
        if (instructionHeading) instructionHeading.style.display = 'none';
        gridContainer.innerHTML = '<p style="color: #ff4a4a; padding: 20px; text-align: center; width: 100%;">Failed to fetch. Confirm Uvicorn backend server is running on port 8000.</p>';
    }
});