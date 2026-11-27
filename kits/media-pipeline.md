# Kit: media pipeline

Code that processes media in bulk: transcription and captions, batch renders and exports, image
processing, audio clean-up, tools that turn one kind of file into another.

## Agents (from Agency Agents, copied into `.claude/agents/`)

| Agent | File | Job |
| --- | --- | --- |
| Voice AI Integration Engineer | `engineering/engineering-voice-ai-integration-engineer.md` | Speech-to-text, captions, voice |
| Video Streaming Engineer | `engineering/engineering-video-streaming-engineer.md` | ffmpeg, encoding, streaming |
| Test Automation Engineer | `testing/testing-test-automation-engineer.md` | Sample files and pipeline tests |
| Code Reviewer | `engineering/engineering-code-reviewer.md` | Reviews each change |
| AI-Generated Code Security Auditor | `security/security-ai-generated-code-auditor.md` | Security review of each change |
| Rust Refactoring Specialist | `engineering/engineering-rust-refactoring-specialist.md` | Only for Rust projects |

## Plugins (see EXTRAS.md)

- **Optional:** `remotion` or `hyperframes` if it renders motion graphics, `ponytail`,
  `mattpocock-skills`.

## Self-check

A sample run on small throwaway files, with the numbers checked (duration, frame count, loudness,
word error rate, file sizes) and the output looked at or listened to. Passing tests are not proof
that a render or transcript is right.

## Preview

The sample output files, plus the app's own screen on its port if it has one.

## Hot files and resources

Hot files: the build manifest (`package.json`, `pyproject.toml`, `Cargo.toml`), the core library's
entry point. Hot resources: the GPU or a local model if only one fits in memory, any shared cache
folder.

## Hands-on (not approved from evidence alone)

Anything that writes to source media or the owner's drives, deletes outputs, uploads, or calls a
paid API in bulk.
