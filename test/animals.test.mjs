/* SPDX-License-Identifier: MIT */
import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { animalKit } from '../assets/hybrid-3d/animals.mjs';

const kit = animalKit(THREE);
const species = ['lion', 'fox', 'wolf'];
const scales = [0.4, 1, 2.75];
const close = (a, b, epsilon = 1e-6) => assert.ok(Math.abs(a - b) <= epsilon, `${a} != ${b}`);

function transforms(root) {
  const result = [];
  root.traverse(node => result.push({
    name: node.name,
    position: node.position.toArray(),
    quaternion: node.quaternion.toArray(),
    scale: node.scale.toArray(),
  }));
  return result;
}

function finiteGeometry(root) {
  let meshes = 0;
  root.updateWorldMatrix(true, true);
  root.traverse(node => {
    assert.ok(node.matrixWorld.elements.every(Number.isFinite), node.name);
    if (!node.isMesh) return;
    meshes++;
    for (const attribute of Object.values(node.geometry.attributes)) {
      assert.ok(Array.from(attribute.array).every(Number.isFinite), node.name);
    }
    node.geometry.computeBoundingBox();
    assert.ok([...node.geometry.boundingBox.min.toArray(),
      ...node.geometry.boundingBox.max.toArray()].every(Number.isFinite), node.name);
  });
  assert.ok(meshes >= 15);
}

for (const kind of species) {
  for (const scale of scales) {
    test(`${kind}: finite, grounded rest silhouette at scale ${scale}`, () => {
      const animal = kit[kind]({ scale });
      const { root, pose } = animal;
      assert.deepEqual(Object.keys(animal).sort(), ['pose', 'root']);
      assert.equal(typeof pose, 'function');
      finiteGeometry(root);
      const bounds = new THREE.Box3().setFromObject(root);
      close(bounds.min.y, 0);
      const size = bounds.getSize(new THREE.Vector3());
      assert.ok(size.x > size.y, 'quadruped silhouette is longer than tall');
      assert.ok(size.y > size.z, 'silhouette is taller than broad');
      for (const axis of ['x', 'y', 'z']) close(root.scale[axis], scale);
      const hips = [];
      root.traverse(node => { if (node.name.endsWith('-hip')) hips.push(node); });
      assert.equal(hips.length, 4);
      for (const hip of hips) {
        const paw = hip.getObjectByName('paw');
        close(new THREE.Box3().setFromObject(paw).min.y, 0);
      }
      const head = root.getObjectByName('head');
      const nose = root.getObjectByName('nose');
      assert.ok(nose.getWorldPosition(new THREE.Vector3()).x > head.getWorldPosition(new THREE.Vector3()).x);
      assert.ok(root.getObjectByName('tail').getWorldPosition(new THREE.Vector3()).x < 0);
      const ear = root.getObjectByName('ear-left');
      assert.ok(ear.geometry.type === 'ConeGeometry');
      if (kind === 'lion') {
        assert.ok(root.getObjectByName('mane').geometry.type === 'IcosahedronGeometry');
        assert.ok(root.getObjectByName('tail-tip'));
      } else {
        const muzzle = root.getObjectByName('muzzle');
        assert.equal(muzzle.geometry.type, 'ConeGeometry');
        assert.ok(muzzle.geometry.parameters.height > muzzle.geometry.parameters.radius * 2);
        assert.ok(ear.geometry.parameters.height > ear.geometry.parameters.radius * 2);
        if (kind === 'fox') {
          assert.ok(root.getObjectByName('tail-brush'));
          assert.equal(root.getObjectByName('tail-tip').material.color.getHex(), 0xf3ead8);
        } else {
          const coat = root.getObjectByName('torso').material.color;
          assert.ok(Math.max(coat.r, coat.g, coat.b) - Math.min(coat.r, coat.g, coat.b) < 0.1,
            'wolf has a neutral grey coat');
          assert.ok(size.x / size.z > 4, 'wolf is lean');
        }
      }
    });

    test(`${kind}: absolute poses reset and seek independently at scale ${scale}`, () => {
      const { root, pose } = kit[kind]({ x: 2, y: 3, z: -4, scale });
      const rest = transforms(root);
      const poses = [
        {},
        { phase: 0.35, stride: 0.6, turn: 0.5 },
        { phase: -1.8, stride: 1, turn: Math.PI, crouch: 0.8 },
        { phase: 4.2, stride: 0.4, rear: 1, crouch: 0.3, turn: -2.1 },
        { phase: 1000000, stride: 0.8, turn: 1000000, crouch: 0.6, rear: 0.2 },
      ];
      const expected = poses.map(parameters => { pose(parameters); return transforms(root); });
      for (const index of [4, 1, 3, 0, 2, 4, 0, 3, 2, 1]) {
        pose(poses[index]);
        assert.deepEqual(transforms(root), expected[index]);
        assert.deepEqual(root.position.toArray(), [2, 3, -4], 'pose must not move the root');
        assert.deepEqual(root.scale.toArray(), [scale, scale, scale]);
        finiteGeometry(root);
      }
      pose();
      assert.deepEqual(transforms(root), rest, 'rear/crouch/gait must not leak into rest');
      pose({ phase: 2, stride: 0, crouch: 0, rear: 0 });
      assert.deepEqual(transforms(root), rest, 'rest has no phase-dependent idle drift');
    });
  }

  test(`${kind}: forward convention, Z-axis gait, clamping, and caller translation`, () => {
    const { root, pose } = kit[kind]({ scale: 1.7 });
    root.position.set(8, 6, -3);
    pose({ phase: Math.PI / 2, stride: 1 });
    const frontLeft = root.getObjectByName('front-left-hip');
    const hindLeft = root.getObjectByName('hind-left-hip');
    assert.equal(frontLeft.rotation.x, 0);
    assert.equal(frontLeft.rotation.y, 0);
    assert.ok(Math.abs(frontLeft.rotation.z) > 0.5);
    close(frontLeft.rotation.z, -hindLeft.rotation.z);
    const paw = frontLeft.getObjectByName('paw');
    const pawPoint = paw.getWorldPosition(new THREE.Vector3());
    pose();
    const restPoint = paw.getWorldPosition(new THREE.Vector3());
    assert.ok(Math.abs(pawPoint.x - restPoint.x) > 0.1);
    close(pawPoint.z, restPoint.z, 1e-8);
    pose({ turn: Math.PI });
    const forward = new THREE.Vector3(1, 0, 0).applyQuaternion(root.quaternion);
    close(forward.x, -1);
    close(forward.z, 0);
    pose({ stride: 100, crouch: 100, rear: 100, phase: 0.4, turn: 0.3 });
    const saturated = transforms(root);
    pose({ stride: 1, crouch: 1, rear: 1, phase: 0.4, turn: 0.3 });
    assert.deepEqual(transforms(root), saturated);
    pose({ stride: -2, crouch: -2, rear: -2 });
    const negative = transforms(root);
    pose();
    assert.deepEqual(transforms(root), negative);
    assert.deepEqual(root.position.toArray(), [8, 6, -3]);
    assert.deepEqual(root.scale.toArray(), [1.7, 1.7, 1.7]);
    // Reset every controlled rotation axis, not just the axis used by the gait.
    for (const name of ['posture', 'head', 'tail', 'front-left-hip']) {
      root.getObjectByName(name).rotation.set(0.3, 0.5, 0.7);
    }
    root.rotation.set(0.7, 0.2, 0.8);
    root.scale.set(7, 8, 9);
    pose();
    assert.deepEqual(transforms(root), negative);
  });
}

