#!/usr/bin/env python3
"""
make_interactive.py — regenerate BOTEC-asylum-figure3.html (the animated, single-panel
interactive) from model.py, matching figure-one-worker.svg: one working asylum seeker at
the 80th percentile of all refugee earners, over the 40-year charge horizon.

    python3 make_interactive.py

CGD Interactive Toolkit build (brand tokens, iframe-resize, analytics, tooltip, a11y).
Only the plotted data and the narrative are model-derived; the scaffolding is fixed.
"""
import model as m

YRS = m.HORIZON
tjA, tjC = m.trajectory(m.EARN_A), m.trajectory(m.EARN_C)
taxA = [m.tax(e) for e in m.EARN_A]; taxC = [m.tax(e) for e in m.EARN_C]
repA, repC = m.repay_stream(m.EARN_A), m.repay_stream(m.EARN_C)

# geometry: x 90..860 across YRS years; £0 at y=400, £40k at y=85.7 (unchanged from v1)
X0, X1, YB, Y40, VMAX = 90.0, 860.0, 400.0, 85.7, 40000
def X(yr): return X0 + (yr - 1) * (X1 - X0) / (YRS - 1)
def Y(v):  return round(YB - v * (YB - Y40) / VMAX, 1)
def pstr(seq): return " ".join(f"{round(a,1)},{round(b,1)}" for a, b in seq)
def area(vals): return pstr([(X0, YB)] + [(X(i+1), Y(vals[i])) for i in range(YRS)] + [(X1, YB)])
def band(base, top):
    up = [(X(i+1), Y(base[i] + top[i])) for i in range(YRS)]
    dn = [(X(i+1), Y(base[i])) for i in range(YRS-1, -1, -1)]
    return pstr(up + dn)
def line(vals): return pstr([(X(i+1), Y(vals[i])) for i in range(YRS)])

def rk(v):   return f"£{round(v/1000)*1000:,}"      # nearest £1,000
def r100(v): return f"£{round(v/100)*100:,}"         # nearest £100

taxA_s, taxC_s = rk(tjA["tax"]), rk(tjC["tax"])
extra_s = rk(tjC["tax"] - tjA["tax"])
pv_s = r100(tjA["repaid_pv"])
clrA, clrC = tjA["clears_year"], tjC["clears_year"]
peakA, peakC = m.PLATEAU_A, m.PLATEAU_C

xticks = "".join(
    f'<text x="{round(X(yr),1)}" y="422">{("yr "+str(yr)) if yr==1 else str(yr)}</text>'
    for yr in (1, 10, 20, 30, 40))
arrA = "[" + ",".join(str(round(e)) for e in m.EARN_A) + "]"
arrC = "[" + ",".join(str(round(e)) for e in m.EARN_C) + "]"

R = {
  "HEADTITLE": f"Asylum charge repayment over {YRS} years",
  "FIGTITLE": f"One asylum seeker’s earnings, tax, and £10,000 charge repayment over {YRS} years",
  "FIGDESC": (f"Step 1, status quo: gross earnings rise to about £{peakA//1000},000, paying {taxA_s} "
              f"in tax over {YRS} years. Step 2 adds the £10,000 charge, repaid in full but only by "
              f"year {clrA} — about {pv_s} in present value. Step 3, with the right to work at three "
              f"months, earnings rise to about £{peakC//1000},000, {extra_s} more tax is paid, and the "
              f"charge clears by year {clrC}."),
  "XTICKS": xticks,
  "AXLABEL": f"£ per year, over {YRS} years",
  "SQTAX": area(taxA), "CHARGESQ": band(taxA, repA),
  "CTAX": area(taxC), "CHARGEC": band(taxC, repC),
  "SQEARN": line(m.EARN_A), "CEARN": line(m.EARN_C),
  "NOTE1": (f"Status quo — the 12-month work ban. Over {YRS} years this earner, at the 80th percentile "
            f"of all refugees, pays <strong>{taxA_s} in income tax and NI</strong>. No charge yet."),
  "NOTE2": (f"Now add the £10,000 charge. Earnings and tax are <strong>unchanged</strong> — it doesn’t "
            f"help anyone earn. It is repaid in full, but so slowly it clears only by <strong>year "
            f"{clrA}</strong> — worth just <strong>~{pv_s} in today’s money</strong>."),
  "NOTE3": (f"Now the <strong>right to work at 3 months</strong>. Earlier work and less scarring lift the "
            f"whole path (faded line = status quo): <strong>{extra_s} more tax</strong>, and the charge "
            f"<strong>clears by year {clrC}</strong>."),
  "ROW1": f"<tr><td>1 · Status quo</td><td>{taxA_s}</td><td>—</td></tr>",
  "ROW2": f"<tr><td>2 · + £10,000 charge</td><td>{taxA_s}</td><td>£10,000 (clears year {clrA}; ~{pv_s} in present value)</td></tr>",
  "ROW3": f"<tr><td>3 · + right to work at 3 months</td><td>{taxC_s}</td><td>£10,000 (cleared by year {clrC})</td></tr>",
  "ARRA": arrA, "ARRC": arrC, "YRS": str(YRS), "XDEN": f"{X1-X0:.0f}/{YRS-1}",
}

