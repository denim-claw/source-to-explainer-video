/* SPDX-License-Identifier: MIT */
import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { fitFixedShot, visibleBounds, boxCorners } from '../assets/hybrid-3d/fixed-shot.mjs';
import { animalKit } from '../assets/hybrid-3d/animals.mjs';

const close = (a, b, epsilon = 1e-8) => assert.ok(Math.abs(a - b) <= epsilon, `${a} != ${b}`);
const cube = (size = 1, material = new THREE.MeshBasicMaterial()) =>
  new THREE.Mesh(new THREE.BoxGeometry(size, size, size), material);

function fixture({ start = 0, end = 2 } = {}) {
  const root = new THREE.Group();
  const focus = cube();
  root.add(focus);
  const calls = [];
  const shot = {
    start, end, root, foci: [{ id: 'subject', root: focus }],
    reset() { focus.position.set(0, 0.5, 0); focus.rotation.set(0, 0, 0); focus.scale.setScalar(1); },
    update(time) {
      assert.ok(time >= start && time < end, `sample escaped shot: ${time}`);
      calls.push(time);
      focus.position.x = (time - start) * 3;
    },
  };
  return { shot, focus, calls };
}

function cameraState(camera) {
  return {
    position: camera.position.toArray(), quaternion: camera.quaternion.toArray(),
    up: camera.up.toArray(), left: camera.left, right: camera.right,
    top: camera.top, bottom: camera.bottom, near: camera.near, far: camera.far, zoom: camera.zoom,
    projection: camera.projectionMatrix.toArray(), world: camera.matrixWorld.toArray(),
    inverseWorld: camera.matrixWorldInverse.toArray(),
  };
}

function inside(camera, bounds) {
  for (const corner of boxCorners(THREE, bounds)) {
    const point = corner.project(camera);
    for (const axis of ['x', 'y', 'z']) {
      assert.ok(Number.isFinite(point[axis]), `nonfinite projected ${axis}`);
      assert.ok(Math.abs(point[axis]) <= 1 + 1e-8, `${axis}=${point[axis]} outside viewport`);
    }
  }
}

test('visibleBounds excludes hidden/decorative ancestors and invisible materials', () => {
  const root = new THREE.Group();
  const focal = cube();
  focal.position.set(2, 1, -1);
  root.add(focal);
  const expected = new THREE.Box3().setFromObject(focal);
  const hidden = new THREE.Group();
  hidden.visible = false;
  hidden.add(cube(500));
  root.add(hidden);
  const decorative = new THREE.Group();
  decorative.userData.decorative = true;
  const decoration = cube(1000);
  decorative.add(decoration);
  root.add(decorative);
  root.add(cube(200, new THREE.MeshBasicMaterial({ visible: false })));
  root.add(cube(300, new THREE.MeshBasicMaterial({ opacity: 0, transparent: true })));
  root.add(cube(300, [new THREE.MeshBasicMaterial({ visible: false }),
    new THREE.MeshBasicMaterial({ opacity: 0.001, transparent: true })]));
  assert.ok(visibleBounds(THREE, root).equals(expected));
  assert.ok(visibleBounds(THREE, decoration).isEmpty(), 'excluded ancestor above focus');
  assert.ok(visibleBounds(THREE, hidden.children[0]).isEmpty(), 'hidden ancestor above focus');
  root.visible = false;
  assert.ok(visibleBounds(THREE, focal).isEmpty());
});

