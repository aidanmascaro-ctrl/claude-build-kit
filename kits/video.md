# Kit: video

Edits, reels, motion graphics and animated explainers: either made from code (Remotion,
HyperFrames) or edited in an editor that Claude can drive (DaVinci Resolve Studio).

## Agents (from Agency Agents, copied into `.claude/agents/`)

| Agent | File | Job |
| --- | --- | --- |
| Short-Video Editing Coach | `marketing/marketing-short-video-editing-coach.md` | Pacing, hooks, cut choices, reels |
| Video Streaming Engineer | `engineering/engineering-video-streaming-engineer.md` | ffmpeg, codecs, exports, proxies |
| Minimal Change Engineer | `engineering/engineering-minimal-change-engineer.md` | Small script fixes |
| Code Reviewer | `engineering/engineering-code-reviewer.md` | Reviews scripts and code |

## Plugins (see EXTRAS.md)

- **Video from code:** `remotion` (React-based video) or `hyperframes` (HTML-based video: captions,
  explainers, product launches).

## Tools

`ffmpeg` (`brew install ffmpeg` on a Mac). For video from code, Node.js. To drive DaVinci
Resolve, you need **Resolve Studio** (the paid version) with external scripting turned on in its
preferences, and an MCP server that connects Claude to it. Recent versions of Resolve Studio
include one; Blackmagic's documentation says how to turn it on.

## Self-check

Rendered stills and short clips at the changed points, checked frame by frame, plus the numbers
that matter (duration, frame count, resolution, audio loudness). For an editor, read back every
setting the change made. Never on the owner's source media: work on a duplicated timeline or a
scratch project.

## Preview

The rendered stills and clip, sent to the owner. Anything only visible inside the editor needs
them at their computer.

## Hot files and resources

Hot resource: **the video editor** (one task at a time, always), and the media drive. For
code-based video, the composition's root file and `package.json`.

## Hands-on (not approved from evidence alone)

Everything that changes a project in the editor, a timeline, a grade, or media on the owner's
drives. Final exports and uploads.
