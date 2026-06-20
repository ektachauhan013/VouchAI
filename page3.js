const creators = [
    { name: "Aarav Sharma", score: 12, platform: "YouTube" },
    { name: "Diya Patel", score: 25, platform: "Instagram" },
    { name: "Kabir Singh", score: 45, platform: "Instagram" },
    { name: "Riya Verma", score: 75, platform: "YouTube" },
    { name: "Ananya Das", score: 18, platform: "Instagram" }
];

const stylesData = {
    educational: {
        cue: "Camera macro focus on formulation elements.",
        voiceover: "Let us break down exactly what ingredients go into this build.",
        audio: "Trending Audio: TechSynth Pro (Used in 85k videos)",
        tags: ["#FormulationCheck", "#DeepDive", "#TechSpecs", "#Unboxing", "#HowTo"],
        hook: "Don't buy a laptop in 2026 until you see this..."
    },
    lifestyle: {
        cue: "Wide tracking angle during morning routine walkthrough.",
        voiceover: "Spending the morning reorganizing my workspace structure.",
        audio: "Trending Audio: Sunrise Lo-Fi Vibes (Used in 210k videos)",
        tags: ["#VlogLife", "#DailyRoutine", "#AestheticVlog", "#Haul", "#Lifestyle"],
        hook: "This single habit altered how I plan my entire day."
    },
    aesthetic: {
        cue: "Tight static shot with sharp ASMR sound feedback.",
        voiceover: "The textural feedback of this structural layout is unmatched.",
        audio: "Trending Audio: Nexaverse Beats (Used in 140k reels this week)",
        tags: ["#CleanBeauty", "#GlowUp", "#SkincareRoutine", "#MinimalStyle", "#ASMR"],
        hook: "Stop applying eyeliner in this way and ruining your whole eyemakeup (Visual hook: Applying eyeliner and eyeshadow for complete look)."
    }
};

window.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('grid');
    const selectedStyle = localStorage.getItem('selectedStyle') || 'educational';
    
    creators.forEach(creator => {
        let statusClass = 'badge-green';
        let statusText = 'Clear';
        
        if (creator.score > 30 && creator.score <= 60) {
            statusClass = 'badge-yellow';
            statusText = 'Caution';
        } else if (creator.score > 60) {
            statusClass = 'badge-red';
            statusText = 'Blocked';
        }

        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
            <h3>${creator.name}</h3>
            <p>Platform: ${creator.platform}</p>
            <p>Fraud Score: ${creator.score}</p>
            <span class="badge ${statusClass}">${statusText}</span>
        `;
        
        card.addEventListener('click', () => {
            document.getElementById('voiceover').innerText = `[${creator.name}] ${stylesData[selectedStyle].voiceover}`;
        });
        grid.appendChild(card);
    });

    // Populate trend metrics
    const data = stylesData[selectedStyle];
    document.getElementById('cue').innerText = data.cue;
    document.getElementById('voiceover').innerText = data.voiceover;
    document.getElementById('audio').innerText = data.audio;
    document.getElementById('hook').innerText = data.hook;
    
    const tagCloud = document.getElementById('hashtags');
    data.tags.forEach(tag => {
        const span = document.createElement('span');
        span.className = 'tag';
        span.innerText = tag;
        tagCloud.appendChild(span);
    });
});

const toggles = document.querySelectorAll('.toggle');
toggles.forEach(toggle => {
    toggle.addEventListener('click', function() {
        toggles.forEach(t => t.classList.remove('active'));
        this.classList.add('active');
    });
});