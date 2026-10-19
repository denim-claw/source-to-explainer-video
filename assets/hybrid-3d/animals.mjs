/* SPDX-License-Identifier: MIT
 * Copyright (c) 2026 min (denim-claw)
 * Original procedural geometry; see the repository LICENSE.
 */

/**
 * Texture-free, stylized low-poly animals with an injected Three.js namespace.
 *
 * const { fox } = animalKit(THREE);
 * const animal = fox({ x: 2, z: -1, scale: 0.8 });
 * scene.add(animal.root);
 * animal.pose({ phase: seconds * 6, stride: 0.7, turn: Math.PI });
 *
 * Floor origin, +Y up, forward +X: yaw/turn=0 faces +X; Math.PI faces -X.
 * Factories accept finite x/y/z, a positive uniform scale, and a coat color
 * (hex integer, CSS hex/name, or THREE.Color). y defaults to zero.
 * pose() is an absolute, seek-order-independent evaluation. phase/turn are
 * radians (reduced modulo 2π); stride/crouch/rear are clamped to [0, 1].
 * Translation belongs to the caller and is never overwritten by pose(). The
 * factory's uniform root scale is preserved on all axes, including crouching.
 * These are simple rigid-part motions, not mocap, IK, or foot-locked gaits.
 * Resting paws touch y=0; moving/rearing paws are not ground constrained.
 */
