# YAGNI and scalability audit

This audit records the post-migration disposition of shared abstractions. Repository-wide import
searches were performed before removals; tests are the final compatibility check.

| Candidate | Decision | Evidence and resulting ownership |
|---|---|---|
| Simulation binding and preset framework | **Deleted** | It had one Cannonball demonstration catalog and no runtime consumer. Lessons already own simulation activities and `SimulationSetupRequest` remains the small notebook-to-page handoff. |
| Generic setup handoff | **Actively adopted** | Notebook restoration and Cannonball consume the typed, framework-neutral request. It remains intentionally smaller than a binding registry. |
| Shared integrators | **Actively adopted** | Cannonball, pendulum, spring, double pendulum, and orbital gravity now call shared RK4 or velocity-Verlet steps. Physics outputs remain covered by model tests. |
| Shared constants and unit conversions | **Retained with multiple concrete consumers** | Named SI constants and formatting/conversion functions serve physics models, pages, and tests. Configurable gravity remains a parameter. |
| Gravity and celestial-body preset classes | **Deleted** | They had no production consumers. Slice controls already own the concrete environment choices they present. |
| `examples/free_fall` reference implementation | **Deleted** | It was a second demonstration physics stack used only by contract tests. Those tests now exercise the real Cannonball contract. |
| Generic `models/parameters.py` and `models/results.py` | **Deleted** | They duplicated vertical-slice parameter/result types and had only foundation-test consumers. Shared architecture enums and definitions remain in `models/simulations.py`. |
| Central mission definition file | **Folded into a real current system** | Every slice owns registry and mission declarations in `metadata.py`; the central catalog only discovers, validates uniqueness, and indexes them. Mission evaluation stays in each slice's `missions.py`. |
| Central registry definition tuple | **Folded into a real current system** | Every slice owns `SIMULATION`; `registry.py` discovers the 22 declarations and retains validated lazy page loading. |
| Cannonball lesson under central education package | **Folded into a real current system** | The lesson now lives beside Cannonball as `subjects/mechanics/cannonball/lesson.py`; the curriculum catalog enrolls it without importing a page. |
| Import compatibility modules | **Deleted** | Repository search found no production imports of the seven old accessibility, binding, canvas, mission, and visual paths. Canonical modules have been established since the naming migration. |
| Session-state legacy key migration | **Deprecated temporarily** | Persisted browser/profile state can outlive a release, so narrow key migration remains. Remove only after a documented storage-version cutoff. |
| `SimulationMode.KID` / `EXPERT` contract names | **Deprecated temporarily** | They remain a public contract compatibility surface. Current registered simulations use the four `InteractiveMode` values. |
| Orbital legacy Euler implementation | **Retained with multiple concrete consumers** | It is an intentional numerical-regression comparator used to demonstrate and test integrator quality, not a UI compatibility shim. |
| Empty speed-analogy compatibility exports | **Deleted** | They had no consumers and no verified educational content. Canonical formatting helpers remain. |
| Shared mechanics canvas adapter | **Retained with multiple concrete consumers** | Several mechanics slices use its documented legacy call signature while sharing the current browser scene implementation. |

## Scalability rules

- A new simulation declares navigation and mission metadata in its own `metadata.py`.
- Central catalogs discover, reject incomplete metadata, validate unique IDs, and index; they do not
  accumulate simulation-specific records.
- Lessons live in the vertical slice that anchors them and remain presentation-independent.
- Domain abstractions need either multiple real consumers or a clear domain reason backed by tests.
- Compatibility code requires an identified external or persisted consumer and a removal condition.
- Demonstrations should test real simulation contracts instead of maintaining parallel example
  architectures.
