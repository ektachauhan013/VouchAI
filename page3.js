window.addEventListener('DOMContentLoaded', () => {
    console.log("🚀 page3.js successfully loaded!");

    // Grabbing data with safe fallback defaults so the script NEVER crashes
    const selectedCreatorName = localStorage.getItem('selectedCreatorName') || 'Dewy Diaries';
    const globalScript = localStorage.getItem('globalScriptOutput') || 'No script text found in storage.';
    const rawTrends = localStorage.getItem('globalTrendsOutput');

    const trendData = rawTrends ? JSON.parse(rawTrends) : null;

    // Inject dynamic heading naming details
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

    // Injects matching trend parameters
    if (trendData) {
        const audioBox = document.getElementById('audio');
        if (audioBox) {
            audioBox.innerText = `${trendData.recommended_audio || 'Confident Build-Up'}`;
        }

        const hookBox = document.getElementById('hook');
        if (hookBox) {
            hookBox.innerText = `"${trendData.optimal_hook || 'Open with a myth-busting line...'}"`;
        }

        const tagCloud = document.getElementById('hashtags');
        if (tagCloud) {
            tagCloud.innerHTML = ''; 
            const tagsList = trendData.hashtag_cloud || ['#SkincareRoutine', '#GlowUp', '#SkinTok', '#ProductReview', '#SelfCare'];
            
            tagsList.forEach(tag => {
                const span = document.createElement('span');
                span.className = 'tag';
                span.innerText = tag.startsWith('#') ? tag : `#${tag}`;
                tagCloud.appendChild(span);
            });
        }
    }

    // COMPREHENSIVE PDF GENERATION EVENT LISTENER
    const downloadBtn = document.getElementById('download-script-btn');
    if (downloadBtn) {
        console.log("📥 Download button found in DOM and event listener attached!");
        
        downloadBtn.addEventListener('click', (e) => {
            e.preventDefault(); // Prevents any default form actions from blocking us
            console.log("⚡ Download button clicked! Compiling PDF...");

            try {
                // Check if jsPDF library loaded correctly from the CDN
                if (!window.jspdf) {
                    alert("❌ jsPDF library failed to load from the internet. Please check your connection or link tag.");
                    return;
                }

                const { jsPDF } = window.jspdf;
                const doc = new jsPDF('p', 'mm', 'a4');

                // Fallback safe extraction values
                const activeToneElement = document.querySelector('.toggle.active');
                const scriptTone = activeToneElement ? activeToneElement.innerText : 'Gen-Z Humor';
                
                const visualCue = document.getElementById('cue')?.innerText || 'N/A';
                const voiceoverScript = document.getElementById('voiceover')?.innerText || 'N/A';
                const audioTrack = document.getElementById('audio')?.innerText || 'N/A';
                const hookStrategy = document.getElementById('hook')?.innerText || 'N/A';
                
                const tagSpans = document.querySelectorAll('#hashtags .tag');
                let tagsArray = [];
                tagSpans.forEach(span => tagsArray.push(span.innerText));
                const totalHashtags = tagsArray.join('  ') || 'N/A';

                let currentY = 20;

                // Page 1 Layout Header Configuration
                doc.setFont("Helvetica", "bold");
                doc.setFontSize(22);
                doc.setTextColor(108, 92, 231); 
                doc.text("VouchAI Content Strategy Brief", 14, currentY);
                
                currentY += 5;
                doc.setDrawColor(108, 92, 231);
                doc.setLineWidth(0.5);
                doc.line(14, currentY, 196, currentY);

                // Campaign Profile Meta Block
                currentY += 12;
                doc.setFontSize(14);
                doc.setTextColor(30, 27, 41);
                doc.text(`Campaign Report For: ${selectedCreatorName}`, 14, currentY);
                
                currentY += 7;
                doc.setFontSize(11);
                doc.setFont("Helvetica", "bold");
                doc.text("SELECTED SCRIPT TONE DIRECTION:", 14, currentY);
                doc.setFont("Helvetica", "normal");
                doc.setTextColor(108, 92, 231);
                doc.text(scriptTone, 88, currentY);

                // Trend Analytics Block
                currentY += 15;
                doc.setDrawColor(230, 230, 235);
                doc.setFillColor(248, 248, 250);
                doc.rect(14, currentY, 182, 50, "F"); 

                doc.setTextColor(30, 27, 41);
                doc.setFont("Helvetica", "bold");
                doc.setFontSize(12);
                doc.text("TREND ANALYTICS MATRICES", 18, currentY + 8);
                
                doc.setFontSize(10);
                doc.text("Recommended Audio Track:", 18, currentY + 18);
                doc.setFont("Helvetica", "normal");
                doc.text(audioTrack, 72, currentY + 18);

                doc.setFont("Helvetica", "bold");
                doc.text("Strategic Hashtags:", 18, currentY + 28);
                doc.setFont("Helvetica", "normal");
                doc.text(totalHashtags, 72, currentY + 28);

                doc.setFont("Helvetica", "bold");
                doc.text("Optimal Hook Strategy:", 18, currentY + 38);
                doc.setFont("Helvetica", "normal");
                const splitHookText = doc.splitTextToSize(hookStrategy, 115);
                doc.text(splitHookText, 72, currentY + 38);

                // Content Script Copy Sections
                currentY += 65;
                doc.setFont("Helvetica", "bold");
                doc.setFontSize(13);
                doc.setTextColor(108, 92, 231);
                doc.text("PRODUCTION SCRIPT & CREATIVE DIRECTIONS", 14, currentY);
                
                currentY += 3;
                doc.line(14, currentY, 110, currentY);

                currentY += 10;
                doc.setFontSize(10);
                doc.setFont("Helvetica", "bold");
                doc.setTextColor(85, 85, 85);
                doc.text("PACING & STYLE DIRECTIVES:", 14, currentY);
                
                currentY += 6;
                doc.setFont("Helvetica", "normal");
                doc.setTextColor(45, 52, 54);
                const splitVisualCue = doc.splitTextToSize(visualCue, 180);
                doc.text(splitVisualCue, 14, currentY);

                currentY += (splitVisualCue.length * 5) + 10;
                doc.setFont("Helvetica", "bold");
                doc.setTextColor(85, 85, 85);
                doc.text("AUDIO VOICEOVER COPY FRAMEWORK:", 14, currentY);

                currentY += 6;
                doc.setFont("Helvetica", "normal");
                doc.setTextColor(17, 17, 17);
                
                const splitScriptLines = doc.splitTextToSize(voiceoverScript, 182);
                
                for (let i = 0; i < splitScriptLines.length; i++) {
                    if (currentY > 275) { 
                        doc.addPage();
                        currentY = 20; 
                    }
                    doc.text(splitScriptLines[i], 14, currentY);
                    currentY += 6;
                }

                // Save PDF file
                doc.save(`${selectedCreatorName.replace(/\s+/g, '_')}_Campaign_Brief.pdf`);

                // Trigger confirmation alert popup
                alert(`🎉 Success! Report compiled accurately.\n"${selectedCreatorName}_Campaign_Brief.pdf" has been downloaded successfully.`);
            
            } catch (error) {
                console.error("Error during PDF generation:", error);
                alert("❌ Something went wrong inside the PDF generator. Check the console layout logs.");
            }
        });
    } else {
        console.error("❌ Button with ID 'download-script-btn' was not found in the HTML DOM!");
    }
});

// Tone Toggle Management Logic
const toggles = document.querySelectorAll('.toggle');
toggles.forEach(toggle => {
    toggle.addEventListener('click', function() {
        toggles.forEach(t => t.classList.remove('active'));
        this.classList.add('active');
    });
});