test('visibleBounds updates ancestors and handles material arrays and instances', () => {
  const outer = new THREE.Group();
  const root = new THREE.Group();
  outer.add(root);
  const mesh = cube(2, [new THREE.MeshBasicMaterial({ visible: false }), new THREE.MeshBasicMaterial()]);
  root.add(mesh);
  outer.position.set(8, 4, -3);
  const bounds = visibleBounds(THREE, root);
  assert.deepEqual(bounds.min.toArray(), [7, 3, -4]);
  assert.deepEqual(bounds.max.toArray(), [9, 5, -2]);
  const instances = new THREE.InstancedMesh(new THREE.BoxGeometry(1, 1, 1),
    new THREE.MeshBasicMaterial(), 2);
  instances.setMatrixAt(0, new THREE.Matrix4().makeTranslation(-5, 0, 0));
  instances.setMatrixAt(1, new THREE.Matrix4().makeTranslation(5, 0, 0));
  const instanceBounds = visibleBounds(THREE, instances);
  close(instanceBounds.min.x, -5.5);
  close(instanceBounds.max.x, 5.5);
  instances.setMatrixAt(1, new THREE.Matrix4().makeTranslation(9, 0, 0));
  close(visibleBounds(THREE, instances).max.x, 9.5, 1e-6);
  const opaque = cube(2, new THREE.MeshBasicMaterial({ opacity: 0, transparent: false }));
  assert.ok(!visibleBounds(THREE, opaque).isEmpty(), 'opacity only hides transparent materials');
});

test('visibleBounds evaluates the current skinned pose, not a cached bind-pose box', () => {
  const geometry = new THREE.BoxGeometry(1, 1, 1);
  const count = geometry.getAttribute('position').count;
  const weights = new Float32Array(count * 4);
  for (let index = 0; index < count; index++) weights[index * 4] = 1;
  geometry.setAttribute('skinIndex', new THREE.Uint16BufferAttribute(new Uint16Array(count * 4), 4));
  geometry.setAttribute('skinWeight', new THREE.Float32BufferAttribute(weights, 4));
  const mesh = new THREE.SkinnedMesh(geometry, new THREE.MeshBasicMaterial());
  const bone = new THREE.Bone();
  mesh.add(bone);
  mesh.bind(new THREE.Skeleton([bone]));
  bone.position.x = 2;
  const first = visibleBounds(THREE, mesh);
  close(first.min.x, 1.5);
  close(first.max.x, 2.5);
  bone.position.x = -3;
  const second = visibleBounds(THREE, mesh);
  close(second.min.x, -3.5);
  close(second.max.x, -2.5);
});

test('boxCorners returns independent finite corners and handles empty/invalid boxes', () => {
  const bounds = new THREE.Box3(new THREE.Vector3(-2, 1, -4), new THREE.Vector3(3, 5, 7));
  const original = bounds.clone();
  const corners = boxCorners(THREE, bounds);
  assert.equal(corners.length, 8);
  assert.equal(new Set(corners.map(corner => corner.toArray().join(','))).size, 8);
  assert.ok(corners.every(corner => bounds.containsPoint(corner)));
  corners[0].x = 100;
  assert.ok(bounds.equals(original));
  assert.deepEqual(boxCorners(THREE, new THREE.Box3()), []);
  assert.throws(() => boxCorners(THREE, {}), TypeError);
  assert.throws(() => boxCorners(THREE,
    new THREE.Box3(new THREE.Vector3(NaN, 0, 0), new THREE.Vector3(1, 1, 1))), /NaN/);
  assert.throws(() => boxCorners(THREE,
    new THREE.Box3(new THREE.Vector3(0, 0, 0), new THREE.Vector3(Infinity, 1, 1))), /finite/);
});

