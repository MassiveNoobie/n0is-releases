# Runtime manifest v1

The app reads a UTF-8 JSON manifest from the release channel. The default channel is the latest published release asset named `manifest-macos-arm64.json` in `MassiveNoobie/n0is-releases`. That channel resolves to a manifest whose component URLs use immutable release tags or pinned upstream versions.

The authoritative shape is [manifest.schema.json](../manifests/manifest.schema.json). The initial platform is `macos-arm64` and the initial minimum OS is `26.0`, matching the current redistributed libraries.

| Field | Meaning |
| --- | --- |
| `schema_version` | Exactly `1`; other versions require explicit app support |
| `release` | The immutable n0is runtime release tag |
| `platform` | Exactly `macos-arm64` for this initial contract |
| `minimum_os` | Explicit minimum macOS version |
| `components` | One archive each for `ollama`, `voice`, and `rug` |
| `models` | Explicit Ollama tags, the agent roles they serve, and upstream source/license URLs |

Each component carries `id`, `version`, `url`, `sha256`, `bytes`, `entrypoint`, `format`, `source_url`, and `license_url`. The archive format is `tar.gz`. The voice component also requires `protocol: "neo-asr-snapshots-v1"`. Rug requires `host_abi: 1`.

`bytes` and `sha256` describe the final compressed download, not its extracted contents. `entrypoint` is a relative path inside the extracted root. It must not be absolute or contain parent traversal. The installer verifies the archive before activation and verifies the actual component interface afterward.

## Archive layout

| Component | Entrypoint and contents |
| --- | --- |
| Ollama | `ollama` at the root of the verified upstream `ollama-darwin.tgz`; retain its accompanying libraries |
| Voice | `qwen_asr` at root, plus `qwen3-asr-0.6b/`, provenance, and notices |
| Rug | `PlugIns/libneon_rug.dylib`, plus relocated `Frameworks/` and `PlugIns/platforms/` dependencies |

Archives may contain safe relative shared-library/framework links. They must not contain paths or links that escape the extracted root, device files, or user-specific paths.

## Generate a manifest

Copy [release-input.example.json](../release-input.example.json) to the ignored `release-input.local.json`, then set its component file paths to the completed archives and its release tag to the actual release being prepared. This recipe is a maintainer input template, not an installer manifest.

```sh
python3 scripts/make_manifest.py release-input.local.json --output dist/manifest-macos-arm64.json
python3 scripts/test_make_manifest.py
```

The generator requires every actual file, checks archive paths and entrypoints, and calculates hashes and byte counts. It performs no upload. A generated manifest is not published until its matching assets have been attached to the release and verified.

Language models are pulled using the selected Ollama tags from their upstream distribution. Ollama verifies its model layers. The manifest's archive checksums apply to the runtime component assets; they do not pretend to be hashes of those upstream model downloads.
