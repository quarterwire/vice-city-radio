(()=>{
"use strict";
const S=(window.STATIONS||[]).filter(s=>s.tracks&&s.tracks.length);
const n=S.length;
const $=id=>document.getElementById(id);
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const mq=matchMedia("(max-width:760px)");
const store={get(k,d){try{const v=JSON.parse(localStorage.getItem("vcr:"+k));return typeof v===typeof d&&v===v?v:d}catch(e){return d}},set(k,v){try{localStorage.setItem("vcr:"+k,JSON.stringify(v))}catch(e){}}};

let sel=Math.max(0,S.findIndex(s=>s.id===store.get("st","flash")));
let on=-1,playing=false,pos=0,cur=-1,vol=+store.get("vol",80),errs=0,tuneTimer=0,hintTimer=0,ytState=-1;

/* ---------- scenery (generated, blurred) ---------- */
function rng(seed){let a=seed>>>0;return()=>{a=a+0x6D2B79F5>>>0;let t=a;t=Math.imul(t^t>>>15,t|1);t^=t+Math.imul(t^t>>>7,t|61);return((t^t>>>14)>>>0)/4294967296}}
function hash(s){let h=2166136261;for(const c of s)h=Math.imul(h^c.charCodeAt(0),16777619);return h>>>0}
const BGS=["bg/street.webp","bg/hotel.webp","bg/gas.webp"];
const sceneDay=$("sceneDay"),sceneNight=$("sceneNight");
const bgi=(+store.get("bg",-1)+1)%BGS.length;store.set("bg",bgi);
sceneDay.style.backgroundImage=`url(${BGS[bgi]})`;sceneNight.style.backgroundImage=`url(${BGS[(bgi+1)%BGS.length]})`;

/* ---------- logos ---------- */
const BOLT='<svg viewBox="0 0 40 70"><path d="M24 0 4 40h14L10 70 36 26H22z" fill="#ff3d9a" stroke="#111" stroke-width="3" stroke-linejoin="round"/></svg>';
const WAVE='<svg viewBox="0 0 100 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><path d="M2 9c8-7 16-7 24 0s16 7 24 0 16-7 24 0 16 7 24 0" stroke="#ffd23f"/><path d="M2 19c8-7 16-7 24 0s16 7 24 0 16-7 24 0 16 7 24 0"/></svg>';
function logo(st){
  const t=st.tile,l=t.l.map(esc);let h;
  if(t.img)return `<div class="logo pic${t.img===2?" full":""}" style="--bg:${t.bg}"><img src="logos/${st.id}.webp" alt="" decoding="async" draggable="false"></div>`;
  switch(t.s){
    case"stack":h=`<b>${l[0]}</b><b>${l[1]}</b><i>${l[2]}</i>`;break;
    case"oval":h=`<div class="ov"><small>${l[0]}</small><b>${l[1]}</b><i>${l[2]}</i></div>`;break;
    case"mono":h=`<b>${l[0]}</b><span>${l[1]}</span>${l[2]?`<small>${l[2]}</small>`:""}`;break;
    case"chunk":h=`<div class="nuts"><i></i><i></i></div><b>${l[0]}</b><small>${l[1]}</small>`;break;
    case"outline":h=`<div class="frame"><b>${l[0]}</b><b>${l[1]}</b></div>`;break;
    case"flash":h=`<div class="fl"><b>${l[0]}</b>${BOLT}</div><small>${l[1]}</small>`;break;
    case"serif":h=`<i class="r"></i><b>${l[0]}</b><small>${l[1]}</small><i class="r"></i>`;break;
    case"round":h=`<div class="hex"><b>${l[0]}</b><small>${l[1]}</small></div>`;break;
    case"kaleido":h=`<div class="kal"></div><b>${l[0]}<br>${l[1]}</b>`;break;
    case"wave":h=`<b>${l[0]}</b>${WAVE}<small>${l[1]}</small>`;break;
    case"dot":h=`<div class="dot"><b>${l[0]}</b></div><small>${l[1]}</small>`;break;
    case"globe":h=`<div class="gl"></div><b>${l[0]}</b><small>${l[1]}</small>`;break;
    default:h=`<b>${l[0]}</b>${l[1]?`<span>${l[1]}</span>`:""}`;
  }
  return `<div class="logo s-${t.s}" style="--bg:${t.bg};--fg:${t.fg};--ac:${t.ac}" aria-hidden="true">${h}</div>`;
}

/* ---------- carousel ---------- */
const car=$("car");
car.innerHTML=S.map((s,i)=>`<button class="tile" data-i="${i}" aria-label="${esc(s.name)}">${logo(s)}</button>`).join("");
const tiles=[...car.children];
function wrap(d){d%=n;if(d>n/2)d-=n;if(d<-n/2)d+=n;return d}
let M=null;
function measure(){
  const w=tiles[0].offsetWidth,gap=parseFloat(getComputedStyle(car).getPropertyValue("--gap"))||w*.3;
  const tabs=document.querySelector(".tabs"),cr=car.getBoundingClientRect();
  if(!w||!cr.width)return null;
  return{w,gap,minX:getComputedStyle(tabs).position==="absolute"?tabs.getBoundingClientRect().right+18-(cr.left+cr.width/2)+w/2:-1e9};
}
function layout(){
  if(!M)M=measure();if(!M)return;
  const{w,gap,minX}=M;
  tiles.forEach((t,i)=>{
    const d=wrap(i-sel),a=Math.abs(d);
    const x=d===0?0:Math.sign(d)*(a*(w+gap)+w*.09);
    t.style.transform=`translateX(${x}px) scale(${d===0?1.18:1})`;
    const blocked=Math.abs(x)>-minX;
    t.style.opacity=blocked?0:a===0?1:a===1?.92:a===2?.42:0;
    t.style.pointerEvents=a>2||blocked?"none":"auto";
    t.tabIndex=a===0?0:-1;
    t.classList.toggle("on",d===0);
  });
  $("posDot").style.left=(n>1?sel/(n-1)*100:50)+"%";
}

/* ---------- views ---------- */
let view="radio";
function setView(v){
  view=v;
  document.querySelectorAll(".tab").forEach(b=>b.setAttribute("aria-selected",b.dataset.v===v));
  ["radio","demand","vehicle"].forEach(k=>$("v-"+k).hidden=k!==v);
  if(v==="demand")renderList();
  if(v==="vehicle")renderVehicle();
  if(v==="radio"){M=null;requestAnimationFrame(layout)}
}
document.querySelectorAll(".tab").forEach(b=>b.onclick=()=>setView(b.dataset.v));

const fmt=s=>Math.floor(s/60)+":"+String(Math.floor(s%60)).padStart(2,"0");
function renderList(){
  const st=S[sel];
  $("dName").textContent=st.name;
  $("dCount").textContent=st.tracks.length+" tracks · tap one to play";
  const q=$("q").value.trim().toLowerCase();
  $("list").innerHTML=st.tracks.map((t,i)=>({t,i})).filter(({t})=>!q||(t[0]+" "+t[1]).toLowerCase().includes(q))
    .map(({t,i})=>`<li class="${on===sel&&cur===i?"now":""}"><button data-t="${i}"><span class="n">${on===sel&&cur===i&&playing?"▶":i+1}</span><span><span class="t">${esc(t[1])}</span><span class="a">${esc(t[0])}${t[2]?" · "+t[2]:""}</span></span><span class="d">${fmt(t[4])}</span></button></li>`).join("");
}
$("q").oninput=renderList;
$("list").onclick=e=>{const b=e.target.closest("button[data-t]");if(!b)return;unlockAudio();playOnDemand(sel,+b.dataset.t)};
function renderVehicle(){
  const st=S[sel];
  $("vName").textContent=st.name;
  $("vAbout").textContent=st.desc||st.tag;
  $("grid").innerHTML=S.map((s,i)=>`<button class="gtile${i===sel?" sel":""}" data-i="${i}" aria-label="${esc(s.name)}">${logo(s)}</button>`).join("");
}
$("grid").onclick=e=>{const b=e.target.closest("[data-i]");if(b){go(+b.dataset.i-sel);renderVehicle()}};

/* ---------- station select ---------- */
function showStation(){
  const st=S[sel];
  $("stName").innerHTML=esc(st.name)+(st.secret?'<span class="lock">SECRET</span>':"");
  $("stTag").textContent=st.tag;
  $("stHosts").textContent="With "+st.hosts;
  $("place").textContent=st.place+", Leonida";
  const acc=st.tile.ac==="#111111"||st.tile.ac==="#140014"?st.tile.bg:st.tile.ac;
  sceneDay.style.setProperty("--accent",acc);sceneNight.style.setProperty("--accent",acc);
  layout();updateTune();
  if(view==="demand")renderList();
}
function go(d){
  if(!d)return;
  sel=((sel+d)%n+n)%n;store.set("st",S[sel].id);showStation();
  if(playing){staticBurst();clearTimeout(tuneTimer);tuneTimer=setTimeout(()=>tune(sel),260)}
}
$("prev").onclick=()=>go(-1);$("next").onclick=()=>go(1);
car.addEventListener("click",e=>{const t=e.target.closest(".tile");if(!t)return;const d=wrap(+t.dataset.i-sel);if(d)go(d);else{unlockAudio();toggle()}});

/* swipe */
let sx=null,sy=0,st0=0;
car.addEventListener("pointerdown",e=>{sx=e.clientX;sy=e.clientY;st0=Date.now()});
car.addEventListener("pointerup",e=>{if(sx==null)return;const dx=e.clientX-sx,dy=e.clientY-sy;sx=null;if(Math.abs(dx)>36&&Math.abs(dx)>Math.abs(dy)){const steps=Math.abs(dx)>220&&Date.now()-st0<400?2:1;go(dx<0?steps:-steps);car.addEventListener("click",ev=>ev.stopPropagation(),{capture:true,once:true})}});
car.addEventListener("pointercancel",()=>sx=null);

/* ---------- radio clock: every station plays "live", in sync for everyone ---------- */
function prep(st){
  if(st._o)return;
  const r=rng(hash(st.id)),o=st.tracks.map((_,i)=>i);
  for(let i=o.length-1;i>0;i--){const j=Math.floor(r()*(i+1));[o[i],o[j]]=[o[j],o[i]]}
  st._o=o;st._T=o.reduce((a,i)=>a+st.tracks[i][4],0);
}
function live(st){
  prep(st);let t=(Date.now()/1000+hash(st.id)%9973)%st._T;
  for(let k=0;k<st._o.length;k++){const d=st.tracks[st._o[k]][4];if(t<d)return d-t<12?{k:(k+1)%st._o.length,off:0}:{k,off:t};t-=d}
  return{k:0,off:0};
}

/* ---------- YouTube engine ---------- */
let yt=null,ready=false,queued=null;
window.onYouTubeIframeAPIReady=()=>{
  yt=new YT.Player("yt",{host:"https://www.youtube-nocookie.com",width:"100%",height:"100%",playerVars:{origin:location.origin,playsinline:1,controls:0,disablekb:1,rel:0,iv_load_policy:3,fs:0,modestbranding:1},
    events:{onReady:()=>{ready=true;yt.setVolume(vol);yt.setLoop(true);if(queued){const q=queued;queued=null;q()}},onStateChange:onState,onError:onErr}});
};
let ytAsked=false;
let ytWarned=false;
function loadYT(){if(ytAsked)return;ytAsked=true;const s=document.createElement("script");s.src="https://www.youtube.com/iframe_api";s.async=true;
  // the autopilot below retries a failed load, so the warning shows only once
  s.onerror=()=>{s.remove();ytAsked=false;if(!ytWarned){ytWarned=true;toast("Can't reach YouTube yet. Retrying…")}};document.head.appendChild(s)}
// Get YouTube ready on the first touch or key press, so pressing play starts the music without waiting.
for(const ev of ["pointerdown","keydown"])addEventListener(ev,loadYT,{once:true,capture:true,passive:true});

// Each station plays as one looping YouTube playlist, in the station's shuffled order.
// YouTube moves from song to song by itself, so the browser never asks for another tap.
let list=[];
function play(i,k,start){
  const st=S[i];prep(st);on=i;playing=true;errs=0;pos=k;
  list=st._o.slice(k).concat(st._o.slice(0,k)).slice(0,200);cur=list[0];
  const ids=list.map(t=>st.tracks[t][3]);
  loadYT();lastOk=Date.now();
  const f=()=>{yt.loadPlaylist(ids,0,Math.max(0,Math.floor(start||0)));yt.setVolume(vol);yt.unMute()};
  ready?f():(queued=f);
  updateTune();updatePlayer();
}
function tune(i){const sp=live(S[i]);play(i,sp.k,sp.off)}
function playOnDemand(i,ti){
  if(sel!==i){sel=i;showStation()}
  prep(S[i]);play(i,S[i]._o.indexOf(ti),0);renderList();
}
function nextSong(){if(on<0||!ready)return;lastOk=Date.now();yt.nextVideo()}
// keep the song shown on screen in step with what YouTube is playing
function syncCur(){
  if(!ready||!list.length)return;
  const k=yt.getPlaylistIndex();
  if(k>=0&&k<list.length&&list[k]!==cur){cur=list[k];pos=S[on]._o.indexOf(cur);updatePlayer();if(view==="demand")renderList()}
}
function stop(){playing=false;clearTimeout(tuneTimer);if(ready)yt.pauseVideo();letSleep();updateTune();updatePlayer()}
function toggle(){if(playing&&on===sel)stop();else{staticBurst();tune(sel)}}
function onState(e){
  ytState=e.data;
  if(e.data!==2)syncCur();
  if(e.data===1){errs=0;hops=0;everPlayed=true;lastOk=Date.now();if(!playing){playing=true;updateTune()}updatePlayer();startWave();keepAwake()}
  else if(!raf)drawWave();
  // YouTube normally advances on its own. If it is still sitting at the end of a song, push it along.
  if(e.data===0&&playing)setTimeout(()=>{if(playing&&ytState===0){if(yt.getPlaylistIndex()>=list.length-1)yt.playVideoAt(0);else yt.nextVideo()}},1500);
  // Only the pause button stops the radio. Pauses from ads, hiccups or the browser are undone.
  if(e.data===2&&playing)setTimeout(()=>{if(playing&&ytState===2&&ready)yt.playVideo()},300);
}
// A song that won't play is skipped. If a whole station fails, hop to the next one.
function onErr(){
  if(!playing)return;
  if(++errs<=5){nextSong();return}
  if(++hops>=n){stop();toast("YouTube isn't playing anything right now. Press play to try again.");return}
  const from=S[on].name;sel=on;go(1);toast(`${from} isn't available, switched to ${S[sel].name}`);
}

/* ---------- autopilot: keeps the radio going without the listener touching anything ---------- */
let lastOk=0,lastT=-1,everPlayed=false,hops=0,lastHint=0;
setInterval(()=>{
  if(!playing)return;
  if(!ready){if(!ytAsked)loadYT();return}            // YouTube failed to load: retry
  const now=Date.now();
  if(ytState===1){const t=yt.getCurrentTime()||0;if(t!==lastT){lastT=t;lastOk=now}}
  if(document.hidden)return;                          // the browser paused us; picked up again on return
  const stuck=now-lastOk;
  if(stuck>4000&&ytState!==1&&ytState!==0)yt.playVideo();
  if(!everPlayed){                                   // the browser blocked the first play (mostly iPhone)
    if(stuck>5000&&now-lastHint>12000){lastHint=now;toast("Tap the video to start playback")}
  }else if(stuck>25000){lastOk=now;nextSong()}       // stuck song or stalled stream: move on
},2000);
function resume(){if(!playing)return;lastOk=Date.now();keepAwake();startWave();if(ready&&ytState!==1)yt.playVideo()}
document.addEventListener("visibilitychange",()=>{if(!document.hidden)resume()});
addEventListener("online",resume);
addEventListener("pageshow",e=>{if(e.persisted)resume()});

// Keep the screen on while the radio plays, so phones and car screens don't lock and cut the music.
let wl=null,wlBusy=false;
async function keepAwake(){
  if(wl||wlBusy||!navigator.wakeLock||document.hidden)return;
  wlBusy=true;try{wl=await navigator.wakeLock.request("screen");wl.addEventListener("release",()=>{wl=null})}catch(e){}wlBusy=false;
}
function letSleep(){try{if(wl)wl.release()}catch(e){}wl=null}

/* ---------- UI state ---------- */
const ICO={play:'<svg viewBox="0 0 24 24" fill="currentColor"><path d="M7 4.5v15L20 12z"/></svg>',pause:'<svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 4h4.5v16H6zM13.5 4H18v16h-4.5z"/></svg>',x:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.4" stroke-linecap="round"><path d="M6 6l12 12M18 6 6 18"/></svg>'};
function updateTune(){
  const live_=playing&&on===sel;
  $("tuneTxt").textContent=live_?"Radio Off":"Tune In";
  $("tuneIco").innerHTML=live_?ICO.x:ICO.play;
  $("tune").setAttribute("aria-label",live_?"Turn radio off":"Tune in to "+S[sel].name);
  $("pp").innerHTML=playing?ICO.pause:ICO.play;
  $("pp").setAttribute("aria-label",playing?"Pause":"Play");
  $("player").classList.toggle("off",!playing);
  $("onair").textContent=playing?"On Air":"Off Air";
}
function updatePlayer(){
  const st=S[on>=0?on:sel];
  $("pArt").innerHTML=logo(st);
  $("pName").textContent=st.name;
  $("pMeta").textContent=st.genre+" · "+st.place;
  const tr=on>=0&&cur>=0?S[on].tracks[cur]:null;
  $("pSong").textContent=tr?tr[0]+" – "+tr[1]:"Press play. Music streams from YouTube";
  document.title=playing&&tr?`${tr[1]} · ${st.name}`:"Vice City Radio";
  if(view==="demand")renderList();
}
$("tune").onclick=()=>{unlockAudio();toggle()};
$("pp").onclick=()=>{unlockAudio();if(playing)stop();else{staticBurst();tune(on>=0?on:sel)}};
$("skip").onclick=()=>{if(playing)nextSong()};
$("toStations").onclick=()=>{setView("radio");document.querySelector(".tuner").scrollIntoView({behavior:"smooth"})};
const volEl=$("vol");volEl.value=vol;volEl.style.setProperty("--v",vol+"%");
volEl.oninput=()=>{vol=+volEl.value;volEl.style.setProperty("--v",vol+"%");store.set("vol",vol);if(ready){yt.setVolume(vol);vol?yt.unMute():0}};

/* song progress */
setInterval(()=>{if(!ready||!playing||ytState!==1)return;const d=yt.getDuration()||0,t=yt.getCurrentTime()||0;$("prog").style.transform="scaleX("+(d?Math.min(1,t/d):0)+")"},1000);

/* ---------- static between stations (synthesised, no files) ---------- */
let ac=null;
function unlockAudio(){try{if(!ac){const C=window.AudioContext||window.webkitAudioContext;if(C)ac=new C()}if(ac&&ac.state==="suspended")ac.resume()}catch(e){}}
function staticBurst(){
  if(!ac||!vol)return;
  try{const len=ac.sampleRate*.38,b=ac.createBuffer(1,len,ac.sampleRate),d=b.getChannelData(0);for(let i=0;i<len;i++)d[i]=(Math.random()*2-1)*(1-i/len);
    const s=ac.createBufferSource(),f=ac.createBiquadFilter(),g=ac.createGain();f.type="bandpass";f.frequency.value=2200;f.Q.value=.6;g.gain.value=.12*vol/100;
    s.buffer=b;s.connect(f).connect(g).connect(ac.destination);s.start()}catch(e){}
}

/* ---------- wave (YouTube audio can't be analysed cross-origin, so it's animated) ---------- */
const cv=$("wave"),cx=cv.getContext("2d"),reduce=matchMedia("(prefers-reduced-motion:reduce)");let raf=0,ph=0;
let WG=null,lastW=0;
function drawWave(ts){
  const live_=playing&&ytState===1&&!reduce.matches;
  if(ts&&live_&&ts-lastW<33){raf=requestAnimationFrame(drawWave);return}
  lastW=ts||0;
  const dpr=Math.min(2,devicePixelRatio||1),w=cv.clientWidth,h=cv.clientHeight;
  if(!w){raf=0;return}
  if(cv.width!==Math.round(w*dpr)){cv.width=Math.round(w*dpr);cv.height=Math.round(h*dpr);WG=null}
  cx.setTransform(dpr,0,0,dpr,0,0);cx.clearRect(0,0,w,h);
  if(!WG){WG=cx.createLinearGradient(0,0,w,0);WG.addColorStop(0,"#ff8cc6");WG.addColorStop(1,"#c88bff")}
  cx.fillStyle=WG;
  const step=mq.matches?4:6,N=Math.floor(w/step);ph+=.14;
  for(let i=0;i<N;i++){
    const e=live_?(.25+.75*Math.abs(Math.sin(i*.55+ph)*Math.sin(i*.21-ph*1.7)*Math.cos(i*.09+ph*.6))):.12;
    const bh=Math.max(2,e*h);cx.fillRect(i*step,(h-bh)/2,2,bh);
  }
  raf=live_&&!document.hidden?requestAnimationFrame(drawWave):0;
}
function startWave(){if(!raf)raf=requestAnimationFrame(drawWave)}

/* ---------- input: keyboard + gamepad ---------- */
function flash(id){const b=$(id);b.classList.add("hit");setTimeout(()=>b.classList.remove("hit"),140)}
addEventListener("keydown",e=>{
  if(e.target.matches("input")||e.metaKey||e.ctrlKey||e.altKey)return;
  const k=e.key.toLowerCase();
  if(k==="arrowleft"||k==="q"||k===","){go(-1);flash("prev");e.preventDefault()}
  else if(k==="arrowright"||k==="e"||k==="."){go(1);flash("next");e.preventDefault()}
  else if(k===" "&&!e.target.closest("button")){unlockAudio();toggle();e.preventDefault()}
});
let gpRaf=0,gpPrev=[];
function poll(){const p=[...(navigator.getGamepads?navigator.getGamepads():[])].find(Boolean);if(!p){gpRaf=0;return}
  const b=p.buttons.map(x=>x.pressed);
  if(b[4]&&!gpPrev[4]){go(-1);flash("prev")}if(b[5]&&!gpPrev[5]){go(1);flash("next")}if(b[0]&&!gpPrev[0]){unlockAudio();toggle()}
  gpPrev=b;gpRaf=requestAnimationFrame(poll)}
addEventListener("gamepadconnected",()=>{if(!gpRaf)gpRaf=requestAnimationFrame(poll)});

/* ---------- misc ---------- */
let tt=0;function toast(m){const t=$("toast");t.textContent=m;t.classList.add("show");clearTimeout(tt);tt=setTimeout(()=>t.classList.remove("show"),4200)}
function sizePlayer(){document.documentElement.style.setProperty("--pb",mq.matches?($("player").offsetHeight+12)+"px":"0px")}
let rz=0;addEventListener("resize",()=>{cancelAnimationFrame(rz);rz=requestAnimationFrame(()=>{M=null;layout();sizePlayer();WG=null;drawWave()})});

if(!n){$("stName").textContent="No stations loaded";return}
showStation();updatePlayer();updateTune();sizePlayer();drawWave();
if(document.fonts)document.fonts.ready.then(()=>{M=null;layout();sizePlayer()});
})();
