<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/yolo-labz/.github/main/profile/assets/brand/logo-wordmark-dark.svg">
  <img src="https://raw.githubusercontent.com/yolo-labz/.github/main/profile/assets/brand/logo-wordmark-light.svg" alt="yolo-labz" width="300">
</picture>

# Small tools. Deliberate automation.

Tools for scripting messaging, browser workflows and local services.

> **Integration draft — temporary art placeholder.** GPT gremlin artwork from
> producer p9 is pending. No final GPT artwork is present in this profile yet.

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

Each project's README has its installation path, operating limits and license.
Choose one tool, check its requirements, then build from there.

[Browse all Yolo Labz repositories →](https://github.com/orgs/yolo-labz/repositories)
