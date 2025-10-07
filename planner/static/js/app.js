// app.js — tiny UI polish
document.addEventListener('DOMContentLoaded', function(){
  // add subtle hover to day cards
  document.querySelectorAll('.day-col').forEach(el=>{
    el.addEventListener('mouseenter', ()=> el.style.transform='translateY(-6px)');
    el.addEventListener('mouseleave', ()=> el.style.transform='translateY(0)');
    el.style.transition='transform .22s cubic-bezier(.2,.9,.3,1)';
  });
});