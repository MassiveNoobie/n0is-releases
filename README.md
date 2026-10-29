# n0is releases

Public distribution metadata and release tooling for **n0is**, the desktop app. **Neo** is the agent inside n0is.

The app's setup flow prepares three local capabilities:

| Capability | What is installed | Where it comes from |
| --- | --- | --- |
| Neo and the agent crew | A compatible Ollama runtime and the selected local language models | Versioned runtime assets; model weights from their official Ollama distribution |
| Voice | The n0is-compatible Qwen ASR runtime and Qwen3-ASR-0.6B weights | Versioned runtime and model assets with checksums and source attribution |
| Rug | A compatible Rug editor/tool library and its required shared libraries | Versioned, platform-specific runtime asset |

This repository is separate from the application source repository. It contains the public installation contract, checksums, release notes, and packaging helpers. It must not contain user data, credentials, private application source, development databases, or downloaded model weights in Git history.

The initial release target is **macOS 26 or newer on Apple Silicon** (`macos-arm64`), matching the current shared-library builds. Other operating systems and CPU architectures require their own built and tested assets before they can be advertised as supported.

## Release status

The first runtime pack is `runtime-0.1.0`. Its manifest and component archives are published together after verification. Unpublished or incomplete releases are not offered as ready to install.

The app presents three quests: give Neo a brain, add local voice, and open Rug’s diagram tools. Downloads explain what they unlock; completion is earned through a real local model answer, a user-started transcription, and successful opening of a practice board. Installing a file alone does not award XP.

Each published runtime release has an immutable tag, a machine-readable manifest, checksummed component assets, provenance information, and release notes. A small channel document may select a tested release. Existing installations keep working when the network or release service is unavailable.

See [the manifest contract](docs/MANIFEST.md), [the release process](docs/RELEASE_PROCESS.md), [component provenance](docs/PROVENANCE.md), and [third-party notices](THIRD_PARTY_NOTICES.md).

## Model distribution

The setup flow pulls language models through the local Ollama API rather than checking multi-gigabyte weights into Git. The public manifest identifies the selected model and its upstream license. A model's license is independent of Ollama's license.

The initial model profile uses Apache-2.0 models:

| Model | Agent roles | Official source |
| --- | --- | --- |
| `qwen2.5:1.5b` | Neo, drafter | [Qwen2.5-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct) |
| `qwen3:4b` | Checker | [Qwen3-4B](https://huggingface.co/Qwen/Qwen3-4B) |
| `qwen2.5:7b-instruct` | Planner, judge | [Qwen2.5-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct) |

The profile is recorded in [default-models.json](manifests/default-models.json). Models selected outside this profile retain their own terms. In particular, the Qwen project lists Qwen2.5 3B under its separate research license. [Official Qwen2.5 announcement](https://qwenlm.github.io/blog/qwen2.5/)

GitHub release assets are limited to files smaller than 2 GiB. Put large files in release assets or their official upstream distribution, and keep manifests and tooling in Git. [GitHub release limits](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)

## Installation behavior

The app should show which capabilities are ready, the download size, progress, and any actionable error. It verifies a downloaded component before activating it, keeps the previous working installation until the replacement is ready, and checks compatibility rather than treating a file's presence as proof that it works.

Installer-managed files belong in the app's per-user support directory. Existing user-supplied model/runtime choices and saved work are preserved. No terminal, Homebrew installation, source checkout, or developer-specific path should be required for a supported public release.