export function animalKit(THREE) {
  for (const key of ['Group', 'Mesh', 'BoxGeometry', 'ConeGeometry',
    'IcosahedronGeometry', 'MeshStandardMaterial', 'Color']) {
    if (typeof THREE?.[key] !== 'function') {
      throw new TypeError(`animalKit requires THREE.${key}`);
    }
  }

  const TAU = Math.PI * 2;
  const definitions = {
    lion: { coat: '#b98a4e', leg: 0.58, width: 0.13, hipX: 0.50, hipZ: 0.22,
      body: [1.45, 0.56, 0.60, -0.07, 0.82],
      chest: [0.60, 0.63, 0.62, 0.51, 0.85],
      head: [0.95, 1.02], tail: [-0.78, 0.83], tailAngle: 0.28 },
    fox: { coat: '#c4703c', leg: 0.35, width: 0.065, hipX: 0.30, hipZ: 0.125,
      body: [0.92, 0.32, 0.34, -0.04, 0.49],
      chest: [0.28, 0.31, 0.30, 0.42, 0.56],
      head: [0.62, 0.66], tail: [-0.52, 0.53], tailAngle: 0.18 },
    wolf: { coat: '#636d77', leg: 0.52, width: 0.07, hipX: 0.36, hipZ: 0.12,
      body: [1.12, 0.31, 0.33, -0.04, 0.67],
      chest: [0.34, 0.40, 0.35, 0.43, 0.73],
      head: [0.68, 0.87], tail: [-0.62, 0.66], tailAngle: 0.45 },
  };

  function options(value, label) {
    if (!value || typeof value !== 'object' || Array.isArray(value)) {
      throw new TypeError(`${label} must be an options object`);
    }
    return value;
  }

  function finite(value, label) {
    if (typeof value !== 'number' || !Number.isFinite(value)) {
      throw new TypeError(`${label} must be a finite number`);
    }
    return value;
  }

  function coatColor(value) {
    const valid = typeof value === 'number'
      ? Number.isInteger(value) && value >= 0 && value <= 0xffffff
      : typeof value === 'string'
        ? /^#(?:[\da-f]{3}|[\da-f]{6})$/i.test(value)
          || Object.hasOwn(THREE.Color.NAMES || {}, value.toLowerCase())
        : value?.isColor && ['r', 'g', 'b'].every(k =>
          typeof value[k] === 'number' && Number.isFinite(value[k]) && value[k] >= 0);
    if (!valid) throw new TypeError('color must be a valid hex/name or finite THREE.Color');
    return new THREE.Color(typeof value === 'string' ? value.toLowerCase() : value);
  }

  const fallback = (value, defaultValue) => value === undefined ? defaultValue : value;
  const clamp = value => Math.max(0, Math.min(1, value));
  const radians = value => {
    const angle = value % TAU;
    return angle > Math.PI ? angle - TAU : angle < -Math.PI ? angle + TAU : angle;
  };

  function build(kind, values = {}) {
    const config = definitions[kind];
    const opts = options(values, kind);
    const x = finite(fallback(opts.x, 0), 'x');
    const y = finite(fallback(opts.y, 0), 'y');
    const z = finite(fallback(opts.z, 0), 'z');
    const scale = finite(fallback(opts.scale, 1), 'scale');
    if (scale <= 0) throw new RangeError('scale must be positive');
    if (![x, y, z].every(value => Number.isFinite(Math.abs(value) + scale * 4))) {
      throw new RangeError('scale/translation exceed representable animal bounds');
    }
    const coat = coatColor(fallback(opts.color, config.coat));
    const root = new THREE.Group();
    root.name = kind;
    root.position.set(x, y, z);
    root.scale.setScalar(scale);

    // Rotate around the hind floor point, not the world/root translation.
    const posture = new THREE.Group();
    posture.name = 'posture';
    posture.position.x = -config.hipX;
    root.add(posture);
    const body = new THREE.Group();
    body.name = 'rig';
    body.position.x = config.hipX;
    posture.add(body);

    const materials = new Map();
    function material(color) {
      const key = color.isColor ? color.getHexString() : color;
      if (!materials.has(key)) materials.set(key, new THREE.MeshStandardMaterial({
        color, flatShading: true, roughness: 0.86, metalness: 0,
      }));
      return materials.get(key);
    }
    function mesh(parent, name, geometry, color, px, py, pz = 0) {
      const part = new THREE.Mesh(geometry, material(color));
      part.name = name;
      part.position.set(px, py, pz);
      parent.add(part);
      return part;
    }
    function box(parent, name, w, h, d, color, px, py, pz = 0) {
      return mesh(parent, name, new THREE.BoxGeometry(w, h, d), color, px, py, pz);
    }
    function cone(parent, name, radius, height, color, px, py, pz = 0) {
      return mesh(parent, name, new THREE.ConeGeometry(radius, height, 4), color, px, py, pz);
    }
    function lump(parent, name, radius, color, px, py, pz = 0) {
      return mesh(parent, name, new THREE.IcosahedronGeometry(radius, 0), color, px, py, pz);
    }
    function block(name, dimensions) {
      const [w, h, d, px, py] = dimensions;
      return box(body, name, w, h, d, coat, px, py);
    }
    block('torso', config.body);
    block('chest', config.chest);

    const hips = [];
    for (const [front, side] of [[false, -1], [false, 1], [true, -1], [true, 1]]) {
      const hip = new THREE.Group();
      hip.name = `${front ? 'front' : 'hind'}-${side < 0 ? 'left' : 'right'}-hip`;
      hip.position.set((front ? 1 : -1) * config.hipX, config.leg, side * config.hipZ);
      body.add(hip);
      box(hip, 'leg', config.width, config.leg, config.width, coat, 0, -config.leg / 2);
      const pawHeight = config.width * 0.65;
      box(hip, 'paw', config.width * 1.4, pawHeight, config.width * 1.25,
        kind === 'fox' ? '#49362d' : coat, config.width * 0.18,
        -config.leg + pawHeight / 2);
      hips.push({ hip, sign: (front ? 1 : -1) * side });
    }

    const head = new THREE.Group();
    head.name = 'head';
    head.position.set(...config.head, 0);
    body.add(head);
    const tail = new THREE.Group();
    tail.name = 'tail';
    tail.position.set(...config.tail, 0);
    body.add(tail);

    if (kind === 'lion') {
      const mane = lump(body, 'mane', 0.51, '#78502a', 0.67, 0.98);
      mane.scale.set(0.77, 1.03, 1.04);
      box(head, 'skull', 0.43, 0.40, 0.44, coat, 0, 0);
      box(head, 'muzzle', 0.33, 0.22, 0.30, '#ddbb8f', 0.30, -0.06);
      box(head, 'nose', 0.07, 0.09, 0.22, '#2a211c', 0.495, -0.035);
      for (const side of [-1, 1]) {
        cone(head, `ear-${side < 0 ? 'left' : 'right'}`, 0.10, 0.19, coat, -0.07, 0.26, side * 0.17);
        box(head, 'eye', 0.055, 0.06, 0.025, '#231d19', 0.19, 0.07, side * 0.222);
      }
      box(tail, 'tail-stem', 0.62, 0.065, 0.065, coat, -0.31, 0);
      lump(tail, 'tail-tip', 0.105, '#78502a', -0.65, 0);
    } else {
      box(head, 'skull', 0.27, kind === 'fox' ? 0.25 : 0.27, 0.28, coat, 0, 0);
      const muzzle = cone(head, 'muzzle', 0.095, kind === 'fox' ? 0.44 : 0.40,
        kind === 'fox' ? '#efd9bb' : '#929aa1', 0.30, -0.05);
      muzzle.rotation.z = -Math.PI / 2;
      box(head, 'nose', 0.065, 0.065, 0.075, '#262a2e', 0.50, -0.05);
      for (const side of [-1, 1]) {
        cone(head, `ear-${side < 0 ? 'left' : 'right'}`, 0.10,
          kind === 'fox' ? 0.33 : 0.27, coat, -0.06, 0.28, side * 0.105);
        box(head, 'eye', 0.055, 0.045, 0.025,
          kind === 'fox' ? '#302b27' : '#dbbd75', 0.115, 0.045, side * 0.142);
      }
      if (kind === 'fox') {
        box(body, 'bib', 0.20, 0.18, 0.26, '#eee3d1', 0.36, 0.43);
        const brush = lump(tail, 'tail-brush', 1, coat, -0.30, 0.02);
        brush.scale.set(0.43, 0.135, 0.15);
        const tip = cone(tail, 'tail-tip', 0.13, 0.30, '#f3ead8', -0.72, 0.02);
        tip.rotation.z = Math.PI / 2;
      } else {
        box(tail, 'tail-stem', 0.52, 0.10, 0.11, coat, -0.25, -0.04);
      }
    }

    function pose(values = {}) {
      const opts = options(values, 'pose');
      // Validate everything before mutating any transform.
      const phase = radians(finite(fallback(opts.phase, 0), 'phase'));
      const stride = clamp(finite(fallback(opts.stride, 0), 'stride'));
      const turn = radians(finite(fallback(opts.turn, 0), 'turn'));
      const crouch = clamp(finite(fallback(opts.crouch, 0), 'crouch'));
      const rear = clamp(finite(fallback(opts.rear, 0), 'rear'));
      root.rotation.set(0, turn, 0);
      root.scale.setScalar(scale);
      posture.rotation.set(0, 0, rear * 0.78);
      posture.scale.set(1, 1 - crouch * 0.18, 1);
      head.rotation.set(0, 0, crouch * 0.10 - rear * 0.14);
      for (const { hip, sign } of hips) {
        // A leg hangs along -Y, so rotation about Z swings it along +X/-X.
        hip.rotation.set(0, 0, Math.sin(phase) * stride * 0.58 * sign);
      }
      tail.rotation.set(0, Math.sin(phase) * stride * 0.22,
        config.tailAngle + Math.cos(phase) * stride * 0.10 + rear * 0.12);
      return root;
    }
    pose();
    return { root, pose };
  }

  return {
    lion: values => build('lion', values),
    fox: values => build('fox', values),
    wolf: values => build('wolf', values),
  };
}
