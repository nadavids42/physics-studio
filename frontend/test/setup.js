const calls = [];

function library(prefix) {
  return new Proxy(
    {},
    {
      get(_target, name) {
        return (...args) => {
          calls.push({ kind: `${prefix}.${String(name)}`, args });
          if (name === "profile") {
            return {
              depth: true,
              environment: false,
              preserveScientificOverlays: true,
            };
          }
          if (name === "context") {
            return {
              depth: true,
              environment: false,
              preserveScientificOverlays: true,
            };
          }
          if (name === "level")
            return args[0]?.config?.presentationLevel || "illustrated";
          if (name === "responsive")
            return args[0]?.transform?.width <= 480 ? "mobile" : "desktop";
          if (name === "token") return args.at(-1);
          return undefined;
        };
      },
    },
  );
}

globalThis.__sceneCalls = calls;
globalThis.PhysicsAnimation = library("animation");
globalThis.PhysicsAnnotations = library("annotations");
globalThis.PhysicsAssets = library("assets");
globalThis.PhysicsExperience = library("experience");
globalThis.PhysicsVisuals = library("visuals");
globalThis.sample = (values, fraction) => {
  if (!values.length) return 0;
  const index = Math.max(0, Math.min(1, fraction)) * (values.length - 1);
  const lower = Math.floor(index);
  const upper = Math.min(values.length - 1, lower + 1);
  return values[lower] + (values[upper] - values[lower]) * (index - lower);
};
