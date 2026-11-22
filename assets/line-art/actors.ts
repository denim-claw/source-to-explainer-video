import {el,pen,shape,paint,blot,limb,joint,place,inkDefs,PAPER} from './lib/ink.ts';
import {spring,minJerk,clamp} from './lib/motion.ts';
import T from './tokens.json';
const svg=el('svg',{viewBox:'0 350 720 650',width:720,height:650},document.body);
svg.style.cssText=`color:${T.ink};--paper:${T.paper};background:transparent`;
inkDefs(svg);const stage=el('g',{},svg);const C=[T.teal,T.ochre];
function path(p:Element,d:string,w=2,color='currentColor'){const e=pen(p,w);e.setAttribute('d',d);e.setAttribute('stroke',color);return e;}
function actor(x:number,dir:1|-1,idx:number,hand:[number,number],look:number,other:[number,number]=[45,82]){
 const g=el('g',{'data-actor':idx},stage);place(g,x,930,dir,3.4);
 const leg1=limb(g,5),leg2=limb(g,5);leg1.draw([[38,77],[35,99],[34,119]]);leg2.draw([[44,77],[46,97],[48,119]]);
 const shoes=blot(g);shoes.setAttribute('d','M30 119q6 -3 12 0l2 3H29Z M45 119q7 -3 12 0l2 3H44Z');
 const back=limb(g,4);back.draw([[37,46],joint([37,46],other,18,19,-1),other]);
 const coat=paint(g,idx===0?'#e1e9e3':'#eee0d3');coat.setAttribute('d','M34 43Q40 40 47 44L49 78Q40 81 30 78L33 59Z');path(g,'M40 47q2 13 0 29 M34 59l5 2',.65);
 path(g,'M39 40l0 4 M44 40l0 4',1);
 const head=el('g',{transform:`rotate(${look} 41 42)`},g);
 const face=shape(head,1);face.setAttribute('d','M36 28Q40 22 46 27L47 32L50 34L47 36Q47 42 41 41Q35 40 35 35Z');
 const hair=blot(head);hair.setAttribute('d',idx===0?'M34 34Q29 21 40 21Q48 21 48 28L43 28L40 26L36 30L36 35Z':'M35 33Q30 24 38 22Q47 20 48 28L44 27L40 30L36 29Z M33 27Q25 22 29 18Q37 16 36 24Z');
 if(idx===0)path(head,'M42 32h5v3h-5z M41 33h-3',.55);
 path(head,'M45 37l1 0',.6);
 const arm=limb(g,4);arm.draw([[46,47],joint([46,47],hand,19,21,1),hand],[.1,.1]);
 const cuff=paint(g,C[idx],.7);cuff.setAttribute('d',`M${hand[0]-2} ${hand[1]-2}l4 0l0 3l-4 0Z`);
 el('ellipse',{cx:hand[0],cy:hand[1],rx:1.7,ry:1.5,fill:PAPER,stroke:'currentColor','stroke-width':.65},g);
 return [x+dir*3.4*(hand[0]-40),930+3.4*(hand[1]-120)];
}

// Bake original spring at 60 Hz; renderAt never integrates.
const sp=[spring(50,12),spring(50,12)];const baked:number[][]=[];
for(let k=0;k<=720;k++){let t=k/60;baked.push(sp.map((s,i)=>s.step(t>=2.3+i*.45&&t<4.1?1:0,1/60)));}
function render(t:number){stage.replaceChildren();const b=baked[Math.min(720,Math.max(0,Math.round(t*60)))];
let h0:[number,number]=[58,73],h1:[number,number]=[58,73];
if(t<2.3){let p=minJerk(clamp(t/1.2,0,1));h0=[54+4*p,82-9*p];h1=[54+4*p,82-9*p];}
else if(t<4.1){h0=[55+7*b[0],72-17*b[0]];h1=[55+7*b[1],72-17*b[1]];}
else {h0=[64,73];h1=[64,73];}
actor(158,1,0,h0,t<2.3?15:-8*b[0]);actor(562,-1,1,h1,t<2.3?15:-8*b[1]);
}
(window as any).__render=render;let current=0;(window as any).__step=(dt=1/30)=>{current+=dt;render(current);return current};render(0);
