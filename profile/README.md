# yolo-labz

AI-native automation tooling for high-leverage operators — built compliance-grade: build provenance, signed attestations, and hard rate/cost ceilings are first-class citizens, not bolted on after the demo.

Plugin family for Claude Code, system daemons for macOS / Linux, and infra recipes that compose. Apache-2.0 + MIT throughout. SLSA L2 + Sigstore + reproducible builds.

## Plugins (Claude Code)

| Plugin | Stack | Purpose |
|--------|-------|---------|
| [wa](https://github.com/yolo-labz/wa) | Go · whatsmeow · SQLite · JSON-RPC | WhatsApp daemon with append-only safety, allowlist + rate limiter + warmup ramp. Built so an LLM can use it without becoming a vector for spam or impersonation. |
| [claude-mac-chrome](https://github.com/yolo-labz/claude-mac-chrome) | Bash · AppleScript · TypeScript | Multi-profile Chrome control on macOS. Reads Chrome's Local State catalog + drives React/Ember SPAs via cliclick at computed screen coords. Zero user configuration. |
| [linkedin-chrome-copilot](https://github.com/yolo-labz/linkedin-chrome-copilot) | TypeScript · Anthropic SDK | LinkedIn copilot: five user-stories (resume, draft-reply, book-slot, CV tailor, guardrails). Per-channel tone + transport + validation. PII-scanner CI gate. |
| [kokoro-speakd](https://github.com/yolo-labz/kokoro-speakd) | Python · ONNX | Persistent Kokoro TTS daemon. Loads model once, serves over unix socket. Sub-200ms warm-call latency. PyPI-published with PEP 740 attestations. |
| [claude-classroom-submit](https://github.com/yolo-labz/claude-classroom-submit) | Python · Google Classroom API | Bypasses Drive Picker iframe via REST API + OAuth 2.0. End-to-end submission < 5s. |
| [fand](https://github.com/yolo-labz/fand) | Rust · launchd | Apple Silicon thermal daemon. Temperature-driven curves, SIGHUP reload, exact-pin reproducible builds. |
| [anthropic-throttle-proxy](https://github.com/yolo-labz/anthropic-throttle-proxy) | Python · HTMX | Self-hosted throttle proxy for the Anthropic API: AIMD rate ceiling for an agent fleet, live saturation dashboard, advisor loop. The spend/429 guardrail everything else runs behind. |

## Composition

Plugins compose. `linkedin-chrome-copilot` uses `claude-mac-chrome` for browser routing. Both sit alongside `wa` for cross-channel pipelines. `kokoro-speakd` narrates agent status without per-call model-load latency. `fand` keeps the laptop cool while all of the above run in parallel.

The agent loop becomes a graph of specialized capabilities, not a monolithic chat assistant.

## Distribution + supply chain

`gh attestation verify <artifact> --owner yolo-labz`: one command, no cosign install, confirms a release artifact was built by this org's CI from the tagged source. Every plugin's release pipeline produces:

- SLSA L2 build provenance via `actions/attest-build-provenance` (GitHub-native attestations; `claude-mac-chrome` adds SLSA L3 via `slsa-github-generator`)
- Dual SBOM: CycloneDX 1.7 + SPDX 2.3 (`syft` / `anchore/sbom-action`)
- Reproducible builds: `SOURCE_DATE_EPOCH`, `-trimpath`, `-buildvcs=true` where the toolchain supports it

Python plugins (`kokoro-speakd`, `claude-classroom-submit`) publish to PyPI via Trusted Publishing with PEP 740 attestations.

CI is hardened across every repo: SHA-pinned actions (40-char) with version comments, `permissions: {}` deny-all + per-job re-grant, and `step-security/harden-runner` egress auditing.

## Tap

`brew install yolo-labz/tap/<plugin>` for CLI tools. Pre-notarized macOS binaries built from a Linux runner via `rcodesign`.

```bash
brew tap yolo-labz/tap
brew install yolo-labz/tap/wa
```

## Constitution

Each repo carries a `constitution.md` (under `.specify/memory/`) with binding rules: hexagonal core, daemon owns state, no `--force` ever, CGO_ENABLED=0 where applicable, conventional commits, signed tags. Spec-driven development with citations: every "best practice" claim links to a primary source.

## Author

[Pedro Balbino](https://github.com/phsb5321) · Senior SWE specializing in AI-native automation. Engineering writeups + plugin demos at [blog.home301server.com.br](https://blog.home301server.com.br) · portfolio at [portfolio.home301server.com.br](https://portfolio.home301server.com.br) · LinkedIn [balbinopedro](https://linkedin.com/in/balbinopedro).
