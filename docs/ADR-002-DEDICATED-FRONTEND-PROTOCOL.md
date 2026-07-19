# ADR-002: Evolve toward a dedicated frontend over Python physics services

- Status: Accepted
- Date: 2026-07-18
- Supersedes: only the frontend destination implied by ADR-001. ADR-001's own plugin/runtime
  decision was later reversed; all simulations now use the plain vertical-slice page pattern.

## Context

Physics Studio must support linked scientific representations, guided lessons, assessments,
notebooks, progress, accessible interaction, and eventually hundreds of simulations. Streamlit
remains productive for Python-authored controls and deployment, but its rerun model and iframe
composition constrain interactions whose state belongs in the browser.

The linked-projectile proof supplied measured evidence rather than a framework preference:

- one coordinated iframe synchronized animation, three graphs, equations, hover, scrubbing, and
  keyboard inspection with zero Streamlit reruns;
- 100 browser seek/update operations averaged below the 16.7 ms frame budget;
- a representative two-run payload was 43,539 bytes at 120 samples per run;
- the bundled runtime was 76,043 bytes and the complete cached document 131,742 bytes;
- Chromium checks verified reduced-motion manual inspection, named controls, live time/value text,
  equation selection, and one shared clock;
- separate player and chart iframes could not provide the same coordination without cross-frame
  messaging and duplicated focus/state handling.

## Options evaluated

| Concern | Improved Streamlit components | Dedicated frontend + Python physics | Evidence and tradeoff |
| --- | --- | --- | --- |
| Linked representations | Possible inside increasingly large custom components | Native shared state and composition | The proof worked only after player, graphs, and equations became one runtime. |
| Accessibility | Good inside one component; fragmented across page/iframes | One focus tree, routing model, and live-region policy | The proof passed, but the iframe remains an accessibility boundary. |
| Mobile UX | Streamlit controls and iframe heights compete for layout | Responsive layout can own the whole lesson/workspace | The 1,080 px pilot iframe is functional, not a credible final mobile composition. |
| State persistence | Python session state is useful but rerun-oriented | Explicit client state synchronized through a protocol | Linked inspection needed no server round trip. Durable progress remains Python-owned. |
| Payload size | Same scientific payload plus self-contained document | Protocol payload can be fetched/cached separately from bundles | Current 43.5 KB payload is acceptable; embedding the 76 KB bundle per document is wasteful. |
| Animation performance | Adequate inside a coordinated component | Adequate with direct browser ownership | Measured seek updates stayed inside a 16.7 ms budget. |
| Contributor complexity | Lowest for Python contributors today | Adds frontend skills and protocol discipline | This is the principal cost; migration must remain simulation-by-simulation. |
| Deployment | One Streamlit process | Static frontend plus Python service/process | Dedicated frontend is more complex and is not introduced in this ADR's foundation stage. |
| Offline use | Existing local Streamlit works | Requires packaged static assets and a local Python service/cache | Neither option is automatically offline-first; preserve local Streamlit until packaging exists. |
| Lessons/assessments | Implemented, but rerun and iframe boundaries grow awkward | Natural routing, focus, responsive composition, and local draft state | Correctness, attempts, progress, and answers remain trusted Python domains. |
| Migration cost | Low immediate, rising component complexity | Higher foundation cost, bounded per plugin | A versioned protocol prevents a flag-day rewrite. |
| Hundreds of simulations | Many page controllers/custom components | Shared shell plus plugin-specific protocol adapters | Only simulations needing rich web interaction should migrate first. |

## Decision

Adopt a dedicated web frontend as the destination while retaining pure Python physics models and
Python-owned grading, notebook, progress, and persistence services. Keep the current Streamlit
application fully operational as the compatibility host during incremental migration.

This ADR does **not** authorize a new frontend application shell, HTTP API, repository-wide page
rewrite, or JavaScript physics implementation. The only immediate foundation is the existing linked
Cannonball representation, and it has exactly one consumer.

Since a second consumer never materialized, the envelope this section originally specified as a
generic "protocol version 1" was renamed to what it actually is: `cannonball/linked_payload.py`'s
single-purpose envelope for the linked-projectile view, with an integer `version` field, simulation
ID and model version, and a JSON payload validated in both Python and JavaScript. It is not a
general mechanism other simulations plug into; treat any future second consumer as a reason to
design a real protocol then, not as something already built.

The linked-projectile representation additionally requires one run per animation track, finite and
equal-length time/position/velocity/acceleration arrays, strictly increasing time, and a positive
duration. Unknown versions fail closed. Python produces all physical samples; JavaScript owns only
presentation state, interpolation/selection, and rendering.

## Compatibility and migration

1. Streamlit continues to route simulations, run their pages, persist profiles, and host lessons.
2. A simulation may add a browser-side payload envelope beside its Python vertical slice. Existing
   renderers remain the fallback and no manifest is mechanically rewritten.
3. Migrate one representation at a time: model result → validated payload envelope → frontend
   consumer. Cannonball linked representations remain the only consumer; a second one has not been
   built and should not be until a concrete experience needs it (see the correction above).
4. A future service transport may deliver the same envelope over HTTP or a local process boundary;
   transport concerns must not change the scientific result contract.
5. Only after a dedicated shell provides equivalent accessibility, profiles, lessons, assessments,
   notebook behavior, offline/local development, and deployment may a migrated route stop using
   Streamlit.

The linked-projectile envelope is single-purpose, single-consumer code, not a versioned
compatibility surface with a deprecation schedule. The current linked iframe embeds its envelope
and does not persist it, so there is no legacy payload to decode.

## Consequences

The direction adds a real protocol maintenance obligation and eventually a second deployable. In
return, browser interaction state can be composed once instead of bridged among Streamlit reruns
and multiple iframes. Python remains the source of scientific truth. Contributors can continue
adding or maintaining ordinary simulations entirely in Python until a concrete experience justifies
frontend migration.

## Non-goals

- Rewriting all simulations or lessons.
- Creating a generalized LMS or enterprise service mesh.
- Duplicating equations, grading, progress, or persistence logic in JavaScript.
- Promising offline-first behavior before a packaged local Python service and asset cache exist.
- Removing Streamlit on a schedule rather than on verified parity.
