// motion.ts — the small physics that make things feel alive without looking procedural.

export const clamp = (x: number, a: number, b: number): number => Math.max(a, Math.min(b, x));
export const lerp = (a: number, b: number, t: number): number => a + (b - a) * t;
export const smooth = (e0: number, e1: number, x: number): number => { const t = clamp((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t); };
export const ease = (t: number): number => smooth(0, 1, t);
export const minJerk = (s: number): number => s * s * s * (10 - 15 * s + 6 * s * s);
export const rnd = (a: number, b: number): number => a + Math.random() * (b - a);

/** Seeded random for static drawing, so a scene looks the same on every load. */
export function seeded(seed = 11): (a?: number, b?: number) => number {
  let s = seed;
  return (a = 0, b = 1) => { s = (s * 16807) % 2147483647; return a + ((s - 1) / 2147483646) * (b - a); };
}

/** Layered sines: organic drift for idle motion that doesn't read as a loop. */
export const wobble = (t: number, k = 1): number => Math.sin(t * 1.3 * k) * 0.6 + Math.sin(t * 2.7 * k + 1.7) * 0.3 + Math.sin(t * 5.1 * k + 4.1) * 0.1;

export interface Spring { x: number; v: number; step(target: number, dt: number): number; kick(v: number): void }

/**
 * Damped spring toward a moving target. Use for anything attached to a moving body:
 * sleeves, bags, ears, a parasol's tilt, arms swinging opposite the legs.
 */
export function spring(stiffness = 40, damping = 6, x = 0): Spring {
  return {
    x, v: 0,
    step(target, dt) { this.v += (stiffness * (target - this.x) - damping * this.v) * dt; this.x += this.v * dt; return this.x; },
    kick(v) { this.v += v; },
  };
}

export interface Pendulum { a: number; v: number; step(force: number, dt: number): number; kick(v: number): void }

/**
 * Pendulum (angle in radians) for hanging things: lanterns, curtains, chimes, signs, a briefcase.
 * `force` is this frame's push — wind, the carrier's acceleration, a click.
 */
export function pendulum(stiffness = 10, damping = 1.1, a = 0): Pendulum {
  return {
    a, v: 0,
    step(force, dt) { this.v += (-this.a * stiffness + force - this.v * damping) * dt; this.a += this.v * dt; return this.a; },
    kick(v) { this.v += v; },
  };
}

export interface Wind { value: number; step(t: number): number }

/** Wind from pointer movement plus a slow breeze; `value` ≈ -2.4…2.4. A quick sideways swipe gusts it. */
export function pointerWind(target: EventTarget, base = 0.3): Wind {
  let aim = base, lastX: number | null = null, lastT = 0;
  const w: Wind = {
    value: base,
    step(t) {
      aim = lerp(aim, base + 0.25 * Math.sin(t * 0.21) + 0.15 * Math.sin(t * 0.67), 0.012);
      w.value = lerp(w.value, aim, 0.05);
      return w.value;
    },
  };
  target.addEventListener('pointermove', (e) => {
    const { clientX } = e as PointerEvent;
    const now = performance.now();
    if (lastX !== null) aim = clamp(aim + ((clientX - lastX) / Math.max(8, now - lastT)) * 0.8, -2.4, 2.4);
    lastX = clientX; lastT = now;
  });
  return w;
}

export interface SequenceStep { from: string; to: string; u: number }

/** A timed sequence of named poses for an interaction (sleep → sit → stretch …). Returns null when finished. */
export function sequence(steps: Array<[name: string, seconds: number]>): (t: number) => SequenceStep | null {
  const total = steps.reduce((a, s) => a + s[1], 0);
  return (t) => {
    if (t < 0 || t >= total) return null;
    let acc = 0, prev = steps[0][0];
    for (const [name, d] of steps) { if (t < acc + d) return { from: prev, to: name, u: (t - acc) / d }; acc += d; prev = name; }
    return null;
  };
}
