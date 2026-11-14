# Brand positioning and claim truth

Evidence snapshot: **02/11/2026** (refreshed from 28/09/2026; every repository
below was re-read through the GitHub API that day). Copy for the six public
flagships. It is not a new brand master, compliance assessment or product test.
Source links below pin the inspected default-branch revisions; they do not imply
that all main features are in the latest release.
[Delivery and checks](visual-rollout-2026-09-28-copy.md).

## Positioning

> Open-source tools for scripting messaging, browser workflows and local services.

Lead with the task the tool performs, then its operating boundary. Avoid claims
of universal safety, institutional trust, speed or adoption. No employer/client
names, availability pitch or vendor-endorsement implication belongs in this copy.

## Six flagship propositions

The qualifier is part of the proposition's usage contract. On a compact card,
keep platform/protocol limits visible and link the full caveat; do not turn the
short sentence into a guarantee by dropping its context.

The set is the public, non-archived repositories whose purpose the positioning
sentence covers, each re-checked on 02/11/2026 (`visibility=public`,
`archived=false`, root license present, pushed within the week except where the
inventory says otherwise). A repository is not carried forward because an earlier
version of this document listed it.

| Project | Proposed sentence | Required qualifier and implementation evidence |
| --- | --- | --- |
| [wa][WA-R] | Automate personal WhatsApp workflows through a persistent daemon with allowlist and rate controls. | Single-user, QR-paired, unofficial WhatsApp Multi-Device via whatsmeow; not the official Cloud API or a bulk-messaging service. [The safety check][WA-C] checks the allowlist before the limiter. MCP sends default to draft mode, but direct mode exists: do not promise every send needs human approval, immunity from account restrictions, or prevention of all misuse. |
| [fand][FA-R] | Configure temperature-driven fan modes on supported Apple Silicon Macs. | macOS/Apple Silicon hardware and suitable SMC sensors are required. [The adapter][FA-C] chooses **forced minimum or auto**, not arbitrary RPM; auto delegates to macOS thermal management. Do not promise lower temperatures, quieter operation or support for every M-series machine. The README labels its old cast unverified. |
| [anthropic-throttle-proxy][AT-R] | Pace Anthropic API traffic across clients with per-bearer queues and a live dashboard. | Configure queue mode: the documented default is **off**; `observe` counts upstream throttling without queueing, and [fair/reactive enable admission queues][AT-C]. Concurrency and quota feedback are not a universal monetary budget cap, extra subscription capacity, or a promise of no 429s. Provider-specific routes need their own configuration. |
| [claude-mac-chrome][CM-R] | Address Chrome profiles and tabs from macOS scripts without relying on window order. | **macOS only**, visible Chrome, Bash 4+, jq, and Apple Events/JavaScript permissions; README also lists Python 3. [Source][CM-C] reads Local State and stable IDs, but matching uses several signals and fallbacks, including URL overlap: not zero setup, zero dependencies, zero heuristics or infallible account selection. IDs last for the window/tab lifetime, not across restart. |
| [chrome-bridge][CB-R] | Drive a dedicated Chromium profile from a local CLI through an extension and relay. | Requires a compatible unpacked-extension-capable Chromium build and localhost relay. [Debug clicks use chrome.debugger/CDP][CB-C]; this is not a unique event-trust mechanism or fingerprint-evasion guarantee. Respect domain restrictions and explicit action authorization; a dedicated profile does not grant permission to use an account. |
| [kokoro-speakd][KS-R] | Keep Kokoro ready between speech requests, with interruptible local playback. | Single-user Unix-socket daemon, model/language assets and an audio player required. [Source][KS-C] caches language pipelines and preempts playback. **Queued is not audible**: acceptance precedes synthesis/playback; not streaming TTS or a sub-200ms guarantee. The README recommends the Nix path because bare pip dependencies do not establish a complete runtime. |

### Why zellij-vertical-tabs is not a seventh proposition

Decided on evidence on 02/11/2026; do not reopen without new evidence.