TEMPLATE = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%%HEADTITLE%%</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  /* CGD brand tokens (cgd-brand-reference.md). Sofia Pro stand-in: Inter. */
  :root{
    --cgd-teal:#0B4C5B; --cgd-light-teal:#006970; --cgd-gold:#FFB52C; --cgd-blue:#2D99B5;
    --cgd-teal-gray:#85A5AD; --cgd-dark-gray:#394649; --cgd-teal-black:#1A272A;
    --cgd-light-gray:#DFE0E2; --cgd-red:#D15553;
    --font:'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif;
  }
  /* iframe-inside reset: no outer chrome, no root margin/padding, transparent bg */
  *{box-sizing:border-box; margin:0; padding:0;}
  html,body{background:transparent;}
  body{font-family:var(--font); color:var(--cgd-teal-black); overflow-x:hidden;}
  .pad{padding:2px 2px 6px;}                 /* internal spacing only */

  .controls{display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-bottom:10px;}
  .step{font:600 clamp(12px,1.6vw,13.5px)/1 var(--font); color:var(--cgd-teal);
    background:#fff; border:1.5px solid var(--cgd-teal-gray); border-radius:22px;
    padding:7px 14px; cursor:pointer;}
  .step[aria-pressed="true"]{color:#fff; background:var(--cgd-light-teal); border-color:var(--cgd-light-teal);}
  .step:focus-visible, .replay:focus-visible{outline:3px solid var(--cgd-gold); outline-offset:2px;}
  .replay{margin-left:auto; font:600 12px var(--font); color:var(--cgd-dark-gray);
    background:none; border:none; cursor:pointer; text-decoration:underline;}

  svg{display:block; width:100%; height:auto; overflow:visible;}
  .legend{font:500 clamp(11px,1.5vw,12.5px) var(--font); fill:var(--cgd-teal);}
  .tick{font:400 clamp(10px,1.4vw,12px) var(--font); fill:var(--cgd-teal-black); font-variant-numeric:tabular-nums;}
  .axlabel{font:500 clamp(11px,1.5vw,12.5px) var(--font); fill:var(--cgd-teal);}

  /* series (CGD categorical/stoplight): earnings=Light Teal line, tax=Blue, charge=Red */
  .earnline{fill:none; stroke:var(--cgd-light-teal); stroke-width:3; stroke-linejoin:round; stroke-linecap:round;}
  .sqtax{fill:var(--cgd-blue);}  .ctax{fill:var(--cgd-blue);}
  .chargeSQ,.chargeC{fill:var(--cgd-red);}
  .grid{stroke:var(--cgd-light-gray); stroke-width:1;}
  .baseline{stroke:var(--cgd-teal-black); stroke-width:1;}

  /* build-up by step (opacity fades; honour reduced motion) */
  .layer,.sqearn{transition:opacity .55s ease;}
  .chargeSQ,.chargeC,.ctax,.cearn{opacity:0;}
  [data-step="3"] .sqtax{opacity:0;}
  [data-step="3"] .sqearn{opacity:.4; stroke:var(--cgd-teal-gray); stroke-dasharray:6 4;}
  [data-step="2"] .chargeSQ{opacity:.92;}
  [data-step="3"] .chargeC{opacity:.92;}
  [data-step="3"] .ctax{opacity:.9;}
  [data-step="3"] .cearn{opacity:1;}
  @media (prefers-reduced-motion: reduce){ .layer,.sqearn{transition:none;} }

  .note{margin-top:10px; font:400 clamp(13px,1.7vw,14px)/1.4 var(--font); color:var(--cgd-teal-black); min-height:44px;}
  .note strong{font-weight:700; color:var(--cgd-teal);}
  details.data{margin-top:8px; font:400 12.5px var(--font); color:var(--cgd-dark-gray);}
  details.data summary{cursor:pointer; color:var(--cgd-teal); font-weight:600;}
  details.data table{border-collapse:collapse; margin-top:8px; font-variant-numeric:tabular-nums;}
  details.data th, details.data td{border:1px solid var(--cgd-light-gray); padding:5px 9px; text-align:left;}
  details.data th{color:var(--cgd-teal); font-weight:600;}
  .visually-hidden{position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); white-space:nowrap;}
