# Kit: app

Apps people install: Mac and Windows desktop apps, menu-bar utilities, iPhone and Android apps.

Pick the stack by where it must run, and say why in one line:
- **Mac only:** SwiftUI (with AppKit where needed), built with `xcodebuild`.
- **iPhone (and maybe Android):** SwiftUI for iPhone only; React Native or Flutter for both.
- **Mac and Windows:** Tauri or Electron.

If a website would do the job, say so during the pushback interview: it's far simpler to build,
share and update.

## Agents (from Agency Agents, copied into `.claude/agents/`)

| Agent | File | Job |
| --- | --- | --- |
| Desktop App Engineer | `engineering/engineering-desktop-app-engineer.md` | Mac and Windows apps |
| Mobile App Builder | `engineering/engineering-mobile-app-builder.md` | iPhone and Android apps |
| Minimal Change Engineer | `engineering/engineering-minimal-change-engineer.md` | Small fixes |
| Code Reviewer | `engineering/engineering-code-reviewer.md` | Reviews each change |
| AI-Generated Code Security Auditor | `security/security-ai-generated-code-auditor.md` | Security review of each change |
| Reality Checker | `testing/testing-reality-checker.md` | "Is it really done?" |

## Plugins (see EXTRAS.md)

- **Already in the kit:** `unslop` for polishing screens.
- **Optional:** `ui-ux-pro-max` (has SwiftUI, React Native and Flutter guidance), `ponytail`,
  `mattpocock-skills`.

## Tools

Mac and iPhone apps need Xcode (free, from the Mac App Store). The Claude desktop app's iOS
Simulator tools, where available, let a session drive and screenshot an iPhone app. Android needs
Android Studio. Publishing to an app store needs a paid developer account; the owner makes it.

## Self-check

A walkthrough that opens every screen the change touches, with throwaway data, and screenshots
each step: an offscreen UI test for Mac apps, the simulator for iPhone apps, a Playwright run for
Tauri or Electron. Plus the core logic's unit tests.

## Preview

A test build installed beside any real copy, under its own name or bundle ID (e.g.
`com.example.myapp.dev`), so testing never touches the owner's real data.

## Hot files and resources

Hot files: the Xcode project file, `Package.swift` or `package.json`, the app's entry point and
settings. Hot resources: **the test build** (one installed at a time), the simulator.

## Hands-on (not approved from evidence alone)

Anything that moves, deletes or uploads the owner's files; permissions and entitlements; signing,
notarization and store releases; payments.
