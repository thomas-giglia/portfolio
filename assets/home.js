/* home: category filters (hash-aware: /#ewb, /#racing, /#course) */
(function(){
  var btns=[].slice.call(document.querySelectorAll('.filters button')), cards=[].slice.call(document.querySelectorAll('#projects .card'));
  function apply(f,push){
    btns.forEach(function(b){b.setAttribute('aria-pressed', b.dataset.f===f);});
    cards.forEach(function(c){c.hidden = !(f==='all' || c.dataset.cat===f);});
    if(push){try{history.replaceState(null,'',f==='all'?location.pathname:'#'+f);}catch(e){}}
  }
  btns.forEach(function(b){b.addEventListener('click',function(){apply(b.dataset.f,true);});});
  var h=(location.hash||'').slice(1); if(['ewb','racing','course'].indexOf(h)>=0) apply(h,false);
})();