</style>
</head>
<body>
<div class="pad">
  <div class="controls" role="group" aria-label="Choose which scenario to show">
    <button type="button" class="step" data-s="1" aria-pressed="true">1 · Status quo</button>
    <button type="button" class="step" data-s="2" aria-pressed="false">2 · + £10,000 charge</button>
    <button type="button" class="step" data-s="3" aria-pressed="false">3 · + right to work at 3 months</button>
    <button type="button" class="replay" id="replay">↻ Replay</button>
  </div>

  <div id="fig" data-step="1">
  <svg viewBox="0 0 900 460" role="img" aria-labelledby="figTitle figDesc">
    <title id="figTitle">%%FIGTITLE%%</title>
    <desc id="figDesc">%%FIGDESC%%</desc>

    <!-- legend -->
    <line x1="90" y1="30" x2="118" y2="30" class="earnline"/><text class="legend" x="124" y="34">Gross earnings</text>
    <rect x="270" y="24" width="12" height="12" class="ctax"/><text class="legend" x="288" y="34">Income tax + NI</text>
    <rect x="440" y="24" width="12" height="12" class="chargeC"/><text class="legend" x="458" y="34">£10k charge repaid</text>

    <!-- gridlines + axes -->
    <g><line class="grid" x1="90" y1="321.4" x2="860" y2="321.4"/><line class="grid" x1="90" y1="242.9" x2="860" y2="242.9"/><line class="grid" x1="90" y1="164.3" x2="860" y2="164.3"/><line class="grid" x1="90" y1="85.7" x2="860" y2="85.7"/></g>
    <g class="tick" text-anchor="end"><text x="80" y="404">£0</text><text x="80" y="325">£10k</text><text x="80" y="247">£20k</text><text x="80" y="168">£30k</text><text x="80" y="90">£40k</text></g>
    <line class="baseline" x1="90" y1="400" x2="860" y2="400"/>
    <line id="cross" x1="90" y1="66" x2="90" y2="400" stroke="#85A5AD" stroke-width="1" stroke-dasharray="4 3" opacity="0"/>
    <g class="tick" text-anchor="middle">%%XTICKS%%</g>
    <text class="axlabel" x="90" y="448">%%AXLABEL%%</text>

    <!-- status-quo tax + charge -->
    <polygon class="layer sqtax" fill-opacity="0.9" points="%%SQTAX%%"/>
    <polygon class="layer chargeSQ" fill-opacity="0.92" points="%%CHARGESQ%%"/>
    <!-- right-to-work tax + charge -->
    <polygon class="layer ctax" fill-opacity="0.9" points="%%CTAX%%"/>
    <polygon class="layer chargeC" fill-opacity="0.92" points="%%CHARGEC%%"/>
    <!-- earnings lines (status quo becomes faded ghost at step 3; right-to-work on top) -->
    <polyline class="sqearn earnline" points="%%SQEARN%%"/>
    <polyline class="layer cearn earnline" points="%%CEARN%%"/>
  </svg>
  </div>

  <p class="note" id="note" aria-live="polite"></p>

  <details class="data">
    <summary>Show the numbers</summary>
    <table>
      <thead><tr><th>Scenario</th><th>%%YRS%%-yr tax paid</th><th>£10k charge repaid</th></tr></thead>
      <tbody>
        %%ROW1%%
        %%ROW2%%
        %%ROW3%%
      </tbody>
    </table>
    <p style="margin-top:6px">Illustrative: one working asylum seeker at the 80th percentile of all refugee earners (many never work at all). Tax = income tax + employee NI (28% above £12,570); charge repayment = 9% above £25,000, capped at £10,000, over %%YRS%% years.</p>
  </details>
