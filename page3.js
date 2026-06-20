window.addEventListener('DOMContentLoaded', () => {
    const selectedCreatorName = localStorage.getItem('selectedCreatorName');
    const globalScript = localStorage.getItem('globalScriptOutput');
    const rawTrends = localStorage.getItem('globalTrendsOutput');

    // System bounding checkpoint to lock secure flow operations
    if (!selectedCreatorName || !globalScript) {
        alert('Please pick a specific matching creator profile from the pipeline dashboard first.');
        window.location.href = 'campaign.html';
        return;
    }

    const trendData = rawTrends ? JSON.parse(rawTrends) : null;

    // Inject dynamic heading naming details mapping chosen candidate profile metrics
    const titleHeader = document.getElementById('script-title');
    if (titleHeader) {
        titleHeader.innerText = `Custom Script for ${selectedCreatorName}`;
    }

    const voiceoverContainer = document.getElementById('voiceover');
    const cueContainer = document.getElementById('cue');

    if (voiceoverContainer) {
        voiceoverContainer.innerText = globalScript;
    }
    
    if (cueContainer) {
        const creatorStyleText = localStorage.getItem('selectedCreatorStyle') || 'natural delivery style';
        cueContainer.innerText = `Visual & Pacing Cue: Delivery matches "${creatorStyleText}" creative formatting guidelines closely.`;
    }

    // Injects matching trend parameters telemetry tracking points returned via FastAPI python pipelines
    if (trendData) {
        const audioBox = document.getElementById('audio');
        if (audioBox) {
            audioBox.innerText = `${trendData.recommended_audio || 'Trending Audio Track - Generic Mix'}`;
        }

        const hookBox = document.getElementById('hook');
        if (hookBox) {
            hookBox.innerText = `"${trendData.optimal_hook || 'Hook: Pay attention to this core insight statement before starting!'}"`;
        }

        const tagCloud = document.getElementById('hashtags');
        if (tagCloud) {
            tagCloud.innerHTML = ''; 
            const tagsList = trendData.hashtag_cloud || ['#Trending', '#InfluencerMarketing'];
            
            tagsList.forEach(tag => {
                const span = document.createElement('span');
                span.className = 'tag';
                span.innerText = tag.startsWith('#') ? tag : `#${tag}`;
                tagCloud.appendChild(span);
            });
        }
    }
});

const toggles = document.querySelectorAll('.toggle');
toggles.forEach(toggle => {
    toggle.addEventListener('click', function() {
        toggles.forEach(t => t.classList.remove('active'));
        this.classList.add('active');
    });
});