test('whole-shot fit contains moving animal bounds and never changes the camera during seeking', () => {
  const root = new THREE.Group();
  const { lion, fox, wolf } = animalKit(THREE);
  const animals = [lion({ scale: 1.4 }), fox({ scale: 0.7 }), wolf({ scale: 1.1 })];
  animals.forEach(animal => root.add(animal.root));
  const floor = cube(10000);
  floor.userData.decorative = true;
  root.add(floor);
  const shot = {
    start: 10, end: 14, root,
    foci: animals.map((animal, index) => ({ id: `animal-${index}`, root: animal.root })),
    utterances: [{ start: 9, end: 11 }, { start: 11, end: 13 }, { start: 13, end: 15 }],
    reset() {
      for (const animal of animals) { animal.root.position.set(0, 0, 0); animal.pose(); }
    },
    update(time) {
      assert.ok(time >= this.start && time < this.end);
      const t = time - this.start;
      animals.forEach((animal, index) => {
        animal.root.position.set(-5 + t * 2.5 + index * 1.2, 0, (index - 1) * 2 + Math.sin(t * 2));
        animal.pose({ phase: t * 6 + index, stride: 0.7, turn: Math.sin(t) * 0.5,
          crouch: index === 1 ? (1 + Math.sin(t)) / 2 : 0,
          rear: index === 0 ? Math.max(0, Math.sin(t * 2)) : 0 });
      });
    },
  };
  const view = { x: 40, y: 20, w: 1080, h: 520 };
  const { camera, report } = fitFixedShot(THREE, shot, { view, step: 0.02, padding: 1.08 });
  assert.ok(camera.isOrthographicCamera);
  assert.deepEqual(report.view, view);
  assert.equal(report.samples, report.sampleTimes.length);
  assert.equal(report.sampleTimes[0], shot.start);
  assert.ok(report.sampleTimes.every(time => time >= shot.start && time < shot.end));
  assert.ok(Object.isFrozen(report) && Object.isFrozen(report.pose.position));
  assert.ok(report.bounds.max[0] - report.bounds.min[0] < 20, 'decorative world was excluded');
  close(camera.right / camera.top, view.w / view.h);
  close(animals[0].root.position.x, -5, 1e-8);
  const fixed = cameraState(camera);
  const poses = [];
  // Audit a denser set than the fit grid, in reverse order and a different order.
  for (let index = 0; index <= 500; index++) poses.push(shot.start + 3.9999 * index / 500);
  for (const time of [...poses].reverse().concat(poses.filter((_, index) => index % 7 === 0))) {
    shot.reset();
    shot.update(time);
    for (const animal of animals) inside(camera, visibleBounds(THREE, animal.root));
    camera.updateMatrixWorld(true);
    camera.updateProjectionMatrix();
    assert.deepEqual(cameraState(camera), fixed);
  }
  const again = fitFixedShot(THREE, shot, { view, step: 0.02, padding: 1.08 });
  assert.deepEqual(again.report, report, 'refitting at a cut is independent of last seek');
  assert.deepEqual(cameraState(again.camera), fixed);
});

test('depth clipping and axial/very large/very small directions stay finite', () => {
  for (const direction of [[0, 0, 1], [0, 1, 0], [0, -1, 0], [1e308, 1e308, 1e308],
    [Number.MIN_VALUE, 0, 0]]) {
    const root = new THREE.Group();
    for (const z of [-400, 400]) {
      const mesh = cube(3);
      mesh.position.z = z;
      root.add(mesh);
    }
    const shot = { start: 0, end: 1, root, foci: [{ id: 'deep-stage', root }], reset() {}, update() {} };
    const { camera } = fitFixedShot(THREE, shot, { direction, view: { w: 300, h: 800 } });
    assert.ok(camera.near > 0 && camera.far > camera.near);
    inside(camera, visibleBounds(THREE, root));
  }
});

test('short shots include start/end-epsilon and never sample outside the shot', () => {
  for (const [start, end] of [[2, 2.0000001], [1, 1 + Number.EPSILON],
    [-4, -3.9999999], [0, Number.MIN_VALUE]]) {
    const { shot, calls } = fixture({ start, end });
    shot.utterances = [{ start: start - 10, end: end + 10 }, { start: end + 10, end: end + 20 }];
    const { report } = fitFixedShot(THREE, shot, { step: 0.2 });
    assert.equal(report.sampleTimes[0], start);
    assert.ok(calls.every(time => time >= start && time < end));
    assert.equal(calls.at(-1), start, 'start pose restored after sampling');
    if (end - start > Number.EPSILON) {
      assert.ok(report.sampleTimes.at(-1) > start);
    }
  }
});