</div>

<script>
/* CGD analytics postMessage utility (analytics-tracking-standard.md) */
(function(){
  var PARENT_ORIGIN='https://www.cgdev.org';
  var NAME=window.CGD_INTERACTIVE_NAME||'uk-asylum-charge-figure1';
  var VALID=new Set(['filter','preset','detail_open','detail_close','view_control','navigate','compare','external_link','download']);
  var viewed=false;
  function send(ev,p){ if(window.parent) window.parent.postMessage(Object.assign({type:'cgd_analytics',event:ev},p),PARENT_ORIGIN); }
  window.CGDTracking={
    trackView:function(){ if(viewed)return; viewed=true; send('interactive_view',{interactive_name:NAME}); },
    trackEngagement:function(t,l,v){ if(!VALID.has(t))return; var p={interactive_name:NAME,action_type:t,action_label:l};
      if(v!==undefined&&v!==null&&v!=='') p.action_value=String(v); send('interactive_engagement',p); }
  };
})();
</script>

<script>
/* CGD iframe-resize (interactive-coding-standard.md). Posts to cgdev.org and, for
   preview, to the actual parent origin (github.io) so the embed self-sizes there too. */
(function(){
  var origins=['https://www.cgdev.org'];
  try{ var ref=document.referrer && new URL(document.referrer).origin;
       if(ref && /^https:/.test(ref) && origins.indexOf(ref)===-1) origins.push(ref); }catch(e){}
  var last=-1;
  function report(){ var h=Math.ceil(document.body.getBoundingClientRect().height);
    if(h<=0||h===last) return; last=h;
    origins.forEach(function(o){ window.parent.postMessage({type:'cgd-iframe-resize',height:h}, o); }); }
  window.addEventListener('load',report);
  if(document.fonts&&document.fonts.ready) document.fonts.ready.then(report);
  if(window.ResizeObserver) new ResizeObserver(report).observe(document.body); else window.addEventListener('resize',report);
})();
</script>

<script>
/* step controller */
(function(){
  var fig=document.getElementById('fig'), note=document.getElementById('note'),
      btns=[].slice.call(document.querySelectorAll('.step')),
      reduce=window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches,
      timer=null, played=false;
  var NOTES={
    1:'%%NOTE1%%',
    2:'%%NOTE2%%',
    3:'%%NOTE3%%'
  };
  function setStep(n){
    fig.dataset.step=String(n);
    btns.forEach(function(b){ b.setAttribute('aria-pressed', b.dataset.s===String(n)?'true':'false'); });
    note.innerHTML=NOTES[n];
  }
  function play(){ clearTimeout(timer); setStep(1);
    if(reduce) return;                      // honour reduced motion: no auto-sequence
    timer=setTimeout(function(){ setStep(2);
      timer=setTimeout(function(){ setStep(3); },1800); },1800);
  }
  btns.forEach(function(b){ b.addEventListener('click',function(){
    clearTimeout(timer); played=true; setStep(+b.dataset.s);
    CGDTracking.trackEngagement('navigate','scenario_step', b.textContent.trim());
  }); });
  document.getElementById('replay').addEventListener('click',function(){
    played=true; play(); CGDTracking.trackEngagement('view_control','replay');
  });
  function maybePlay(){ if(played) return; var r=fig.getBoundingClientRect();
    if(r.top < (window.innerHeight||800)*0.85 && r.bottom>0){ played=true; play(); } }
  if('IntersectionObserver' in window){
    new IntersectionObserver(function(es){ es.forEach(function(e){ if(e.isIntersecting&&!played){ played=true; play(); } }); },{threshold:.35}).observe(fig);
  }
  setStep(1); maybePlay(); setTimeout(maybePlay,300);
  CGDTracking.trackView();
})();
</script>

