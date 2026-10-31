<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/yolo-labz/.github/main/profile/assets/brand/logo-wordmark-dark.svg">
  <img src="https://raw.githubusercontent.com/yolo-labz/.github/main/profile/assets/brand/logo-wordmark-light.svg" alt="yolo-labz" width="300">
</picture>

# Small tools. Deliberate automation.

Open-source tools for scripting messaging, browser workflows and local services.

<img src="https://raw.githubusercontent.com/yolo-labz/.github/main/profile/assets/brand/rollout/gremlin-wide-hero.png" alt="Green programming gremlin with pointed ears and a fanged grin typing on a keyboard, with mauve code accents" width="640">

*GPT-generated gremlin exploration — an illustration proposal, not an approved brand master.*

## Start with a task

### Connect your workflows

- **[wa](https://github.com/yolo-labz/wa)** — personal WhatsApp workflows with allowlist and rate controls.
  Single-user, QR-paired, unofficial Multi-Device; not the Cloud API or a bulk-messaging service.
- **[chrome-bridge](https://github.com/yolo-labz/chrome-bridge)** — drive a dedicated Chromium profile from a local CLI.
  Requires a compatible unpacked-extension-capable browser, extension and localhost relay.

### Work on your Mac

- **[claude-mac-chrome](https://github.com/yolo-labz/claude-mac-chrome)** — address Chrome profiles and tabs from scripts without relying on window order.
  macOS only; visible Chrome, Bash 4+, jq, Python 3 and automation permissions required. IDs last for the tab/window lifetime.
- **[fand](https://github.com/yolo-labz/fand)** — configure temperature-driven fan modes on supported Apple Silicon Macs.
  macOS and suitable SMC sensors required; forced-minimum or automatic modes, not arbitrary RPM.

### Keep services ready

- **[kokoro-speakd](https://github.com/yolo-labz/kokoro-speakd)** — keep Kokoro ready between speech requests, with interruptible local playback.
  Single-user Unix-socket daemon; model assets and an audio player required. Queued does not mean audible.
- **[anthropic-throttle-proxy](https://github.com/yolo-labz/anthropic-throttle-proxy)** — pace Anthropic API traffic across clients with per-bearer queues and a live dashboard.
  Enable fair/reactive queue mode; the default is off. Pacing does not create provider quota.

### Read and listen

- **[Proso](https://github.com/phsb5321/Proso)** — read a page or a selection aloud in Firefox, with word highlighting and playback controls.
  Audio needs your own provider key, a synthesis host you run, or an eligible managed plan. There is no built-in browser TTS fallback and provider charges may apply.
- **[Lectrice](https://github.com/phsb5321/Tauri-PDF-Reader)** — keep your place in local PDFs, highlight passages and optionally listen to them.
  PDF viewing works offline; the published v0.2.0 narration path uses ElevenLabs with your own key and sends the requested text to that provider. Apple-silicon macOS gets a personal Nix channel rather than a notarized installer, and Windows packages are unpublished.

Both live under [phsb5321](https://github.com/phsb5321) and are linked here as-is: ownership and URLs are unchanged.

### Shape your workspace

- **[zellij-vertical-tabs](https://github.com/yolo-labz/zellij-vertical-tabs)** — list Zellij tabs in a sidebar that survives heavy load.
  A Zellij plugin, not a standalone binary; match the plugin version to your Zellij release.

Each project's README has its installation path, operating limits and license.
Choose one tool, check its requirements, then build from there.

## Report where it breaks

Use the project's README for installation and its issue tracker for problems. Include the version, operating system, expected result and a minimal reproduction. Never attach API keys, private documents, message histories or browser profiles.

[Browse all Yolo Labz repositories →](https://github.com/orgs/yolo-labz/repositories)
