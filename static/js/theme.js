const btn = document.getElementById('theme-toggle');
const root = document.documentElement;
function applyTheme(t){
  if(t==='dark') document.documentElement.setAttribute('data-theme','dark');
  else document.documentElement.removeAttribute('data-theme');
}
const saved = localStorage.getItem('theme') || 'light';
applyTheme(saved);
if(btn){ btn.addEventListener('click', ()=>{
  const cur = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
  const next = cur === 'dark' ? 'light' : 'dark';
  applyTheme(next);
  localStorage.setItem('theme', next);
})}
