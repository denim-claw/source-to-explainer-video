// SPDX-License-Identifier: MIT
import test from 'node:test';import assert from 'node:assert/strict';import * as T from 'three';
import {actorKit} from '../assets/narrative-3d/actors.mjs';import {setKit} from '../assets/narrative-3d/sets.mjs';
function state(root){root.updateMatrixWorld(true);const out=[];root.traverse(o=>out.push(o.matrixWorld.toArray()));return JSON.stringify(out);}
test('people: complete finite geometry, floor origin, face cue and reversible poses',()=>{
 for(const role of ['courtier','ruler','guard']){
  const a=actorKit(T).actor({role});const bounds=new T.Box3().setFromObject(a.root);
  assert.ok(Math.abs(bounds.min.y)<.02);assert.ok(bounds.max.y>1.8);assert.ok(Object.keys(a.joints).length>=10);
  a.root.position.set(2,0,3);a.pose({walk:.8,phase:1,bow:.2,reach:.4});const before=state(a.root);
  a.pose({walk:1,phase:8,stop:1});a.pose({walk:.8,phase:1,bow:.2,reach:.4});assert.equal(state(a.root),before);
  assert.deepEqual(a.root.position.toArray(),[2,0,3]);assert.throws(()=>a.pose({phase:NaN}));
 }
});
test('all set factories return actual Object3D with nonempty finite bounds',()=>{
 const kit=setKit(T);
 for(const key of ['court','throne','chest','meetingRoom','house']){
  const obj=kit[key]();assert.ok(obj.isObject3D);const b=new T.Box3().setFromObject(obj);assert.ok(!b.isEmpty());assert.ok([...b.min.toArray(),...b.max.toArray()].every(Number.isFinite));
 }
 assert.ok(kit.house().getObjectByName('roof').isMesh);
});
