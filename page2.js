document.getElementById('analyze').addEventListener('click', function() {
    const style = document.getElementById('style-select').value;
    localStorage.setItem('selectedStyle', style);
    window.location.href = 'dashboard.html';
});