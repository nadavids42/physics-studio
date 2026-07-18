// Transitional bridge for scene bundles loaded after the shared player runtime.
// Keeping this seam explicit makes scene dependencies testable without rebundling the runtime.
export const PhysicsAnimation = globalThis.PhysicsAnimation;
export const PhysicsAnnotations = globalThis.PhysicsAnnotations;
export const PhysicsAssets = globalThis.PhysicsAssets;
export const PhysicsExperience = globalThis.PhysicsExperience;
export const PhysicsVisuals = globalThis.PhysicsVisuals;
export const sample = globalThis.sample;
