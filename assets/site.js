/* theme toggle */
(function(){
  var b=document.getElementById('themeBtn'), r=document.documentElement;
  if(!b) return;
  b.addEventListener('click',function(){
    var cur=r.getAttribute('data-theme') || (matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');
    var nx=cur==='dark'?'light':'dark'; r.setAttribute('data-theme',nx);
    try{localStorage.setItem('tg-theme',nx);}catch(e){}
  });
})();
/* copy buttons */
document.querySelectorAll('.codeblock .copy').forEach(function(btn){
  btn.addEventListener('click',function(){
    var txt=btn.closest('.codeblock').querySelector('pre').innerText;
    var done=function(){btn.textContent='Copied';setTimeout(function(){btn.textContent='Copy';},1400);};
    if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(txt).then(done,function(){});}
    else{var t=document.createElement('textarea');t.value=txt;document.body.appendChild(t);t.select();try{document.execCommand('copy');done();}catch(e){}t.remove();}
  });
});

