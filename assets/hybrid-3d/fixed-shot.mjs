/* SPDX-License-Identifier: MIT
 * Copyright (c) 2026 min (denim-claw)
 * Original fixed-shot geometry/camera helpers; see the repository LICENSE.
 */

const DEFAULT_VIEW = Object.freeze({ x: 0, y: 0, w: 1280, h: 720 });
const SAMPLE_LIMIT = 100_000;

function requireThree(THREE, camera = false) {
  for (const key of ['Vector3', 'Box3', ...(camera ? ['OrthographicCamera'] : [])]) {
    if (typeof THREE?.[key] !== 'function') throw new TypeError(`requires THREE.${key}`);
  }
}

function object3D(value, label) {
  if (!value?.isObject3D || typeof value.updateWorldMatrix !== 'function') {
    throw new TypeError(`${label} must be a THREE.Object3D`);
  }
}

function object(value, label) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw new TypeError(`${label} must be an object`);
  }
  return value;
}

function finite(value, label) {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    throw new TypeError(`${label} must be a finite number`);
  }
  return value;
}

function positive(value, label) {
  finite(value, label);
  if (value <= 0) throw new RangeError(`${label} must be positive`);
  return value;
}

function finiteBox(box, label) {
  for (const vector of [box.min, box.max]) {
    for (const axis of ['x', 'y', 'z']) finite(vector[axis], `${label}.${axis}`);
  }
}

function suppressed(node) {
  return node.visible === false || Boolean(node.userData?.decorative);
}

function materialVisible(material) {
  return material && material.visible !== false
    && (!material.transparent || material.opacity > 0.005);
}

/**
 * Conservative world-space bounds of visible focal mesh geometry.
 * THREE is injected; no project asset module or scene globals are required.
 * Hidden/decorative ancestors (including ancestors above root) exclude a subtree.
 * Mark floors, blob shadows, and non-focal effects with userData.decorative=true.
 * Fully hidden materials and near-zero transparent opacity are excluded. If any
 * material in a material array is visible, its whole mesh is bounded, so bounds
 * may overestimate partially hidden geometry. Shader vertex displacement, sprite
 * billboards, and non-mesh primitives are not bounded by this helper.
 */
export function visibleBounds(THREE, root) {
  requireThree(THREE);
  object3D(root, 'root');
  const result = new THREE.Box3();
  for (let ancestor = root; ancestor; ancestor = ancestor.parent) {
    if (suppressed(ancestor)) return result;
  }
  root.updateWorldMatrix(true, true);
  function visit(node) {
    if (suppressed(node)) return;
    if (node.isMesh && node.geometry) {
      const materials = Array.isArray(node.material) ? node.material : [node.material];
      if (materials.some(materialVisible)) {
        if (!node.matrixWorld.elements.every(Number.isFinite)) {
          throw new RangeError(`non-finite world transform: ${node.name || 'mesh'}`);
        }
        // Object-level bounds incorporate instances/current skinned poses.
        let bounds;
        if (node.isInstancedMesh || node.isSkinnedMesh) {
          node.computeBoundingBox();
          bounds = node.boundingBox;
        } else {
          if (!node.geometry.boundingBox) node.geometry.computeBoundingBox();
          bounds = node.geometry.boundingBox;
        }
        if (bounds && !bounds.isEmpty()) {
          finiteBox(bounds, 'geometry bounds');
          const world = bounds.clone().applyMatrix4(node.matrixWorld);
          finiteBox(world, 'world bounds');
          result.union(world);
        }
      }
    }
    for (const child of node.children) visit(child);
  }
  visit(root);
  return result;
}

/** Return eight independent corners, or [] for an empty Box3. */
export function boxCorners(THREE, box) {
  requireThree(THREE);
  if (!box?.isBox3) throw new TypeError('box must be a THREE.Box3');
  // The canonical empty Box3 uses infinities, but NaNs are always invalid.
  if ([...box.min.toArray(), ...box.max.toArray()].some(Number.isNaN)) {
    throw new TypeError('box must not contain NaN');
  }
  if (box.isEmpty()) return [];
  finiteBox(box, 'box');
  const result = [];
  for (const x of [box.min.x, box.max.x]) {
    for (const y of [box.min.y, box.max.y]) {
      for (const z of [box.min.z, box.max.z]) result.push(new THREE.Vector3(x, y, z));
    }
  }
  return result;
}

