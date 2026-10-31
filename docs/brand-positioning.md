# Brand positioning and claim truth

Evidence snapshot: **28/09/2026**. Proposed copy for the six named flagships,
not a published profile, new brand master, compliance assessment or product test.
Source links below pin the inspected main revisions; they do not imply that all
main features are in the latest release. [Delivery and checks](visual-rollout-2026-09-28-copy.md).

## Positioning

> Open-source tools for scripting messaging, browser workflows and local services.

Lead with the task the tool performs, then its operating boundary. Avoid claims
of universal safety, institutional trust, speed or adoption. No employer/client
names, availability pitch or vendor-endorsement implication belongs in this copy.

## Six flagship propositions

The qualifier is part of the proposition's usage contract. On a compact card,
keep platform/protocol limits visible and link the full caveat; do not turn the
short sentence into a guarantee by dropping its context.

| Project | Proposed sentence | Required qualifier and implementation evidence |
| --- | --- | --- |
| [wa][WA-R] | Automate personal WhatsApp workflows through a persistent daemon with allowlist and rate controls. | Single-user, QR-paired, unofficial WhatsApp Multi-Device via whatsmeow; not the official Cloud API or a bulk-messaging service. [The safety check][WA-C] checks the allowlist before the limiter. MCP sends default to draft mode, but direct mode exists: do not promise every send needs human approval, immunity from account restrictions, or prevention of all misuse. |
| [fand][FA-R] | Configure temperature-driven fan modes on supported Apple Silicon Macs. | macOS/Apple Silicon hardware and suitable SMC sensors are required. [The adapter][FA-C] chooses **forced minimum or auto**, not arbitrary RPM; auto delegates to macOS thermal management. Do not promise lower temperatures, quieter operation or support for every M-series machine. The README labels its old cast unverified. |
| [anthropic-throttle-proxy][AT-R] | Pace Anthropic API traffic across clients with per-bearer queues and a live dashboard. | Configure queue mode: the documented default is **off**; [fair/reactive enable admission queues][AT-C]. Concurrency and quota feedback are not a universal monetary budget cap, extra subscription capacity, or a promise of no 429s. Provider-specific routes need their own configuration. |
| [claude-mac-chrome][CM-R] | Address Chrome profiles and tabs from macOS scripts without relying on window order. | **macOS only**, visible Chrome, Bash 4+, jq, and Apple Events/JavaScript permissions; README also lists Python 3. [Source][CM-C] reads Local State and stable IDs, but matching uses several signals and fallbacks, including URL overlap: not zero setup, zero dependencies, zero heuristics or infallible account selection. IDs last for the window/tab lifetime, not across restart. |
| [chrome-bridge][CB-R] | Drive a dedicated Chromium profile from a local CLI through an extension and relay. | Requires a compatible unpacked-extension-capable Chromium build and localhost relay. [Debug clicks use chrome.debugger/CDP][CB-C]; this is not a unique event-trust mechanism or fingerprint-evasion guarantee. Respect domain restrictions and explicit action authorization; a dedicated profile does not grant permission to use an account. |
| [kokoro-speakd][KS-R] | Keep Kokoro ready between speech requests, with interruptible local playback. | Single-user Unix-socket daemon, model/language assets and an audio player required. [Source][KS-C] caches language pipelines and preempts playback. **Queued is not audible**: acceptance precedes synthesis/playback; not streaming TTS or a sub-200ms guarantee. The README recommends the Nix path because bare pip dependencies do not establish a complete runtime. |

## Claim matrix

**supported** = the cited source supports this narrowly worded statement, not a
fresh runtime certification. **unsupported** = do not use the current broad
claim; absent proof is not proof of universal failure. **needs measurement** =
plausible outcome, but no suitable measurement in this slice.

