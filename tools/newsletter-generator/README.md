# Newsletter Generator (offline, local)

A single self-contained HTML file for building a newsletter-style web page.
No install, no server, no internet connection — everything runs in your
browser and nothing ever leaves your computer.

## Use it

Double-click `index.html` (or open it from your browser with File → Open)
to launch the tool. There's nothing to build or serve.

- Fill in the masthead (title, subtitle, issue label, date, accent color, font).
- Add content blocks — heading, paragraph, image, quote, button link, divider —
  and reorder or delete them with the arrows/✕ on each block.
- Images are read from your local disk and embedded directly into the page,
  so the exported file is fully self-contained too.
- The right-hand pane is a live preview of the finished newsletter.

## Dictating a family update

Every paragraph block has two extra buttons:

- **🎤 Dictate** — click to start talking; your words are transcribed live
  into the text box. Click again (now labeled "⏹ Stop") to finish. This uses
  your browser's built-in speech recognition. On Chrome/Edge that typically
  sends audio to the browser's own speech service over the internet to get
  text back (not to this tool or any server of ours); Safari transcribes
  on-device. If you're offline, dictation just won't produce text — the
  status line will say so.
- **✨ Improve flow** — rewrites your rough notes into cleaner prose.
  - If your browser exposes on-device AI (Chrome's built-in Rewriter/Prompt
    API), the rewrite happens entirely on your computer, no internet needed.
  - Otherwise it falls back to a basic local cleanup — removing filler words
    like "um"/"uh"/"like", fixing capitalization and punctuation — which
    always works fully offline but isn't a true AI rewrite.
  - A "↺ Undo rewrite" button appears afterward so you can revert to what
    you dictated if you preferred it.

## Saving your work

- Your draft auto-saves to the browser's local storage as you type, so
  reopening `index.html` later picks up where you left off (on the same
  browser/computer).
- **Save Draft (.json)** downloads an editable copy of your draft so you can
  back it up or move it to another computer. Load it back in with
  **Load Draft (.json)**.
- **Export Web Page (.html)** downloads the finished newsletter as a
  standalone HTML file you can open in any browser, host on a website, or
  attach to an email.
- **Print / Save PDF** opens the finished page in a new tab and triggers
  your browser's print dialog, which can save directly to PDF.

## Why it's offline-only by design

The file loads no external stylesheets, fonts, scripts, or images — only
web-safe system fonts and inline CSS/JS. You can disconnect from the
internet entirely and it will work exactly the same.