test('animal options validate before constructing or changing transforms', () => {
  assert.throws(() => animalKit({}), /THREE/);
  for (const kind of species) {
    for (const options of [null, [], 1, 'fox', { x: NaN }, { y: Infinity }, { z: '2' }, { x: null },
      { scale: 0 }, { scale: -1 }, { scale: NaN }, { scale: Infinity }, { scale: Number.MAX_VALUE },
      { color: null }, { color: 'not-a-color' }, { color: -1 }, { color: Infinity }, { color: '#zzyyxx' },
      { color: { isColor: true, r: NaN, g: 0, b: 0 } }]) {
      assert.throws(() => kit[kind](options), { name: /TypeError|RangeError/ });
    }
    const { root, pose } = kit[kind]({ color: new THREE.Color('#88aa99') });
    pose({ phase: 0.9, stride: 0.5, rear: 0.7 });
    const before = transforms(root);
    for (const options of [null, [], false, { phase: NaN }, { stride: Infinity },
      { turn: -Infinity }, { crouch: '1' }, { rear: NaN }, { phase: null }]) {
      assert.throws(() => pose(options), TypeError);
      assert.deepEqual(transforms(root), before, 'bad pose must not partially mutate');
    }
    for (const color of ['#abc', 'navy', 0xaabbcc]) {
      finiteGeometry(kit[kind]({ color }).root);
    }
  }
});

test('animal instances share neither animated transforms nor material state', () => {
  const a = kit.fox();
  const b = kit.fox();
  const before = transforms(b.root);
  a.pose({ phase: 0.7, stride: 1, turn: 1, rear: 1 });
  a.root.getObjectByName('torso').material.color.set('#ff0000');
  assert.deepEqual(transforms(b.root), before);
  assert.notEqual(b.root.getObjectByName('torso').material.color.getHex(), 0xff0000);
});
