/* longest shortage by year (cached values from the spreadsheet's Daily Running Totals, 50 m³ tank) */
(function(){
  var d={2025:17,2024:15,2023:16,2022:12,2021:22,2020:62,2019:13,2018:13,2017:16,2016:11,2015:19,2014:10,2013:10,2012:13,2011:44,2010:71,2009:17,2008:53,2007:34,2006:40,2005:33,2004:17,2003:31,2002:52,2001:30};
  var box=document.getElementById('streakBars'), mx=71, html='';
  Object.keys(d).sort(function(a,b){return b-a;}).forEach(function(y){
    html+='<div class="brow" role="row" title="'+y+': '+d[y]+' days"><span class="by" role="cell">'+y+'</span><span class="bt" role="cell"><i style="width:'+(d[y]/mx*100).toFixed(1)+'%"></i></span><span class="bv" role="cell">'+d[y]+' d</span></div>';
  });
  box.innerHTML=html;
})();

/* Tank-size sweep (re-run of the RETAIN mass-balance spreadsheet) */
(function(){
  var caps=[10,25,50,75,100,150,200,250,300,400,500];
  var recent=[47.5,33.0,22.0,16.9,13.7,10.2,7.7,6.1,5.0,4.0,2.8];
  var recentMax=[62,62,62,62,62,62,56,50,46,46,37];
  var full=[54.6,42.3,33.0,29.0,26.5,23.7,21.6,20.2,19.0,17.7,16.3];
  var tb=document.querySelector('#tankTable tbody');
  caps.forEach(function(c,i){var tr=document.createElement('tr');
    tr.innerHTML='<td>'+c+'</td><td class="num">'+recent[i].toFixed(1)+'%</td><td class="num">'+recentMax[i]+' days</td><td class="num">'+full[i].toFixed(1)+'%</td>';tb.appendChild(tr);});

  var fig=document.getElementById('tankChart'), svg=fig.querySelector('svg'), tip=fig.querySelector('.tip'), wrap=fig.querySelector('.chart-wrap');
  var NS='http://www.w3.org/2000/svg';
  function el(n,a,p){var e=document.createElementNS(NS,n);for(var k in a)e.setAttribute(k,a[k]);(p||svg).appendChild(e);return e;}
  function draw(){
    while(svg.firstChild)svg.removeChild(svg.firstChild);
    var W=wrap.clientWidth, H=Math.max(240,Math.min(320,W*0.5));
    var m={l:44,r:W<500?16:118,t:12,b:40}, iw=W-m.l-m.r, ih=H-m.t-m.b;
    svg.setAttribute('viewBox','0 0 '+W+' '+H); svg.setAttribute('width',W); svg.setAttribute('height',H);
    var x=function(v){return m.l+v/500*iw;}, y=function(v){return m.t+ih-v/60*ih;};
    [0,20,40,60].forEach(function(t){
      el('line',{x1:m.l,x2:m.l+iw,y1:y(t),y2:y(t),class:'grid'});
      var tx=el('text',{x:m.l-8,y:y(t)+4,class:'tick','text-anchor':'end'});tx.textContent=t+'%';});
    [0,100,200,300,400,500].forEach(function(t){var tx=el('text',{x:x(t),y:m.t+ih+18,class:'tick','text-anchor':'middle'});tx.textContent=t;});
    var xl=el('text',{x:m.l+iw/2,y:H-4,class:'axlab','text-anchor':'middle'});xl.textContent='Tank size (m³)';
    function series(vals,cls,label){
      var d=vals.map(function(v,i){return (i?'L':'M')+x(caps[i]).toFixed(1)+','+y(v).toFixed(1);}).join('');
      el('path',{d:d,class:'ln '+cls});
      vals.forEach(function(v,i){el('circle',{cx:x(caps[i]),cy:y(v),r:4,class:'dot '+cls});});
      if(W>=500){var t=el('text',{x:x(500)+10,y:y(vals[vals.length-1])+4,class:'dl'});t.textContent=label;}
    }
    series(full,'s2','2000–2025');
    series(recent,'s1','2012–2025');
    var hair=el('line',{x1:0,x2:0,y1:m.t,y2:m.t+ih,class:'hair',visibility:'hidden'});
    var hit=el('rect',{x:m.l,y:m.t,width:iw,height:ih,fill:'transparent'});
    function move(ev){
      var r=svg.getBoundingClientRect(), px=(ev.touches?ev.touches[0].clientX:ev.clientX)-r.left;
      var v=(px-m.l)/iw*500, bi=0; caps.forEach(function(c,i){if(Math.abs(c-v)<Math.abs(caps[bi]-v))bi=i;});
      var cx=x(caps[bi]); hair.setAttribute('x1',cx);hair.setAttribute('x2',cx);hair.setAttribute('visibility','visible');
      tip.hidden=false;
      tip.innerHTML='<b>'+caps[bi]+' m³ tank</b><div><i style="background:var(--s1)"></i>2012–25: '+recent[bi].toFixed(1)+'% of days</div><div><i style="background:var(--s2)"></i>2000–25: '+full[bi].toFixed(1)+'% of days</div><div class="muted">Longest outage (2012–25): '+recentMax[bi]+' days</div>';
      var tw=tip.offsetWidth; var left=cx+12; if(left+tw>W) left=cx-tw-12; tip.style.left=left+'px'; tip.style.top=(m.t+6)+'px';
    }
    function leave(){hair.setAttribute('visibility','hidden');tip.hidden=true;}
    hit.addEventListener('mousemove',move);hit.addEventListener('touchstart',move,{passive:true});hit.addEventListener('touchmove',move,{passive:true});hit.addEventListener('mouseleave',leave);
  }
  draw(); var to; window.addEventListener('resize',function(){clearTimeout(to);to=setTimeout(draw,120);});
})();
