
window.addEventListener('load', function () { setTimeout(function () { document.getElementById('loader').classList.add('out'); }, 350); });
var ro = new IntersectionObserver(function (e) { e.forEach(function (el) { if (el.isIntersecting) el.target.classList.add('in'); }); }, { threshold: 0.08 });
document.querySelectorAll('.rev').forEach(function (el) { ro.observe(el); });
function toggleMob() { document.getElementById('ham').classList.toggle('open'); document.getElementById('mobMenu').classList.toggle('open'); }