- **It is real and public:** [yolo-labz/zellij-vertical-tabs][ZV-R] is public and
  not archived, with a root [MIT license][ZV-L], 21 commits (last push 31/10/2026),
  0 open issues, and OSV, Scorecard, CodeQL, gitleaks and Sonar workflows.
- **It has a working record, not a release:** the README's Build and Use sections
  give `nix build` or `cargo build --release --target wasm32-wasip1` plus a KDL
  layout snippet. Its demonstration was captured in an isolated Zellij 0.44.3
  session with 26 synthetic tabs and checked by `docs/check-demo.py`
  ([record][ZV-M]). No GitHub Release or tag exists, so there is no packaged
  install path and no version to name. This refresh executed nothing.
- **It does not fit a proposition:** the positioning sentence covers scripting
  messaging, browser workflows and local services. A tab-list sidebar for a
  terminal multiplexer is none of the three, and writing it into a proposition
  would stretch the sentence the other six satisfy.
- **Consequence:** it stays out of the flagship table. The organization profile may
  still list it, but outside the task headings the six occupy, with its own
  qualifier: a Zellij WASM plugin built from source, no release yet. Its claims are
  limited to what [its README][ZV-R] states; "survives heavy load" and any
  Zellij-release compatibility claim are not supported there.

## Claim matrix

**supported** = the cited source supports this narrowly worded statement, not a
fresh runtime certification. **unsupported** = do not use the current broad
claim; absent proof is not proof of universal failure. **needs measurement** =
plausible outcome, but no suitable measurement in this slice.

| ID | Claim under review | Status | Evidence / safe disposition |
| --- | --- | --- | --- |
| S01 | The six tools implement the mechanisms named in the propositions. | supported | Six READMEs cross-checked against the six implementation links above. Source inspection only; no messaging, SMC, browser or synthesis action executed. |
| S02 | These six root source licenses are Apache-2.0 for wa and MIT for the other five. | supported | Read the pinned LICENSE files in the inventory below (and via the repository license API on 02/11/2026). This does not cover every dependency, model, voice, font or artwork. |
| S03 | Published release entries exist for five of the six repositories. | supported | GitHub release inventory below excludes drafts/prereleases. A listed asset is not verified provenance or a tested installation. |
| U01 | The organization is compliance-grade or certified for regulated workloads. | unsupported | No named standard, assessment scope, auditor or certification is established by these sources. Security mechanisms and badges are not compliance certification. Omit. |
| U02 | Every plugin ships SLSA L2/L3, Sigstore and dual SBOMs; all builds are reproducible. | unsupported | Release coverage is uneven: fand's observed release lists one binary; proxy has no published GitHub Release returned. Other releases list SBOM/signature/provenance files, not a fresh verification result. Verify a specific artifact digest, signer/workflow and provenance predicate before claiming a level; reproducibility needs independent matching builds. |
| U03 | Apache-2.0 + MIT throughout the organization and all its media. | unsupported | S02 covers only six source roots. This profile repository has no root LICENSE at the inspected base (re-checked 02/11/2026). Third-party assets and dependencies need separate terms. Do not extend source licenses to the org or its art. |
| U04 | All macOS binaries are pre-notarized. | unsupported | [wa documents unsigned/un-notarized darwin releases][WA-R]; [fand documents ad-hoc signing without Developer ID][FA-R]. Signing, notarization and provenance are distinct. Omit the blanket claim. |
| U05 | Chrome automation requires zero configuration/dependencies and cannot select the wrong account. | unsupported | [claude-mac-chrome requirements and source][CM-C] include jq, Bash/AppleScript, permissions and matching fallbacks. Name the platform and setup rather than claiming universality. |
| U06 | chrome-bridge creates uniquely trusted first-party events or avoids detection. | unsupported | [Input.dispatchMouseEvent through chrome.debugger][CB-C] is CDP input. Neither event trust nor anti-detection superiority was measured. |
| U07 | The proxy guarantees a hard spend ceiling or eliminates upstream rate limits. | unsupported | [Configurable queuing][AT-C] and provider feedback do not create quota or certify a monetary ceiling across every route. Keep the proposition about pacing. |
| U08 | wa makes autonomous messaging unconditionally safe. | unsupported | [Allowlist/rate checks][WA-C] are concrete controls, not guarantees about consent, message content, official platform approval or account sanctions. |
| M01 | kokoro-speakd starts speech in under 200ms; the tools are uniformly fast. | needs measurement | [queued precedes playback][KS-C]. Measure request acceptance, synthesis and audible onset separately, with hardware, text, voice, revision, load, sample count and p50/p95; never reuse old illustrated timing tokens. |
| M02 | fand improves cooling/noise, or a source diagram proves a live browser action. | needs measurement | [fand][FA-R], [claude-mac-chrome][CM-R] and [chrome-bridge][CB-R] explicitly limit their historical media. Require controlled hardware comparisons or isolated real captures, not animations. |
| M03 | Scorecard or star counts demonstrate growth, adoption or trust. | needs measurement | A star count or security-practice score is a point-in-time number, not a trend or a user study, and none is quoted in this copy. Need a dated same-scope series plus usage/retention evidence; a security-practice score is not market demand. |

