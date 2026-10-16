# Cairn integration and model-routing limits

This workspace's Cairn dispatcher appends `competition_tooling.md` to the default `bootstrap.md`, `explore.md`, and `reason.md` prompt groups. A prompt adapter can therefore make the workflow available to Cairn without pretending Cairn natively loads an Agent Skills directory.

## Model routing

- Cairn workers are selected through the existing worker/task configuration. Use separate configured workers for the routine DeepSeek solver and higher-reasoning GPT reviewer where the installed Cairn version supports those providers.
- The inspected worker schema exposes worker name/type/task types/priority/environment, but no per-task reasoning-effort control. Do not invent `thinking`, `reasoning_effort`, or dynamic model-switch fields.
- Put provider model identifiers and API keys in the user's supported environment/configuration mechanism. Never store real keys in this skill, prompt, task facts, logs, or package.
- If a configured worker cannot run the requested model, say so and continue with the active model only if it can perform the task safely; label any requested escalation as unavailable.

## Runtime handoff

The current Cairn prompt loader adds the shared `competition_tooling.md` file at runtime. The workspace copy has been extended with this skill's authorized-scope, DataCon non-Theory test profile, safe attachment handling, and verification requirements. For a different Cairn checkout/version, verify its prompt loader and copy the adapter into the prompt resource it actually loads; do not assume this path or behavior is universal.

## Parallel Cairn projects or workers

Cairn may run multiple project/worker sessions, but do not give each a separate browser login when the platform account allows only one session. If the runner can attach to the same authenticated browser process/context, assign each worker a distinct page and challenge; different pages may be used in parallel. Keep a shared assignment/page ledger and never let a worker create a separate browser context or reauthenticate.

VNC may appear as platform-owned device tabs inside one topology page or as official deep-linked Chrome tabs per machine; inspect the live UI and verify device labels/desktops. The user's Qianxin run reports that duplicate pages for one machine contend for input, practical capacity was roughly 4–6 sessions, and concurrent console input could fail. These are environment-specific observations, not fixed guarantees. Never open one target twice; use per-target `vnc_gate.py` locks, and serialize input across consoles unless page-scoped control is proven independent. If Cairn cannot attach to the shared authenticated browser context, serialize browser operations rather than launching additional logins. This is a workflow contract, not an OS-level sandbox.