| ID | Claim under review | Status | Evidence / safe disposition |
| --- | --- | --- | --- |
| S01 | The six tools implement the mechanisms named in the propositions. | supported | Six READMEs cross-checked against the six implementation links above. Source inspection only; no messaging, SMC, browser or synthesis action executed. |
| S02 | These six root source licenses are Apache-2.0 for wa and MIT for the other five. | supported | Read the pinned LICENSE files in the inventory below. This does not cover every dependency, model, voice, font or artwork. |
| S03 | Published release entries exist for five of the six repositories. | supported | GitHub release inventory below excludes drafts/prereleases. A listed asset is not verified provenance or a tested installation. |
| U01 | The organization is compliance-grade or certified for regulated workloads. | unsupported | No named standard, assessment scope, auditor or certification is established by these sources. Security mechanisms and badges are not compliance certification. Omit. |
| U02 | Every plugin ships SLSA L2/L3, Sigstore and dual SBOMs; all builds are reproducible. | unsupported | Release coverage is uneven: fand's observed release lists one binary; proxy has no published GitHub Release returned. Other releases list SBOM/signature/provenance files, not a fresh verification result. Verify a specific artifact digest, signer/workflow and provenance predicate before claiming a level; reproducibility needs independent matching builds. |
| U03 | Apache-2.0 + MIT throughout the organization and all its media. | unsupported | S02 covers only six source roots. This profile repository has no root LICENSE at the inspected base. Third-party assets and dependencies need separate terms. Do not extend source licenses to the org or its art. |
| U04 | All macOS binaries are pre-notarized. | unsupported | [wa documents unsigned/un-notarized darwin releases][WA-R]; [fand documents ad-hoc signing without Developer ID][FA-R]. Signing, notarization and provenance are distinct. Omit the blanket claim. |
| U05 | Chrome automation requires zero configuration/dependencies and cannot select the wrong account. | unsupported | [claude-mac-chrome requirements and source][CM-C] include jq, Bash/AppleScript, permissions and matching fallbacks. Name the platform and setup rather than claiming universality. |
| U06 | chrome-bridge creates uniquely trusted first-party events or avoids detection. | unsupported | [Input.dispatchMouseEvent through chrome.debugger][CB-C] is CDP input. Neither event trust nor anti-detection superiority was measured. |
| U07 | The proxy guarantees a hard spend ceiling or eliminates upstream rate limits. | unsupported | [Configurable queuing][AT-C] and provider feedback do not create quota or certify a monetary ceiling across every route. Keep the proposition about pacing. |
| U08 | wa makes autonomous messaging unconditionally safe. | unsupported | [Allowlist/rate checks][WA-C] are concrete controls, not guarantees about consent, message content, official platform approval or account sanctions. |
| M01 | kokoro-speakd starts speech in under 200ms; the tools are uniformly fast. | needs measurement | [queued precedes playback][KS-C]. Measure request acceptance, synthesis and audible onset separately, with hardware, text, voice, revision, load, sample count and p50/p95; never reuse old illustrated timing tokens. |
| M02 | fand improves cooling/noise, or a source diagram proves a live browser action. | needs measurement | [fand][FA-R], [claude-mac-chrome][CM-R] and [chrome-bridge][CB-R] explicitly limit their historical media. Require controlled hardware comparisons or isolated real captures, not animations. |
| M03 | Scorecard or star counts demonstrate growth, adoption or trust. | needs measurement | The supplied prior baseline (median Scorecard **6.9**, **6 stars**) is a snapshot, not a trend or user study. It is not remeasured here. Need a dated same-scope series plus usage/retention evidence; a security-practice score is not market demand. |
| M04 | New GPT directions are approved masters or proven to improve conversion. | needs measurement | No artwork is approved by this copy audit. Approval requires the exact rendered asset and a recorded decision; conversion claims additionally require a controlled outcome study. Generation success alone establishes neither. |

## Public source and release inventory

Inspected default-branch commits are pinned in the reference links. Root license
text was read, not inferred from the org profile. Release listings are a
**28/09/2026 observation**, not immutable attestations; no release binary was
executed, cryptographically verified or benchmarked in this slice.

| Repository / source revision | Root source license | Latest published stable GitHub Release observed | Evidence boundary |
| --- | --- | --- | --- |
| wa · `d2efe6d2d64aaeb28911a45858e8237d0a3c5c99` | [Apache-2.0][WA-L] | [v2.3.0][WA-REL] · 07/09/2026 | 22 assets, including platform archives, SBOMs and checksum signature bundle; not a notarization result. |
| fand · `a9930b516fe1898f607529610876912538e35097` | [MIT][FA-L] | [v0.3.4][FA-REL] · 24/04/2026 | One listed asset: fand-aarch64-darwin; no SBOM asset in that release listing. |
| anthropic-throttle-proxy · `fbe39d64057cdad69794ad6e96f30eca36972f38` | [MIT][AT-L] | [No published GitHub Release returned][AT-REL] | Does not establish absence of tags, OCI images or manually dispatched attestations. |
| claude-mac-chrome · `2cc389965b9df9abdc24d840c1190797ff207d92` | [MIT][CM-L] | [v1.1.1][CM-REL] · 12/04/2026 | Six assets, including tarball, intoto, Sigstore, two SBOMs and SHA256SUMS; signatures not verified here. |
| chrome-bridge · `556f59e4325a93e62f4450b09c5d8dc8d5af6b86` | [MIT][CB-L] | [v0.1.0][CB-REL] · 07/05/2026 BRT | Four assets: source archive, checksum, two SBOMs; event behavior cannot be inferred from the release. |
| kokoro-speakd · `f2b6387ceaede3dbd54cbb3f1d2852163016b6a3` | [MIT][KS-L] | [v0.3.0][KS-REL] · 29/05/2026 | Wheel, sdist and two SBOMs. Publication is not proof of complete pip runtime or PEP 740 verification. |

