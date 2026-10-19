// SPDX-License-Identifier: MIT
import test from 'node:test';
import assert from 'node:assert/strict';
import * as T from 'three';
import {FLIPBOOKS,cellUV,makeFlipbookSprite,advanceFlipbook,makeFlameCluster,makeSmokePuff,radialGlowTexture} from '../assets/hybrid-3d/fx-flipbook.mjs';
const texture = () => new T.DataTexture(new Uint8Array(1024*512*4),1024,512);
const state = root => {root.updateMatrixWorld(true);const a=[];root.traverse(o=>a.push([o.name,o.visible,o.matrixWorld.toArray(),o.material?.opacity,o.material?.map?.offset.toArray()]));return JSON.stringify(a);};
test('UV top row, last row, negative and wrapped frame',()=>{
 const s=FLIPBOOKS.flame03;
 assert.deepEqual(cellUV(s,0),{x:0,y:.75});assert.deepEqual(cellUV(s,63),{x:.9375,y:0});
 assert.deepEqual(cellUV(s,64),cellUV(s,0));assert.deepEqual(cellUV(s,-1),cellUV(s,63));
 assert.throws(()=>cellUV({...s,frames:65},0));assert.throws(()=>cellUV(s,NaN));
});
test('emitters own map offsets, frame rewrite survives external reset, no atlas mipmap bleed',()=>{
 const source=texture(),a=makeFlipbookSprite(T,{texture:source,spec:FLIPBOOKS.flame03}),b=makeFlipbookSprite(T,{texture:source,spec:FLIPBOOKS.flame03});
 assert.notEqual(a.material.map,b.material.map);advanceFlipbook(a,1.2);const wanted=a.material.map.offset.toArray();
 assert.notDeepEqual(wanted,b.material.map.offset.toArray());a.material.map.offset.set(0,0);advanceFlipbook(a,1.2);assert.deepEqual(a.material.map.offset.toArray(),wanted);
 assert.equal(a.material.map.generateMipmaps,false);assert.ok(a.material.map.repeat.x<1/16);
});
test('fire absolute seeking resets heat/scale/light/glow, glow is attached',()=>{
 const f=makeFlameCluster(T,{texture:texture(),spec:FLIPBOOKS.flame03,x:3,z:2,scale:.7,glowTexture:radialGlowTexture(T)});
 assert.equal(f.glow.mesh.parent,f.root);assert.equal(f.glow.mesh.position.x,0);
 f.update(1.6,.8);const a=state(f.root);f.update(8,0);f.update(.1,1);f.update(1.6,.8);assert.equal(state(f.root),a);
 for(const s of f.sprites)assert.ok(Math.abs(s.position.y-s.userData.baseHeight*s.scale.y/2)<1e-12);
 const intensity=f.lamp.intensity;const g=makeFlameCluster(T,{texture:texture(),spec:FLIPBOOKS.flame03,scale:.7,lightGain:6});g.update(1.6,.8);assert.ok(Math.abs(g.lamp.intensity/intensity-2)<1e-12);
 assert.throws(()=>f.update(NaN,1));assert.throws(()=>makeFlameCluster(T,{texture:texture(),layers:0}));
});
test('smoke applies requested scale once, finite endpoints and deterministic seeking',()=>{
 const a=makeSmokePuff(T,{texture:texture(),spec:FLIPBOOKS.smoke01,scale:1}),b=makeSmokePuff(T,{texture:texture(),spec:FLIPBOOKS.smoke01,scale:2});
 a.update(1,1,.5);b.update(1,1,.5);const wa=new T.Box3().setFromObject(a.mesh).getSize(new T.Vector3()).x,wb=new T.Box3().setFromObject(b.mesh).getSize(new T.Vector3()).x;assert.ok(Math.abs(wb/wa-2)<1e-10);
 const before=state(a.mesh);a.update(9,0,1);a.update(1,1,.5);assert.equal(state(a.mesh),before);
 for(const age of [0,1]){a.update(2,1,age);assert.ok(Number.isFinite(a.mesh.material.opacity));}
 assert.equal(b.mesh.material.blending,T.NormalBlending);
});
