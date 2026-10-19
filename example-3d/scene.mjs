// SPDX-License-Identifier: MIT
import * as T from '../node_modules/three/build/three.module.js';
import {animalKit} from '../assets/hybrid-3d/animals.mjs';
import {fitFixedShot,visibleBounds,boxCorners} from '../assets/hybrid-3d/fixed-shot.mjs';
import {actorKit} from '../assets/narrative-3d/actors.mjs';
import {setKit} from '../assets/narrative-3d/sets.mjs';
import {FLIPBOOKS,loadFlipbookTexture,makeFlameCluster,makeSmokePuff,radialGlowTexture} from '../assets/hybrid-3d/fx-flipbook.mjs';
const clamp=n=>Math.max(0,Math.min(1,n));
async function main(){
 const renderer=new T.WebGLRenderer({canvas:document.querySelector('#stage'),antialias:false,alpha:true,preserveDrawingBuffer:true});
 renderer.setPixelRatio(1);renderer.setSize(1280,450,false);renderer.shadowMap.enabled=false;
 renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.NoToneMapping;
 const scene=new T.Scene();scene.add(new T.HemisphereLight('#e8f0fa','#28323c',2.0));
 const sun=new T.DirectionalLight('#ffffff',2.5);sun.position.set(-3,8,9);scene.add(sun);
 const floor=new T.Mesh(new T.PlaneGeometry(30,20),new T.MeshLambertMaterial({color:'#253745'}));floor.rotation.x=-Math.PI/2;floor.position.y=-.025;scene.add(floor);
 const groups=Array.from({length:3},()=>new T.Group());groups.forEach(g=>scene.add(g));
 const animal=animalKit(T),lion=animal.lion({scale:.94}),fox=animal.fox({scale:.76}),wolves=[animal.wolf({scale:.76}),animal.wolf({scale:.70})];
 const beasts=[lion,fox,...wolves];beasts.forEach(b=>groups[0].add(b.root));
 function blob(parent,rx,rz){const m=new T.Mesh(new T.CircleGeometry(1,32),new T.MeshBasicMaterial({color:'#080d13',transparent:true,opacity:.40,depthWrite:false}));m.rotation.x=-Math.PI/2;m.scale.set(rx,rz,1);m.position.y=-.012;m.userData.decorative=true;parent.add(m);return m;}
 const animalShadows=beasts.map((b,i)=>blob(groups[0],i===0?1.0:.65,i===0?.33:.20));
 const textures=Object.fromEntries(await Promise.all(Object.entries(FLIPBOOKS).map(async([id,s])=>[id,await loadFlipbookTexture(T,new T.TextureLoader(),new URL('../assets/hybrid-3d/textures/'+s.file,import.meta.url).href)])));
 const sets=setKit(T),house=sets.house();house.position.set(-.15,0,-.12);groups[1].add(house);
 const facing=Math.atan2(7,12),glowTexture=radialGlowTexture(T);
 const fires=[makeFlameCluster(T,{texture:textures.flame02,spec:FLIPBOOKS.flame02,x:1.12,z:1.15,scale:1.12,facing,gain:.68,lightGain:.45,glowTexture}),makeFlameCluster(T,{texture:textures.flame03,spec:FLIPBOOKS.flame03,x:.65,z:1.00,scale:.75,facing,seed:4,layers:2,gain:.52,lightGain:.45,glowTexture})];
 fires.forEach(f=>groups[1].add(f.root));
 const smoke=[makeSmokePuff(T,{texture:textures.smoke01,spec:FLIPBOOKS.smoke01,x:.9,y:1.1,z:1.0,scale:1.3,facing,opacity:.30,rise:1.9}),makeSmokePuff(T,{texture:textures.smoke02,spec:FLIPBOOKS.smoke02,x:.8,y:1.2,z:.9,scale:1.1,facing,opacity:.26,rise:1.7,seed:1})];
 smoke.forEach(s=>groups[1].add(s.mesh));
 const people=actorKit(T),ruler=people.actor({role:'ruler',color:'#4d8c9b'}),courtier=people.actor({color:'#ce926a'});
 groups[2].add(ruler.root,courtier.root);ruler.root.position.set(-1.8,0,0);ruler.root.rotation.y=Math.PI/2;
 const rulerShadow=blob(groups[2],.3,.2),courtierShadow=blob(groups[2],.3,.2);rulerShadow.position.set(-1.8,-.012,0);
 const titles=['Lion, fox and two wolves','Fire and smoke: bundled CC0 atlases','People and a readable departure'];
 const captions=['Distinct mesh silhouettes. Absolute-time gait, not motion capture.','Two fire emitters, two smoke atlases and separate light / sprite gain.','Fixed camera. The figure turns, then walks out of the interaction.'];
 const updates=[
  t=>{const q=clamp(t/4);beasts.forEach((b,i)=>{b.root.position.set(-2.1+q*2.8-(i===3?.55:0),0,[-1.6,.05,1.55,2.35][i]);b.pose({phase:t*7+i,stride:.8,turn:0});animalShadows[i].position.set(b.root.position.x,-.012,b.root.position.z);});},
  t=>{const q=clamp((t-4)/4);fires.forEach((f,i)=>f.update(t+i*.7,.7+.3*q));smoke.forEach((s,i)=>s.update(t,1,((q*.87+i*.23)%1)));},
  t=>{const q=clamp((t-8)/4),walk=clamp((q-.22)/.72);ruler.pose();courtier.root.position.set(-.65+walk*3.3,0,.2);courtierShadow.position.set(courtier.root.position.x,-.012,.2);courtier.root.rotation.y=-Math.PI/2+Math.PI*clamp(q/.25);courtier.pose({walk:walk>0?1:0,phase:t*7,bow:(1-clamp(q/.2))*.5});},
 ];
 const shots=groups.map((root,i)=>({start:i*4,end:(i+1)*4,root,
  foci:(i===0?beasts.map(b=>b.root):i===1?[house,...fires.map(f=>f.root),...smoke.map(s=>s.mesh)]:[ruler.root,courtier.root]).map((r,n)=>({id:`object-${i}-${n}`,root:r})),
  reset(){root.visible=true;},update(t){root.visible=true;updates[i](t);}}));
 const fits=shots.map(s=>fitFixedShot(T,s,{view:{w:1280,h:450},step:.16,padding:1.14,direction:[7,4,12]}));
 const cameras=fits.map(f=>f.camera),signatures=cameras.map(c=>JSON.stringify([c.matrixWorld.toArray(),c.projectionMatrix.toArray()]));
 window.renderAt=t=>{if(!Number.isFinite(t)||t<0||t>=12)throw Error('time outside [0,12)');const i=Math.floor(t/4);groups.forEach((g,n)=>g.visible=n===i);shots[i].update(t);document.querySelector('#title').textContent=titles[i];document.querySelector('#caption').textContent=captions[i];renderer.render(scene,cameras[i]);const signature=JSON.stringify([cameras[i].matrixWorld.toArray(),cameras[i].projectionMatrix.toArray()]);if(signature!==signatures[i])throw Error('camera drift');let visibleFoci=0;const framingFailures=[];for(const f of shots[i].foci){const b=visibleBounds(T,f.root);if(b.isEmpty())continue;visibleFoci++;for(const corner of boxCorners(T,b)){const p=corner.project(cameras[i]);if(Math.abs(p.x)>1.00001||Math.abs(p.y)>1.00001||Math.abs(p.z)>1.00001){framingFailures.push(f.id);break;}}}if(framingFailures.length)throw Error('focal framing failure: '+framingFailures.join(','));return {shot:i,time:t,camera:signature,textureCount:Object.keys(textures).length,visibleFoci,framingFailures};};
 window.inspectLabels=()=>{const nodes=['#kicker','#title','#caption','#footer'].map(s=>{const r=document.querySelector(s).getBoundingClientRect();return {selector:s,x:r.x,y:r.y,w:r.width,h:r.height};});const clipped=nodes.filter(r=>r.x<0||r.y<0||r.x+r.w>1280||r.y+r.h>720);const overlaps=[];for(let i=0;i<nodes.length;i++)for(let j=i+1;j<nodes.length;j++){const a=nodes[i],b=nodes[j];if(a.x<b.x+b.w&&a.x+a.w>b.x&&a.y<b.y+b.h&&a.y+a.h>b.y)overlaps.push([a.selector,b.selector]);}return {nodes,clipped,overlaps};};
 window.cameraReports=fits.map(f=>f.report);window.renderAt(0);return {three:T.REVISION,textures:Object.keys(textures).length,shots:shots.length};
}
window.assetReady=main();
