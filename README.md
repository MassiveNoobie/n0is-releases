# Neo, voice, and Rug downloads

Download catalog and supporting runtime files for local AI capabilities.

**This repository does not distribute the n0is desktop application.**

[Model/runtime downloads and checksums](https://github.com/MassiveNoobie/n0is-releases/releases/tag/runtime-0.1.0)

| Files | Purpose |
| --- | --- |
| `voice-macos-arm64.tar.gz` | Qwen3-ASR-0.6B speech model and its compatible recognition runtime |
| `rug-macos-arm64.tar.gz` | Optional Rug tool library and its runtime dependencies |
| `manifest-macos-arm64.json` | Versions, download URLs, sizes, checksums, and the three Neo model selections |
| `SHA256SUMS` | Component checksums |
| `n0is-qwen-asr-*` | Corresponding open-source speech-runtime source, patch, and provenance |

Neo's language-model weights are pulled through the official Ollama registry. The selected models are [listed here](manifests/default-models.json). Voice model weights are included in the voice archive.

Initial runtime target: Apple Silicon, macOS 26 or newer.

GitHub automatically adds “Source code (zip)” and “Source code (tar.gz)” links to releases. Those archive this catalog repository's manifests, documentation, licenses, and packaging scripts. They do not contain the desktop application.

See the [manifest contract](docs/MANIFEST.md), [release process](docs/RELEASE_PROCESS.md), [provenance](docs/PROVENANCE.md), and [third-party notices](THIRD_PARTY_NOTICES.md).
