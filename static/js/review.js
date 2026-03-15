window.addEventListener('load', function(){ setTimeout(function(){ document.getElementById('loader').classList.add('out'); }, 350); });
var ro = new IntersectionObserver(function(e){ e.forEach(function(el){ if(el.isIntersecting) el.target.classList.add('in'); }); }, { threshold: 0.08 });
document.querySelectorAll('.rev').forEach(function(el){ ro.observe(el); });
function toggleMob(){ document.getElementById('ham').classList.toggle('open'); document.getElementById('mobMenu').classList.toggle('open'); }

// Confirm delete
var pendForm = null;
function cfmDel(e, form){ e.preventDefault(); pendForm = form; document.getElementById('overlay').classList.add('open'); return false; }
function closeOv(){ document.getElementById('overlay').classList.remove('open'); pendForm = null; }
document.getElementById('cfmBtn').addEventListener('click', function(){ if(pendForm) pendForm.submit(); });

// Filter
function setChip(v, el){
  document.querySelectorAll('.chip').forEach(function(c){ c.classList.remove('active'); });
  el.classList.add('active');
  document.getElementById('sentFilter').value = v;
  applyFilter();
}
function applyFilter(){
  var q = document.getElementById('searchInput').value.toLowerCase();
  var s = document.getElementById('sentFilter').value;
  document.querySelectorAll('.rc').forEach(function(c){
    var mt = !q || c.dataset.text.includes(q) || c.dataset.prod.includes(q);
    var ms = !s || c.dataset.sent === s;
    c.style.display = (mt && ms) ? '' : 'none';
  });
  document.querySelectorAll('.pg-group').forEach(function(g){
    var vis = Array.from(g.querySelectorAll('.rc')).some(function(c){ return c.style.display !== 'none'; });
    g.style.display = vis ? '' : 'none';
  });
}
function toggleRead(id, btn){
  var el = document.getElementById('txt_' + id);
  var exp = el.classList.toggle('expanded');
  btn.textContent = exp ? 'Show less ↑' : 'Read more ↓';
}