<script>
/* Crosshair tooltip: hover the chart to read each year's values for the current scenario. */
(function(){
  var fig=document.getElementById('fig'), svg=fig.querySelector('svg'), cross=document.getElementById('cross');
  var A=%%ARRA%%;
  var C=%%ARRC%%;
  function tax(e){ return 0.28*Math.max(0,e-12570); }
  function cum(arr){ var bal=10000,o=[]; arr.forEach(function(e){ var r=Math.min(bal,0.09*Math.max(0,e-25000)); bal-=r; o.push(10000-bal); }); return o; }
  var cumA=cum(A), cumC=cum(C);
  function xOf(yr){ return 90+(yr-1)*(%%XDEN%%); }
  function fmt(n){ return '£'+Math.round(n).toLocaleString('en-GB'); }
  var tip=document.createElement('div');
  tip.style.cssText='position:fixed;z-index:9998;pointer-events:none;opacity:0;transition:opacity .1s;max-width:230px;'+
    'background:#1A272A;color:#fff;font:400 12.5px/1.45 Inter,system-ui,sans-serif;padding:8px 11px;border-radius:6px;box-shadow:0 2px 12px rgba(0,0,0,.28);';
  document.body.appendChild(tip);
  function hide(){ tip.style.opacity='0'; cross.setAttribute('opacity','0'); }
  fig.addEventListener('mouseleave', hide);
  fig.addEventListener('mousemove', function(e){
    var rect=svg.getBoundingClientRect();
    if(!rect.width){ hide(); return; }
    var sx=(e.clientX-rect.left)*(900/rect.width);
    if(sx<80||sx>870){ hide(); return; }
    var yr=Math.max(1,Math.min(%%YRS%%,Math.round((sx-90)/(%%XDEN%%))+1));
    var step=+fig.dataset.step;
    var earn=(step===3?C:A)[yr-1], t=tax(earn);
    var rep = step===3 ? cumC[yr-1] : (step===2 ? cumA[yr-1] : null);
    var html='<b>Year '+yr+'</b><br>Earnings '+fmt(earn)+'<br>Tax + NI '+fmt(t)+(rep!==null?'<br>Charge repaid '+fmt(rep)+' of £10,000':'');
    tip.innerHTML=html; tip.style.opacity='1';
    cross.setAttribute('x1',xOf(yr)); cross.setAttribute('x2',xOf(yr)); cross.setAttribute('opacity','0.9');
    var x=e.clientX+14, y=e.clientY+14, w=tip.offsetWidth, h=tip.offsetHeight;
    if(x+w>window.innerWidth-8) x=e.clientX-w-14;
    if(y+h>window.innerHeight-8) y=e.clientY-h-14;
    tip.style.left=x+'px'; tip.style.top=y+'px';
  });
})();
</script>
</body>
</html>
'''

out = TEMPLATE
for k, v in R.items():
    out = out.replace(f"%%{k}%%", v)
with open("BOTEC-asylum-figure3.html", "w") as f:
    f.write(out)
assert "%%" not in out, "unreplaced token remains"
print("Wrote BOTEC-asylum-figure3.html")
print(f"  A: {taxA_s} tax, charge clears yr {clrA} (PV {pv_s}); C: {taxC_s} tax (+{extra_s}), clears yr {clrC}")