## Public source and release inventory

Inspected default-branch commits are pinned in the reference links. Root licenses
were read through the repository license API, not inferred from the org profile.
Release listings are a **02/11/2026 observation** (unchanged from 28/09/2026 for
all six), not immutable attestations; no release binary was executed,
cryptographically verified or benchmarked in this slice. `wa` and
`anthropic-throttle-proxy` are now GitHub mirrors (merge-of-record is a separate
Git host, per their GitHub descriptions); the pins refer to the mirror's default
branch.

| Repository / source revision | Root source license | Latest published stable GitHub Release observed | Evidence boundary |
| --- | --- | --- | --- |
| wa · `f8274f8ba389b4f3519d608885fb531dfda321d8` | [Apache-2.0][WA-L] | [v2.3.0][WA-REL] · 07/09/2026 | 22 assets, including platform archives, SBOMs and checksum signature bundle; not a notarization result. |
| fand · `d281fe2dd32183e5c1b5bb308329413a316da605` | [MIT][FA-L] | [v0.3.4][FA-REL] · 24/04/2026 | One listed asset: fand-aarch64-darwin; no SBOM asset in that release listing. |
| anthropic-throttle-proxy · `bb2bb109a6f0032663d49f9b2e447a75babb8a55` | [MIT][AT-L] | [No published GitHub Release returned][AT-REL] | Does not establish absence of tags, OCI images or manually dispatched attestations. |
| claude-mac-chrome · `1dbedbbf0df5beba78eb443fa92ef8f0f124bdd0` | [MIT][CM-L] | [v1.1.1][CM-REL] · 12/04/2026 | Six assets, including tarball, intoto, Sigstore, two SBOMs and SHA256SUMS; signatures not verified here. |
| chrome-bridge · `860a9eb605ee14f0a095a82bd9ab16285870e0e5` | [MIT][CB-L] | [v0.1.0][CB-REL] · 07/05/2026 BRT | Four assets: source archive, checksum, two SBOMs; event behavior cannot be inferred from the release. |
| kokoro-speakd · `b9850e6cda5812632cc88d587332abc3e62b4dca` | [MIT][KS-L] | [v0.3.0][KS-REL] · 29/05/2026 | Wheel, sdist and two SBOMs. Publication is not proof of complete pip runtime or PEP 740 verification. |
| zellij-vertical-tabs · `da8efee8d2423760306bf4e1292585bd26e3a6c3` (not a flagship) | [MIT][ZV-L] | [No published GitHub Release or tag returned][ZV-REL] | Public, 0 open issues. Install is build-from-source per its README; see the decision above. |

