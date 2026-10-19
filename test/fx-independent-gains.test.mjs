// SPDX-License-Identifier: MIT
import test from 'node:test';import assert from 'node:assert/strict';import * as T from 'three';
import {makeFlameCluster} from '../assets/hybrid-3d/fx-flipbook.mjs';
test('sprite gain and point light gain are independent in both directions',()=>{
 const texture=new T.DataTexture(new Uint8Array(16),2,2);
 const make=(gain,lightGain)=>{const f=makeFlameCluster(T,{texture,gain,lightGain});f.update(1,.8);return f;};
 const a=make(.2,3),b=make(.8,3),c=make(.2,6);
 assert.equal(a.lamp.intensity,b.lamp.intensity);assert.notEqual(a.sprites[0].material.opacity,b.sprites[0].material.opacity);
 assert.equal(a.sprites[0].material.opacity,c.sprites[0].material.opacity);assert.equal(c.lamp.intensity/a.lamp.intensity,2);
});
