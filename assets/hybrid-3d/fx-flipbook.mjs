// SPDX-License-Identifier: MIT
// Original time-driven Three.js helpers; texture rights are separately CC0-1.0.
// This is billboard compositing, not volumetric fire or recorded live-action footage.
export const FLIPBOOKS = Object.freeze({
  flame02: Object.freeze({cols:16, rows:4, frames:64, fps:24, file:'Flame02_16x4.png', cell:[128,256]}),
  flame03: Object.freeze({cols:16, rows:4, frames:64, fps:26, file:'Flame03_16x4.png', cell:[64,128]}),
  smoke01: Object.freeze({cols:8, rows:8, frames:64, fps:20, file:'WispySmoke01_8x8.png', cell:[128,128]}),
  smoke02: Object.freeze({cols:8, rows:8, frames:64, fps:20, file:'WispySmoke02_8x8.png', cell:[128,128]}),
});
function finite(n, name) { if (!Number.isFinite(n)) throw new TypeError(`${name} must be finite`); return n; }
function positive(n, name) { finite(n,name); if (n<=0) throw new RangeError(`${name} must be positive`); return n; }
const unit = n => Math.max(0,Math.min(1,finite(n,'progress')));
function validSpec(s) {
  if (!s || !['cols','rows','frames'].every(k=>Number.isSafeInteger(s[k])&&s[k]>0) || s.frames>s.cols*s.rows) throw new RangeError('Invalid flipbook grid');
  positive(s.fps,'fps'); return s;
}
export function cellUV(spec, frame) {
  validSpec(spec); finite(frame,'frame');
  const f=((Math.floor(frame)%spec.frames)+spec.frames)%spec.frames;
  return {x:(f%spec.cols)/spec.cols, y:1-(Math.floor(f/spec.cols)+1)/spec.rows};
}
export function makeFlipbookMaterial(T, texture, spec, {tint='#ffffff', blending=T.AdditiveBlending}={}) {
  validSpec(spec);
  const map=texture.clone(); map.wrapS=map.wrapT=T.ClampToEdgeWrapping;
  // Mipmap levels of a shared atlas bleed neighbouring cells. Use linear sampling
  // and a half-texel inset when the decoded texture dimensions are available.
  const width=texture.image?.width, height=texture.image?.height;
  const inset={x:width?0.5/width:0, y:height?0.5/height:0};
  map.repeat.set(1/spec.cols-2*inset.x,1/spec.rows-2*inset.y);
  map.generateMipmaps=false; map.minFilter=T.LinearFilter; map.magFilter=T.LinearFilter; map.needsUpdate=true;
  const mat=new T.MeshBasicMaterial({map,color:tint,transparent:true,depthWrite:false,blending,side:T.DoubleSide,toneMapped:false});
  mat.userData.flipbookInset=inset; return mat;
}
export function makeFlipbookSprite(T,{texture,spec,x=0,y=0,z=0,w=1,h=1,facing=0,tint,opacity=1,phase=0,speed=1,loop=true,blending}={}) {
  [x,y,z,facing,phase,speed,opacity].forEach(n=>finite(n,'sprite parameter')); positive(w,'width'); positive(h,'height');
  const material=makeFlipbookMaterial(T,texture,spec,{tint,blending}); material.opacity=unit(opacity);
  const mesh=new T.Mesh(new T.PlaneGeometry(w,h),material); mesh.position.set(x,y,z); mesh.rotation.y=facing;
  Object.assign(mesh.userData,{spec,phase,speed,loop,baseOpacity:material.opacity,frame:0}); advanceFlipbook(mesh,0); return mesh;
}
export function advanceFlipbook(sprite,t,progress=null) {
  finite(t,'time'); const {spec,phase,speed,loop}=sprite.userData;
  const raw=Math.floor((t*speed+phase)*spec.fps);
  const frame=loop?((raw%spec.frames)+spec.frames)%spec.frames:progress===null?Math.max(0,Math.min(spec.frames-1,raw)):Math.min(spec.frames-1,Math.floor(unit(progress)*spec.frames));
  const uv=cellUV(spec,frame), inset=sprite.material.userData.flipbookInset;
  // Always write offsets: callers may restore materials during deterministic seeking.
  sprite.material.map.offset.set(uv.x+inset.x,uv.y+inset.y); sprite.userData.frame=frame; return frame;
}
export function radialGlowTexture(T,{size=128}={}) {
  if (!Number.isSafeInteger(size)||size<2) throw new RangeError('Glow size must be an integer >=2');
  // DataTexture avoids a DOM dependency and works in Node tests as well as browsers.
  const rgba=new Uint8Array(size*size*4);
  for(let y=0;y<size;y++) for(let x=0;x<size;x++) {
    const a=Math.max(0,1-Math.hypot((x+.5)/size*2-1,(y+.5)/size*2-1))**2, i=(y*size+x)*4;
    rgba[i]=255; rgba[i+1]=154; rgba[i+2]=65; rgba[i+3]=Math.round(255*a);
  }
  const tex=new T.DataTexture(rgba,size,size,T.RGBAFormat); tex.colorSpace=T.SRGBColorSpace; tex.needsUpdate=true; return tex;
}
export function makeGroundGlow(T,{texture,x=0,z=0,radius=1.6,y=.02,opacity=.55}={}) {
  positive(radius,'radius'); [x,y,z].forEach(n=>finite(n,'glow position')); opacity=unit(opacity);
  const material=new T.MeshBasicMaterial({map:texture,color:'#ffbc85',transparent:true,depthWrite:false,blending:T.AdditiveBlending,opacity,toneMapped:false});
  const mesh=new T.Mesh(new T.PlaneGeometry(radius*2,radius*2),material); mesh.rotation.x=-Math.PI/2; mesh.position.set(x,y,z);
  return {mesh,update(t,heat=1){finite(t,'time');const h=unit(heat);material.opacity=opacity*h*(.85+.15*Math.sin(t*11.3+x*7.1));mesh.visible=h>.02;}};
}
export function makeFlameCluster(T,{texture,spec=FLIPBOOKS.flame02,x=0,y=0,z=0,scale=1,facing=0,tint='#ffffff',seed=0,layers=3,gain=.4,lightGain=3,light=true,glowTexture=null,glowRadius=1.7}={}) {
  positive(scale,'scale'); [x,y,z,facing,seed,gain,lightGain].forEach(n=>finite(n,'cluster parameter'));
  if(gain<0||lightGain<0||!Number.isSafeInteger(layers)||layers<1||layers>16) throw new RangeError('Invalid gain or layer count');
  const root=new T.Group(); root.position.set(x,y,z);
  const random=i=>{const n=Math.sin((seed+1)*91.7+i*47.3)*43758.5453;return n-Math.floor(n);};
  const sprites=[];
  for(let i=0;i<layers;i++) {
    const r=random(i),q=random(i+11),w=scale*(.7+r*.35),h=scale*(1.2+q*.65);
    const sprite=makeFlipbookSprite(T,{texture,spec,x:(r-.5)*scale*.4,y:h/2,z:(q-.5)*scale*.3,w,h,facing,tint,opacity:Math.min(1,gain*(i? .62:1)),phase:r*3.7+i*.31,speed:.82+q*.5});
    sprite.userData.baseHeight=h; sprites.push(sprite); root.add(sprite);
  }
  const lamp=light?new T.PointLight('#ff8a30',0,scale*9,2):null;
  if(lamp){lamp.position.set(0,scale*1.3,scale*.42);root.add(lamp);}
  // Glow is owned by the cluster, in local coordinates, not an unattached object.
  const glow=glowTexture?makeGroundGlow(T,{texture:glowTexture,radius:glowRadius*scale}):null;
  if(glow)root.add(glow.mesh);
  return {root,sprites,lamp,glow,update(t,heat=1){
    finite(t,'time');const h=unit(heat);root.visible=h>.02;
    for(const sprite of sprites){advanceFlipbook(sprite,t);sprite.material.opacity=sprite.userData.baseOpacity*h;sprite.scale.set(.78+.22*h,.32+.68*h,1);sprite.position.y=sprite.userData.baseHeight*sprite.scale.y/2;}
    if(lamp)lamp.intensity=12*h*scale*lightGain;
    if(glow)glow.update(t,h);
  }};
}
export function makeSmokePuff(T,{texture,spec=FLIPBOOKS.smoke01,x=0,y=0,z=0,scale=1,facing=0,tint='#aeb7bd',opacity=.5,rise=2.4,drift=.5,seed=0}={}) {
  positive(scale,'scale');[x,y,z,rise,drift,seed].forEach(n=>finite(n,'smoke parameter'));opacity=unit(opacity);
  const mesh=makeFlipbookSprite(T,{texture,spec,x,y,z,w:scale,h:scale,facing,tint,opacity,loop:false,blending:T.NormalBlending});
  return {mesh,update(t,alive=1,age=0){
    finite(t,'time');const p=unit(age);advanceFlipbook(mesh,t,p);
    mesh.position.set(x+drift*Math.sin(p*2.4+seed)*p,y+rise*p,z);
    // Geometry already contains scale: do not square it in the transform.
    mesh.scale.setScalar(.55+1.05*p);mesh.material.opacity=opacity*unit(alive)*Math.sin(Math.PI*p)**.6;mesh.visible=mesh.material.opacity>.004;
  }};
}
export function loadFlipbookTexture(T,loader,url) {
  return new Promise((resolve,reject)=>loader.load(url,tex=>{tex.colorSpace=T.SRGBColorSpace;tex.generateMipmaps=false;tex.minFilter=T.LinearFilter;tex.magFilter=T.LinearFilter;resolve(tex);},undefined,reject));
}
