# Source provenance

This plugin derives from the Omarchy clipboard implementation:

- Upstream: https://github.com/omacom/omarchy
- Tag: `v4.0.4`
- Commit: `c668141e9c42b13c80c9ca4ea108e11708c5e8a5`
- Source directory: `shell/plugins/clipboard/`
- Original copyright: David Heinemeier Hansson
- License: MIT, preserved verbatim in `LICENSE`

The source files in that tag were compared byte-for-byte with the original
plugin installed by the Omarchy 4.0.4-1 package before the customization.

`ClipboardHistory.js` and `capture.sh` retain the upstream implementation.
`Clipboard.qml` adds ordered multiple text selection, row markers, a combined
preview, stdin clipboard copying, and the corresponding keyboard/mouse actions.
`ClipboardSelection.js`, tests, and repository documentation were added for
this extension. The manifest provides a separate plugin ID while declaring
the native clipboard as its clone source.

Extension and packaging: Copyright (c) 2026 felix-antonio-sl, under the same MIT
license. Upstream authors retain copyright in their original code.
