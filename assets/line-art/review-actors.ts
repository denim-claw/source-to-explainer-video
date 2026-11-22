// Adapted from MIT JDhruv14 line-art-animation + approved Pillow hybrid proof.
// Only illustrative roles; no human agency or unmeasured model outcome asserted.
import {el,pen,shape,paint,blot,limb,joint,place,inkDefs,PAPER} from './lib/ink.ts';
import {spring} from './lib/motion.ts';
import T from './review-tokens.json';
const svg=el('svg',{viewBox:'0 0 720 410',width:720,height:410},document.body);
svg.style.cssText=`color:${T.ink};--paper:${T.paper};background:transparent`;
inkDefs(svg); el('style',{},svg).textContent='.pp{fill:var(--paper)}'; const layout=el('g',{'data-layer':'layout'},svg);
// Immutable spring lookup. renderAt never mutates/integrates physics.
const s=spring(50,12);const bake:number[]=[];
for(let k=0;k<=1800;k++)bake.push(s.step(k/60>=.4?1:0,1/60));
function actor(x:number,foot:number,dir:1|-1,role:string,scale:number,hand:[number,number],look:number,col:string){
 const slot=el('g',{'data-slot':role},layout);
 const g=el('g',{'data-motion':role,'data-role':role},slot);place(g,x,foot,dir,scale);
 const path=(p:Element,d:string,w=1)=>{const e=pen(p,w);e.setAttribute('d',d);return e};
 const l=limb(g,5),r=limb(g,5);l.draw([[38,77],[35,99],[34,119]]);r.draw([[44,77],[46,97],[48,119]]);
 blot(g).setAttribute('d','M30 119q6 -3 12 0l2 3H29Z M45 119q7 -3 12 0l2 3H44Z');
 const back=limb(g,4);back.draw([[37,46],joint([37,46],[45,82],18,19,-1),[45,82]]);
 paint(g,col).setAttribute('d','M34 43Q40 40 47 44L49 78Q40 81 30 78L33 59Z');path(g,'M40 47q2 13 0 29 M34 59l5 2',.65);
 path(g,'M39 40l0 4 M44 40l0 4');
 const head=el('g',{transform:`rotate(${look} 41 42)`},g);
 shape(head,1).setAttribute('d','M36 28Q40 22 46 27L47 32L50 34L47 36Q47 42 41 41Q35 40 35 35Z');
 blot(head).setAttribute('d',role.includes('worker')?'M35 33Q30 24 38 22Q47 20 48 28L44 27L40 30L36 29Z':'M34 34Q29 21 40 21Q48 21 48 28L43 28L40 26L36 30L36 35Z');
 if(!role.includes('worker'))path(head,'M42 32h5v3h-5z M41 33h-3',.55);
 path(head,'M45 37l1 0',.6);
 const arm=limb(g,4);arm.draw([[46,47],joint([46,47],hand,19,21,1),hand],[.1,.1]);
 paint(g,T.accent,.7).setAttribute('d',`M${hand[0]-2} ${hand[1]-2}l4 0l0 3l-4 0Z`);
 el('ellipse',{cx:hand[0],cy:hand[1],rx:1.7,ry:1.5,fill:PAPER,stroke:'currentColor','stroke-width':.65},g);
}
const split=T.a08_duration;
async function renderAt(t:number){
 layout.replaceChildren();const scene=t<split?'A08':'A09';const local=t<split?t:t-split;
 const springAt=(since:number)=>bake[Math.max(0,Math.min(1800,Math.round(since*60)))];
 if(scene==='A08'){
  const second=local>=T.a08_second;const progress=springAt(second?local-T.a08_second:local);
  // Worker reads log first; main gestures toward its own code in second utterance.
  actor(100,370,1,'worker',2.15,[62,second?76:75-13*progress],second?-3:13,T.worker_fill);
  actor(620,370,-1,'lead',2.15,[62,second?75-13*progress:77],second?12:0,T.lead_fill);
 }else{
  actor(174,184,1,'solo',1.4,[52,78],0,T.lead_fill);
  const active=local>=T.a09_worker;
  const p=springAt(local-T.a09_worker);
  actor(510,184,-1,'lead',1.4,[55+7*(active?p:0),75-14*(active?p:0)],active?8:0,T.lead_fill);
  if(active)for(const [i,x] of [410,510,610].entries()){
   const q=springAt(local-T.a09_worker-i*.25);
   actor(x,326,i===2?-1:1,`worker-${i}`,0.90,[55+5*q,75-10*q],q*8,T.worker_fill);
  }
 }
 // Rasterize a fresh self-contained SVG image per sample. DOM equality alone did
 // not imply pixel equality in Chromium (history-dependent subpixel edge cache).
 const image=new Image(720,410);
 image.src='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(new XMLSerializer().serializeToString(svg));
 await image.decode();document.body.replaceChildren(image);
}
(window as any).__svg=()=>svg.outerHTML;
(window as any).__render=renderAt;let current=0;
(window as any).__step=(dt=1/30)=>{current+=dt;renderAt(current);return current};
renderAt(0);