// Previous representable float, including negative times and adjacent endpoints.
function previousFloat(value) {
  if (value === 0) return -Number.MIN_VALUE;
  const number = new Float64Array([value]);
  const bits = new BigUint64Array(number.buffer);
  bits[0] += value > 0 ? -1n : 1n;
  return number[0];
}

function sampleTimes(start, end, step, utterances) {
  const duration = end - start;
  const gridCount = Math.ceil(duration / step);
  if (!Number.isFinite(gridCount) || gridCount > SAMPLE_LIMIT - 2) {
    throw new RangeError(`step requires too many samples (limit ${SAMPLE_LIMIT})`);
  }
  // Never subtract a fixed millisecond from a sub-millisecond shot. Fall back
  // to the previous float if subtraction rounds back up to the excluded end.
  let last = end - Math.min(0.001, duration / 2);
  if (last >= end) last = previousFloat(end);
  last = Math.max(start, last);
  const times = new Set([start, last]);
  for (let index = 1; index < gridCount; index++) {
    const time = start + index * step;
    if (time >= start && time < end) times.add(time);
  }
  for (const utterance of utterances) {
    object(utterance, 'utterance');
    finite(utterance.start, 'utterance.start');
    finite(utterance.end, 'utterance.end');
    if (utterance.end <= utterance.start) throw new RangeError('utterance.end must exceed start');
    const a = Math.max(start, utterance.start);
    const b = Math.min(end, utterance.end);
    if (a >= b) continue;
    for (const fraction of [0, 0.05, 0.1, 0.2, 0.4, 0.5, 0.65, 0.72, 0.8, 0.9, 0.95, 1]) {
      const time = a + (b - a) * fraction;
      times.add(Math.max(start, time >= end ? last : time));
    }
    if (times.size > SAMPLE_LIMIT) throw new RangeError('too many utterance samples');
  }
  return [...times].sort((a, b) => a - b);
}

/**
 * Fit ONE held orthographic camera from a sampled whole-shot union.
 *
 * shot = { start, end, root, reset(), update(absoluteTime), foci:[{id,root}],
 *          utterances?: [{start,end}] }
 * opts = { view:{x:0,y:0,w:1280,h:720}, step:0.2, padding:1.045,
 *          direction:[2.2,7.4,16] }
 *
 * Foci must be descendants of shot.root (or root itself). reset()/update(t)
 * must evaluate absolute poses. The sampling interval is [start,end), including
 * start and end-epsilon; utterances are clipped to that interval. On completion
 * (also on a sampling failure), reset()/update(start) restores the start pose.
 *
 * view describes the renderer's viewport in pixels; this helper does not call
 * renderer.setViewport(). padding >= 1 is a multiplicative framing margin.
 * direction points FROM the target TO the camera. Depth clipping is fitted too.
 * Treat the returned camera's pose/frustum as immutable until the next cut.
 * It remains a normal Three camera so renderer matrix-cache updates still work;
 * there is no animation-time update/refit hook and no scene callbacks retained.
 *
 * Finite sampling cannot prove containment at unobserved extrema or discontinuous
 * changes. Reduce step/add utterance anchors, and audit the actual rendered poses.
 */
