window.addEventListener('load', function () {
    // Loader ko hatane ke liye
    setTimeout(function () {
        const loader = document.getElementById('loader');
        const card = document.getElementById('card');
        
        if(loader) loader.classList.add('out');
        
        // CRITICAL FIX: Card ko dikhane ke liye '.vis' class add karna zaroori hai
        if(card) card.classList.add('vis'); 
    }, 350);
});

// Password Toggle Logic (Eye button ke liye)
document.addEventListener('DOMContentLoaded', function() {
    const pBtn = document.getElementById('pBtn');
    const passwordInput = document.querySelector('input[name="password"]');

    if (pBtn && passwordInput) {
        pBtn.addEventListener('click', function() {
            const isPwd = passwordInput.type === 'password';
            passwordInput.type = isPwd ? 'text' : 'password';
            this.textContent = isPwd ? '🙈' : '👁️';
        });
    }
});

// Aapka purana IntersectionObserver logic (Reviews ke liye)
var ro = new IntersectionObserver(function (e) {
    e.forEach(function (el) {
        if (el.isIntersecting) el.target.classList.add('in');
    });
}, { threshold: 0.08 });

document.querySelectorAll('.rev').forEach(function (el) { ro.observe(el); });

function toggleMob() {
    document.getElementById('ham').classList.toggle('open');
    document.getElementById('mobMenu').classList.toggle('open');
}