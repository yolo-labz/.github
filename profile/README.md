# Yolo Labz

**Tools for reading, listening, and making your desktop work for you.**

Start with the task you want to do. Each project has its own installation path,
platform support, and limitations.

## Read with your ears

### [Proso — listen to web pages in Firefox](https://github.com/phsb5321/Proso)

Read articles or selected text aloud, follow word highlighting, and control
playback without leaving the page.

[**Install from Mozilla Add-ons**](https://addons.mozilla.org/en-US/firefox/addon/proso/)
· [Setup and privacy](https://github.com/phsb5321/Proso#installation)

Free to install, not automatically free to synthesize: audio needs your own
provider key, a synthesis host you operate, or an eligible managed plan. There
is no built-in browser TTS fallback. Provider charges may apply.

### [Lectrice — read and annotate local PDFs](https://github.com/phsb5321/Tauri-PDF-Reader)

Keep your place, highlight passages, and optionally listen to them. PDF viewing
works offline; the published v0.2.0 narration path uses ElevenLabs with your own
API key and sends the requested text to that provider.

[**Linux downloads**](https://github.com/phsb5321/Tauri-PDF-Reader/releases)
· [Start here](https://github.com/phsb5321/Tauri-PDF-Reader#lectrice)

Apple-silicon macOS has a separate personal Nix channel, not a notarized public
installer. Windows packages are not published. Current source and tagged
releases can differ; check the project's platform and release notes.

Proso and Lectrice are maintained under [phsb5321](https://github.com/phsb5321).
They are linked here alongside the Yolo Labz repositories; their existing URLs
and ownership have not changed.

## Shape your workspace

| If you want to… | Start with | Before you install |
|---|---|---|
| Hear locally synthesized speech from scripts | [kokoro-speakd](https://github.com/yolo-labz/kokoro-speakd) | A persistent Kokoro daemon; check model, audio and platform setup. |
| Navigate Zellij tabs in a sidebar | [zellij-vertical-tabs](https://github.com/yolo-labz/zellij-vertical-tabs) | A Zellij plugin; the README includes an isolated-session recording. |
| Put application menus in a desktop panel | [noctalia-appmenu](https://github.com/yolo-labz/noctalia-appmenu) | Check the supported shell/toolkit versions; compatibility is not universal. |

## Automate deliberately

| Project | What it does | Boundary |
|---|---|---|
| [wa](https://github.com/yolo-labz/wa) | A WhatsApp CLI and daemon for explicit messaging workflows. | Pairing grants account access. The README demo is unpaired, not a send demonstration. |
| [claude-mac-chrome](https://github.com/yolo-labz/claude-mac-chrome) | Control Chrome profiles on macOS with AppleScript and shell helpers. | macOS-only; review permissions and profile selection first. |
| [chrome-bridge](https://github.com/yolo-labz/chrome-bridge) | Connect a Chrome extension to a local automation relay. | Review its security model; it is not an invisibility or trusted-event guarantee. |

[Browse all Yolo Labz repositories →](https://github.com/orgs/yolo-labz/repositories)

## Try one, tell us where it breaks

Use the chosen project's README for installation and its issue tracker for
problems. Include the version, operating system, expected result, and a minimal
reproduction. Do not attach API keys, private documents, message histories, or
browser profiles.

Licenses, release provenance, and support guarantees are **per project**. Check
the repository and the specific release rather than assuming one policy covers
everything here.

[Engineering notes](https://blog.home301server.com.br)
· [Portfolio](https://portfolio.home301server.com.br)