## GPT workflow and asset usage contract

The reusable lesson from **Lectrice and Proso is the process, not permission to
copy their identity**. [Lectrice's public brand spec][LE-B] distinguishes traced
marks, optical cuts and real type; [its finishing record][LE-V] separates vector
checks from actual render inspection. [Proso's geometry amendment][PR-G] discloses
a specific reuse of frozen Lectrice trace bytes, not a blanket authorization for
new generated geometry. Its [editorial-art contract][PR-A] and [palette][PR-P]
separate identity from illustrations and product UI tokens.

The actual prior path is GPT/ChatGPT through the existing **server-hosted browser
fleet**, using gpt-image and its shared authenticated attach helper, not a new
image API client. It serializes the shared composer, verifies a reference upload,
anchors the reply to the submitted prompt and saves the resulting image bytes.
Proso's wrapper adds a prompt/tool/hash provenance sidecar. This was inspected
read-only; no image call, browser attachment, session change or fleet health claim
is made here. A successful generation receipt proves bytes were obtained, not
that the composition, anatomy, palette or identity is correct.

| Asset class | Permitted role after its own review | Consumer obligation |
| --- | --- | --- |
| Existing versioned vector mark / mascot | Reuse the exact approved source for the named brand and surface; deterministically regenerate derivatives. | Pin path, commit and hash; preserve geometry, optical cut, palette and real wordmark typography. Tracing does not make model-origin art hand-drawn. A changed path requires a new review. |
| GPT image direction | Labelled exploration or reference input. | Preserve prompt/reference provenance and generation receipt; inspect the actual image. Do not promote it to logo, favicon, UI icon or site identity because the tool returned success. Do not assume this document approved it. |
| Editorial art / composed banner | A separately accepted illustration, with real type and existing vector marks composited afterward. | Retain image hash and provenance; review at the target crop/size, provide useful alt text, and distinguish illustration from product screenshot, telemetry or benchmark. Publication is a separate gate. |

For **yolo-labz**, start with the existing [YL mark system][YL-B] and
[programming-gremlin grammar][YL-M] at the inspected base. The latter explicitly
assigns the bird motif to Lectrice; importing a bird, Proso's palette or a new
GPT gremlin pose does not amend yolo-labz's identity. This audit does not certify
those existing assets' appearance or approve any newly proposed artwork.

### Attribution and handoff fields

Every consumer should retain the following beside the asset, not in a disposable
scratch directory. This is a provenance contract, **not a new copyright license**.
Public source visibility alone is not permission to reuse every asset. Check
font/art/dependency terms and preserve their required notices; ask the owner for
missing rights before external reuse. Do not describe output as OpenAI-endorsed.

```text
Asset: repo-relative source and derivative paths
Origin: GPT/OpenAI-assisted direction, or the actual non-model origin
Transformation: selected raster → vector trace / composed editorial image / none
Identity source: brand, exact source commit and SHA-256
Generation record: prompt/reference IDs and tool receipt (private IDs kept private)
Typography: real font/version and license; no model-painted wordmark
Review: exact rendered bytes, target sizes/crops, reviewer and recorded decision
Status: exploration / accepted for named use / rejected (never inferred from success)
Usage: named surfaces, required attribution/rights, remaining publication gate
```

Do not invent an image-model version from a ChatGPT UI label. Keep private
account identifiers, chat URLs, credentials and vault excerpts out of public
sidecars. Each surface owner must verify the actual render and its permissions;
copy approval cannot stand in for an artwork or deployment decision.

[WA-R]: https://github.com/yolo-labz/wa/blob/d2efe6d2d64aaeb28911a45858e8237d0a3c5c99/README.md
[WA-C]: https://github.com/yolo-labz/wa/blob/d2efe6d2d64aaeb28911a45858e8237d0a3c5c99/internal/app/safety.go#L5-L28
[WA-L]: https://github.com/yolo-labz/wa/blob/d2efe6d2d64aaeb28911a45858e8237d0a3c5c99/LICENSE
[WA-REL]: https://github.com/yolo-labz/wa/releases/tag/v2.3.0
[FA-R]: https://github.com/yolo-labz/fand/blob/a9930b516fe1898f607529610876912538e35097/README.md
[FA-C]: https://github.com/yolo-labz/fand/blob/a9930b516fe1898f607529610876912538e35097/src/control/adapter.rs#L1-L75
[FA-L]: https://github.com/yolo-labz/fand/blob/a9930b516fe1898f607529610876912538e35097/LICENSE
[FA-REL]: https://github.com/yolo-labz/fand/releases/tag/v0.3.4
[AT-R]: https://github.com/yolo-labz/anthropic-throttle-proxy/blob/fbe39d64057cdad69794ad6e96f30eca36972f38/README.md
[AT-C]: https://github.com/yolo-labz/anthropic-throttle-proxy/blob/fbe39d64057cdad69794ad6e96f30eca36972f38/src/anthropic_throttle_proxy/limiter.py#L687-L825
[AT-L]: https://github.com/yolo-labz/anthropic-throttle-proxy/blob/fbe39d64057cdad69794ad6e96f30eca36972f38/LICENSE
[AT-REL]: https://github.com/yolo-labz/anthropic-throttle-proxy/releases
[CM-R]: https://github.com/yolo-labz/claude-mac-chrome/blob/2cc389965b9df9abdc24d840c1190797ff207d92/README.md
[CM-C]: https://github.com/yolo-labz/claude-mac-chrome/blob/2cc389965b9df9abdc24d840c1190797ff207d92/skills/chrome-multi-profile/chrome-lib.sh#L77-L260
[CM-L]: https://github.com/yolo-labz/claude-mac-chrome/blob/2cc389965b9df9abdc24d840c1190797ff207d92/LICENSE
[CM-REL]: https://github.com/yolo-labz/claude-mac-chrome/releases/tag/v1.1.1
[CB-R]: https://github.com/yolo-labz/chrome-bridge/blob/556f59e4325a93e62f4450b09c5d8dc8d5af6b86/README.md
[CB-C]: https://github.com/yolo-labz/chrome-bridge/blob/556f59e4325a93e62f4450b09c5d8dc8d5af6b86/extension/service-worker.js#L177-L193
[CB-L]: https://github.com/yolo-labz/chrome-bridge/blob/556f59e4325a93e62f4450b09c5d8dc8d5af6b86/LICENSE
[CB-REL]: https://github.com/yolo-labz/chrome-bridge/releases/tag/v0.1.0
[KS-R]: https://github.com/yolo-labz/kokoro-speakd/blob/f2b6387ceaede3dbd54cbb3f1d2852163016b6a3/README.md
[KS-C]: https://github.com/yolo-labz/kokoro-speakd/blob/f2b6387ceaede3dbd54cbb3f1d2852163016b6a3/daemon.py#L96-L347
[KS-L]: https://github.com/yolo-labz/kokoro-speakd/blob/f2b6387ceaede3dbd54cbb3f1d2852163016b6a3/LICENSE
[KS-REL]: https://github.com/yolo-labz/kokoro-speakd/releases/tag/v0.3.0
[LE-B]: https://github.com/phsb5321/Tauri-PDF-Reader/blob/b2797cd0c04d73dabf8a5799bf2f5331462bffc4/docs/brand/brand-spec.md
[LE-V]: https://github.com/phsb5321/Tauri-PDF-Reader/blob/b2797cd0c04d73dabf8a5799bf2f5331462bffc4/docs/brand/vector-finishing.md
[PR-G]: https://github.com/phsb5321/Proso/blob/e0f963a8767db8db69203533126fc72c14dc7b56/brand/GEOMETRY.md
[PR-P]: https://github.com/phsb5321/Proso/blob/e0f963a8767db8db69203533126fc72c14dc7b56/brand/PALETTE.md
[PR-A]: https://github.com/phsb5321/Proso/blob/e0f963a8767db8db69203533126fc72c14dc7b56/docs/visual-assets.md
[YL-B]: https://github.com/yolo-labz/.github/blob/64880882f235922007dd22a0cdb22c7ea5f09f83/profile/assets/brand/README.md
[YL-M]: https://github.com/yolo-labz/.github/blob/64880882f235922007dd22a0cdb22c7ea5f09f83/profile/assets/brand/mascot/README.md
