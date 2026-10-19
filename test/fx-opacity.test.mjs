// SPDX-License-Identifier: MIT
import test from 'node:test';import assert from 'node:assert/strict';import * as T from 'three';
import {FLIPBOOKS,makeSmokePuff,makeGroundGlow,makeFlameCluster,radialGlowTexture} from '../assets/hybrid-3d/fx-flipbook.mjs';
const texture=()=>new T.DataTexture(new Uint8Array(16),2,2);
test('smoke and ground glow preserve clamped opacity during absolute updates',()=>{
 for(const opacity of [-4,4]){
  const s=makeSmokePuff(T,{texture:texture(),spec:FLIPBOOKS.smoke01,opacity});s.update(1,1,.5);assert.ok(s.mesh.material.opacity>=0&&s.mesh.material.opacity<=1);
  const g=makeGroundGlow(T,{texture:radialGlowTexture(T),opacity});g.update(1,1);assert.ok(g.mesh.material.opacity>=0&&g.mesh.material.opacity<=1);
 }
});
test('cluster passes an authored tint to each independently cloned material',()=>{
 const c=makeFlameCluster(T,{texture:texture(),tint:'#f08030'});for(const s of c.sprites)assert.equal(s.material.color.getHexString(),'f08030');
});
