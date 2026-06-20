/*document.getElementById('verify').addEventListener('click', function() {
    const email = document.getElementById('email').value;
    const alertBox = document.getElementById('alert');
    
    if(email.includes('@') && email.includes('.')) {
        alertBox.classList.remove('hidden');
    } else {
        alert('Please enter a valid email format.');
    }
});
*/
document.getElementById('next-page').addEventListener('click', function() {
    const company = document.getElementById('company').value;
    const niche = document.getElementById('niche').value;
    
    localStorage.setItem('companyName', company);
    localStorage.setItem('corporateNiche', niche);
    
    window.location.href = 'campaign.html';
});