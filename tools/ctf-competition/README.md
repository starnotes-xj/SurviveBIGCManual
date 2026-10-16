# CTF Competition Skill

Reusable Agent Skill for Claude Code, OpenCode, and Codex CLI, with a prompt adapter for Cairn. In a real competition, work every challenge in each authorized category; the one-challenge-per-category cap applies only to scoped test runs such as the DataCon 214 preliminary-round test (categories shown on the official stage page except Theory/理论).

## Use in this repository

- Codex CLI and OpenCode: this skill is under `.agents/skills/ctf-competition/`.
- Claude Code: a synchronized project copy is present under `.claude/skills/ctf-competition/`; re-run the copy command below after editing the canonical skill.
- Cairn: the current bundled source appends its `competition_tooling.md` to default analysis prompts; that prompt has been updated with the compact adapter. See `references/cairn.md` before applying to another Cairn version.

## Install for Claude Code

From the repository root, run:

```powershell
New-Item -ItemType Directory -Force .claude/skills/ctf-competition | Out-Null
Copy-Item -Path .agents/skills/ctf-competition/* -Destination .claude/skills/ctf-competition -Recurse -Force
```

Codex CLI and OpenCode can use the project skill directly. For a different repo, copy the folder to its `.agents/skills/ctf-competition/` and, for Claude Code, also `.claude/skills/ctf-competition/`.

For another Cairn checkout, append `adapters/cairn/competition_tooling.md` to the prompt resource that its dispatcher actually loads. The edited local Cairn prompt is in the deployment bundle under `outputs/Cairn-CTF-队友部署包/`; verify its loader before copying this integration to another version.

The latest standalone share package is `outputs/ctf-competition-skill-portable-vnc.zip`. It contains the `ctf-competition/` skill directory and excludes generated Python caches.

## Safety extractor

The standard-library-only `scripts/safe_extract.py` supports ZIP and TAR variants. It rejects traversal/absolute paths, links and special files, collisions, Windows device/ADS names, more than 2,000 entries, or more than 200 MiB compressed/uncompressed by default. The archive must be reviewed first; extraction does not make its contents trusted or safe to execute.

```powershell
python .agents/skills/ctf-competition/scripts/safe_extract.py .\challenge.zip --destination .\artifacts\challenge\extracted
```

## Multiple AI sessions with a single-login platform and VNC

Use one authenticated Chrome/Edge process and one browser context inside the authorized environment. When the user delegates competition login/takeover, the Skill authorizes accepting ordinary required account/service and privacy acknowledgements for that event, but not payment, public posting, unrelated data-sharing, or waivers. Each AI session attaches to the same context, owns a unique page/tab ID, and receives a separate challenge/machine. Do not launch another Chrome or log in again. VNC may use internal device tabs inside one topology page, official deep links in separate Chrome tabs, or a Guacamole bastion console opened from an asset list (Qianxin UHA experience, including per-tab CDP certificate handling and RDP single-session conflicts, is in `references/browser-and-vnc.md`); verify the platform's actual structure. Never duplicate the same machine. Use a shared assignment/page ledger and serialize VNC input across consoles unless page-scoped controls are proven independent:

```powershell
python .agents/skills/ctf-competition/scripts/vnc_gate.py acquire --state-dir .ctf-coordination/datacon-account --owner codex-crypto --target ops-kali-01
python .agents/skills/ctf-competition/scripts/vnc_gate.py status --state-dir .ctf-coordination/datacon-account --target ops-kali-01
python .agents/skills/ctf-competition/scripts/vnc_gate.py release --state-dir .ctf-coordination/datacon-account --owner codex-crypto --target ops-kali-01
```

Take and share a screenshot/output after each VNC batch, then release the gate. A stale lock must not be cleared until the previous controller is confirmed stopped. The gate coordinates only cooperating sessions that share the same filesystem; it does not enforce browser authentication or prevent a separate uncoordinated login. If the runner cannot attach to the same browser process/context, serialize its platform browsing instead of launching another Chrome.

## Model preferences

The skill recommends the user's configured DeepSeek Flash-class model for routine solving, GPT-6 Sol high/xhigh for difficult derivation/review, and GPT-6 Astra only for unusually hard cases. These are routing preferences, not guaranteed model IDs or a capability to switch models. Configure separate workers in the chosen runner and verify the exact provider/model names there. Never place API keys in this package.

## Current test boundary

In a real competition, inspect the official rules and visible category list and work every challenge in each authorized category until solved or genuinely stuck. For the user's DataCon scoped test, skip Theory/理论 and test at most one challenge in each remaining category. Determine from the actual stage UI whether separate category pages in one authenticated browser context remain independent; do not assume parallelism from URLs alone. Do not scan the platform or attack infrastructure. If performing the requested post-event submit test, try one verified flag once through the visible UI; if the control is disabled, record submission unavailable and do not bypass it through an API/network request or altered client state.