test('clipped utterance anchors and the final in-shot sample are included', () => {
  const { shot } = fixture({ start: 1, end: 3 });
  shot.utterances = [{ start: -10, end: -5 }, { start: -1, end: 1.5 },
    { start: 1.7, end: 2.1 }, { start: 2.5, end: 20 }];
  const { report } = fitFixedShot(THREE, shot, { step: 0.6 });
  for (const anchor of [1, 1.5, 1.7, 2.1, 2.5, 2.999]) {
    assert.ok(report.sampleTimes.some(time => Math.abs(time - anchor) < 1e-10), `missing ${anchor}`);
  }
  assert.deepEqual(report.sampleTimes, [...new Set(report.sampleTimes)].sort((a, b) => a - b));
  assert.ok(report.sampleTimes.every(time => time >= 1 && time < 3));
});

test('invalid fit arguments fail before executing shot callbacks', () => {
  const badOptions = [null, [], { step: 0 }, { step: -1 }, { step: NaN }, { step: Infinity },
    { step: Number.MIN_VALUE }, { step: '0.1' }, { padding: 0 }, { padding: 0.9 },
    { padding: Infinity }, { padding: NaN }, { view: null }, { view: { w: 0, h: 1 } },
    { view: { w: 1, h: -1 } }, { view: { w: Infinity, h: 1 } }, { view: { w: 1, h: NaN } },
    { view: { w: 1, h: 1, x: -1 } }, { view: { w: 1, h: 1, y: '0' } },
    { view: { w: 1e308, h: Number.MIN_VALUE } }, { direction: null }, { direction: [0, 0, 0] },
    { direction: [1, 2] }, { direction: [1, 2, 3, 4] }, { direction: Array(3) }, { direction: [1, NaN, 1] },
    { direction: [1, Infinity, 1] }, { direction: [1, '1', 1] }];
  for (const options of badOptions) {
    const { shot, calls } = fixture();
    assert.throws(() => fitFixedShot(THREE, shot, options), { name: /TypeError|RangeError/ });
    assert.equal(calls.length, 0);
  }
  for (const patch of [{ start: NaN }, { end: Infinity }, { end: 0 }, { end: -1 },
    { start: -Number.MAX_VALUE, end: Number.MAX_VALUE }, { root: {} }, { reset: null },
    { update: 1 }, { foci: [] }, { foci: [{ id: '', root: new THREE.Group() }] },
    { foci: [{ id: 'foreign', root: new THREE.Group() }] }, { utterances: null },
    { utterances: [{ start: 1, end: 1 }] }, { utterances: [{ start: NaN, end: 1 }] }]) {
    const { shot, calls } = fixture();
    assert.throws(() => fitFixedShot(THREE, { ...shot, ...patch }), { name: /TypeError|RangeError/ });
    assert.equal(calls.length, 0);
  }
  const { shot, focus } = fixture();
  shot.foci.push({ id: 'subject', root: focus });
  assert.throws(() => fitFixedShot(THREE, shot), /unique/);
  assert.throws(() => fitFixedShot({}, shot), /THREE/);
});

test('empty geometry and failed sampling restore the start pose; invalid geometry is rejected', () => {
  const { shot, focus, calls } = fixture();
  focus.visible = false;
  assert.throws(() => fitFixedShot(THREE, shot), /no visible/);
  assert.equal(calls.at(-1), shot.start);
  focus.visible = true;
  const originalUpdate = shot.update;
  shot.update = time => {
    originalUpdate(time);
    if (time > 0.3) throw new Error('intentional sampling failure');
  };
  assert.throws(() => fitFixedShot(THREE, shot), /intentional sampling failure/);
  assert.equal(calls.at(-1), shot.start);
  close(focus.position.x, 0);
  focus.position.x = NaN;
  assert.throws(() => visibleBounds(THREE, focus), /non-finite/);
  focus.position.x = 0;
  focus.geometry.boundingBox = new THREE.Box3(new THREE.Vector3(-1, 0, 0), new THREE.Vector3(Infinity, 1, 1));
  assert.throws(() => visibleBounds(THREE, focus), /finite/);
});