[WA-R]: https://github.com/yolo-labz/wa/blob/f8274f8ba389b4f3519d608885fb531dfda321d8/README.md
[WA-C]: https://github.com/yolo-labz/wa/blob/f8274f8ba389b4f3519d608885fb531dfda321d8/internal/app/safety.go#L5-L28
[WA-L]: https://github.com/yolo-labz/wa/blob/f8274f8ba389b4f3519d608885fb531dfda321d8/LICENSE
[WA-REL]: https://github.com/yolo-labz/wa/releases/tag/v2.3.0
[FA-R]: https://github.com/yolo-labz/fand/blob/d281fe2dd32183e5c1b5bb308329413a316da605/README.md
[FA-C]: https://github.com/yolo-labz/fand/blob/d281fe2dd32183e5c1b5bb308329413a316da605/src/control/adapter.rs#L1-L75
[FA-L]: https://github.com/yolo-labz/fand/blob/d281fe2dd32183e5c1b5bb308329413a316da605/LICENSE
[FA-REL]: https://github.com/yolo-labz/fand/releases/tag/v0.3.4
[AT-R]: https://github.com/yolo-labz/anthropic-throttle-proxy/blob/bb2bb109a6f0032663d49f9b2e447a75babb8a55/README.md
[AT-C]: https://github.com/yolo-labz/anthropic-throttle-proxy/blob/bb2bb109a6f0032663d49f9b2e447a75babb8a55/src/anthropic_throttle_proxy/limiter.py#L702-L876
[AT-L]: https://github.com/yolo-labz/anthropic-throttle-proxy/blob/bb2bb109a6f0032663d49f9b2e447a75babb8a55/LICENSE
[AT-REL]: https://github.com/yolo-labz/anthropic-throttle-proxy/releases
[CM-R]: https://github.com/yolo-labz/claude-mac-chrome/blob/1dbedbbf0df5beba78eb443fa92ef8f0f124bdd0/README.md
[CM-C]: https://github.com/yolo-labz/claude-mac-chrome/blob/1dbedbbf0df5beba78eb443fa92ef8f0f124bdd0/skills/chrome-multi-profile/chrome-lib.sh#L77-L260
[CM-L]: https://github.com/yolo-labz/claude-mac-chrome/blob/1dbedbbf0df5beba78eb443fa92ef8f0f124bdd0/LICENSE
[CM-REL]: https://github.com/yolo-labz/claude-mac-chrome/releases/tag/v1.1.1
[CB-R]: https://github.com/yolo-labz/chrome-bridge/blob/860a9eb605ee14f0a095a82bd9ab16285870e0e5/README.md
[CB-C]: https://github.com/yolo-labz/chrome-bridge/blob/860a9eb605ee14f0a095a82bd9ab16285870e0e5/extension/service-worker.js#L177-L193
[CB-L]: https://github.com/yolo-labz/chrome-bridge/blob/860a9eb605ee14f0a095a82bd9ab16285870e0e5/LICENSE
[CB-REL]: https://github.com/yolo-labz/chrome-bridge/releases/tag/v0.1.0
[KS-R]: https://github.com/yolo-labz/kokoro-speakd/blob/b9850e6cda5812632cc88d587332abc3e62b4dca/README.md
[KS-C]: https://github.com/yolo-labz/kokoro-speakd/blob/b9850e6cda5812632cc88d587332abc3e62b4dca/daemon.py#L96-L347
[KS-L]: https://github.com/yolo-labz/kokoro-speakd/blob/b9850e6cda5812632cc88d587332abc3e62b4dca/LICENSE
[KS-REL]: https://github.com/yolo-labz/kokoro-speakd/releases/tag/v0.3.0
[ZV-R]: https://github.com/yolo-labz/zellij-vertical-tabs/blob/da8efee8d2423760306bf4e1292585bd26e3a6c3/README.md
[ZV-L]: https://github.com/yolo-labz/zellij-vertical-tabs/blob/da8efee8d2423760306bf4e1292585bd26e3a6c3/LICENSE
[ZV-M]: https://github.com/yolo-labz/zellij-vertical-tabs/blob/da8efee8d2423760306bf4e1292585bd26e3a6c3/docs/MEDIA.md
[ZV-REL]: https://github.com/yolo-labz/zellij-vertical-tabs/releases
