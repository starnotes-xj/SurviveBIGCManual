# Competition workflow and evidence layout

## Per-challenge workspace

Keep competition materials isolated by event, round, and challenge. Suggested layout:

```text
artifacts/<event>/<round>/<category>-<challenge-slug>/
  challenge.md       # statement and task metadata; redact secrets
  original/          # untouched official downloads
  extracted/         # safe extraction output
  evidence/          # hashes, file/type output, relevant logs
  solve.py|sage      # reviewed, reproducible solver
  result.txt         # verified result; protect if competition rules require
  notes.md           # hypotheses, tests, and remaining uncertainty
```

Do not put credentials, cookies, access tokens, or browser storage state in this tree. Never overwrite the original archive.

## Parallel AI sessions and shared browser/VNC

Run one authenticated Chrome/Edge process inside the authorized environment. Attach each AI session to that same browser context and assign a unique page ID plus challenge; never start another browser/profile or sign in again. Different pages can navigate, inspect, and download in parallel, with each agent writing only to its assigned challenge directory. Keep a shared `talk.txt`/task ledger to prevent duplicate challenge assignments and page ownership collisions. Agents return:

1. observed challenge inputs and file hashes;
2. the hypothesis/derivation and rejected approaches;
3. a reproducible solver and its run output;
4. independent verification and a candidate flag, if recovered.

Agents may analyze evidence and prepare next actions in parallel. Assign each VNC page to its operator-machine target; different verified machines may be controlled concurrently, while sessions targeting the same machine must serialize input with `vnc_gate.py` using that same target alias. If the browser connector relies on global focus or input, serialize those operations as well. Capture/share each result before releasing that machine's gate. Assign one submitter per challenge and serialize submissions for the same challenge. See `browser-and-vnc.md` for same-context attachment, per-machine VNC gating, and recovery details.

## Attachment acquisition

1. Navigate only from the official event/challenge page, after confirming the event and category.
2. Use the browser's authenticated download flow. Save the exact filename and source challenge. If a link redirects outside the event's expected domain, pause and inspect before following.
3. Record SHA-256 and size of each original file. Keep the challenge statement separately.
4. List archive members before extraction. Reject absolute paths, `..`, links, device files, duplicate names, and unexpected huge/nested payloads. Use the bundled extractor, which enforces these checks.
5. Read text/source as data. For binary artifacts, use non-executing tools (`file`, `xxd`, `strings`, metadata parsers) first. Do not `source`, import, run, or install challenge-provided code/dependencies without reviewing them.

## Claim quality

Use these labels in notes and final reports:

- **Observed:** directly present in the challenge page/file/tool output.
- **Inferred:** supported explanation, with the supporting evidence stated.
- **Unverified:** plausible but not reproduced or checked.

A candidate flag is locally verified when an independent local check succeeds. Report platform acceptance separately: only call it accepted/scored after the official UI confirms it. If a post-event submit control remains disabled, record submission as unavailable; do not bypass the UI with a direct API/network request or altered client state. Capture any visible platform response and do not resubmit blindly.
