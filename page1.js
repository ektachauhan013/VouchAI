document.getElementById('next-page').addEventListener('click', function(e) {
    e.preventDefault();

    const company = document.getElementById('company')?.value.trim();
    const niche = document.getElementById('niche')?.value;
    const email = document.getElementById('email')?.value.trim();
    const password = document.getElementById('password')?.value;

    // Field completeness validation condition
    if (!company || !niche || !email || !password) {
        alert('Please fill out all registration and identity fields before continuing.');
        return;
    }

    // RegEx verification for strict email structural patterns
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(email)) {
        alert('Please enter a valid email address format.');
        return;
    }

    if (password.length < 6) {
        alert('Password should be at least 6 characters long for system safety.');
        return;
    }

    localStorage.setItem('companyName', company);
    localStorage.setItem('corporateNiche', niche);
    
    window.location.href = 'campaign.html';
});