export function fitFixedShot(THREE, shot, opts = {}) {
  requireThree(THREE, true);
  object(shot, 'shot');
  object(opts, 'options');
  const start = finite(shot.start, 'shot.start');
  const end = finite(shot.end, 'shot.end');
  if (end <= start || !Number.isFinite(end - start)) {
    throw new RangeError('shot.end must exceed start by a finite duration');
  }
  object3D(shot.root, 'shot.root');
  if (typeof shot.reset !== 'function' || typeof shot.update !== 'function') {
    throw new TypeError('shot.reset and shot.update must be functions');
  }
  if (!Array.isArray(shot.foci) || !shot.foci.length) {
    throw new TypeError('register at least one focal object, not the decorative floor');
  }
  const ids = new Set();
  for (const focal of shot.foci) {
    object(focal, 'focal');
    if (typeof focal.id !== 'string' || !focal.id || ids.has(focal.id)) {
      throw new TypeError('focal ids must be nonempty, unique strings');
    }
    ids.add(focal.id);
    object3D(focal.root, 'focal.root');
    let node = focal.root;
    while (node && node !== shot.root) node = node.parent;
    if (!node) throw new RangeError('focal.root must belong to shot.root');
  }
  const step = positive(opts.step === undefined ? 0.2 : opts.step, 'step');
  const padding = positive(opts.padding === undefined ? 1.045 : opts.padding, 'padding');
  if (padding < 1) throw new RangeError('padding must be at least 1 to contain the bounds');
  const suppliedView = object(opts.view === undefined ? DEFAULT_VIEW : opts.view, 'view');
  const view = {
    x: finite(suppliedView.x === undefined ? 0 : suppliedView.x, 'view.x'),
    y: finite(suppliedView.y === undefined ? 0 : suppliedView.y, 'view.y'),
    w: positive(suppliedView.w, 'view.w'),
    h: positive(suppliedView.h, 'view.h'),
  };
  if (view.x < 0 || view.y < 0) throw new RangeError('viewport offsets must be nonnegative');
  const aspect = positive(view.w / view.h, 'viewport aspect');
  const direction = opts.direction === undefined ? [2.2, 7.4, 16] : opts.direction;
  if (!Array.isArray(direction) || direction.length !== 3) {
    throw new TypeError('direction must be an array of three finite numbers');
  }
  for (const value of direction) finite(value, 'direction component');
  const magnitude = Math.max(...direction.map(Math.abs));
  if (magnitude === 0) throw new RangeError('direction must be nonzero');
  // Normalize safely even for very small/large finite direction components.
  const ray = new THREE.Vector3(...direction.map(value => value / magnitude)).normalize();
  const utterances = shot.utterances === undefined ? [] : shot.utterances;
  if (!Array.isArray(utterances)) throw new TypeError('utterances must be an array');
  const times = sampleTimes(start, end, step, utterances);

  try {
    const union = new THREE.Box3();
    for (const time of times) {
      shot.reset();
      shot.update(time);
      shot.root.updateWorldMatrix(true, true);
      for (const focal of shot.foci) union.union(visibleBounds(THREE, focal.root));
    }
    if (union.isEmpty()) throw new RangeError('no visible focal mesh geometry');
    finiteBox(union, 'sampled bounds');
    const target = union.getCenter(new THREE.Vector3());
    const size = union.getSize(new THREE.Vector3());
    const radius = positive(Math.max(Math.hypot(size.x, size.y, size.z) / 2, 1e-6), 'bounds radius');
    const distance = positive(Math.max(1, radius * 2), 'camera distance');
    const near = positive(Math.max(1e-4, radius * 1e-4), 'near');
    const far = positive(distance + radius + Math.max(1, radius * 0.01), 'far');
    const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, near, far);
    if (Math.abs(ray.y) > 0.999) camera.up.set(0, 0, 1);
    camera.position.copy(target).addScaledVector(ray, distance);
    if (![...target.toArray(), ...camera.position.toArray()].every(Number.isFinite)) {
      throw new RangeError('bounds are too large to fit a finite camera');
    }
    camera.lookAt(target);
    camera.updateMatrixWorld(true);
    const local = boxCorners(THREE, union).map(corner => corner.applyMatrix4(camera.matrixWorldInverse));
    const halfHeight = positive(Math.max(1e-6,
      ...local.map(corner => Math.abs(corner.y)),
      ...local.map(corner => Math.abs(corner.x) / aspect)) * padding, 'frustum height');
    const halfWidth = positive(halfHeight * aspect, 'frustum width');
    camera.left = -halfWidth;
    camera.right = halfWidth;
    camera.top = halfHeight;
    camera.bottom = -halfHeight;
    camera.updateProjectionMatrix();
    const cameraValues = [...camera.projectionMatrix.elements, ...camera.projectionMatrixInverse.elements,
      ...camera.matrixWorld.elements, ...camera.matrixWorldInverse.elements];
    if (!cameraValues.every(Number.isFinite)
      || camera.projectionMatrixInverse.elements.every(value => value === 0)) {
      throw new RangeError('camera matrices must remain finite');
    }
    const freezeArray = values => Object.freeze(values);
    const report = Object.freeze({
      method: 'One held orthographic camera from the sampled whole-shot focal union',
      samples: times.length,
      sampleStep: step,
      sampleTimes: freezeArray(times),
      padding,
      view: Object.freeze(view),
      bounds: Object.freeze({ min: freezeArray(union.min.toArray()), max: freezeArray(union.max.toArray()) }),
      pose: Object.freeze({
        position: freezeArray(camera.position.toArray()), quaternion: freezeArray(camera.quaternion.toArray()),
        left: camera.left, right: camera.right, top: camera.top, bottom: camera.bottom, near, far,
      }),
    });
    return { camera, report };
  } finally {
    shot.reset();
    shot.update(start);
    shot.root.updateWorldMatrix(true, true);
  }
}
