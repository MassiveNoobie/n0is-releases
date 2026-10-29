# Component provenance

Every release needs a provenance record based on its actual built assets. Keep one record per component/version/platform. Do not infer provenance from a file name or copy a developer's local path into a public record.

Record:

| Field | Required evidence |
| --- | --- |
| Component and version | Product component ID, release version, platform, and minimum OS version |
| Source | Public source repository and exact immutable revision; for model weights, official model ID and immutable model revision |
| Changes | Source or a patch for modifications to third-party code, including the n0is voice snapshot protocol extension |
| Build | Compiler/toolchain, build options, and reproducible build or packaging instructions |
| Runtime interface | Supported voice protocol or Rug host interface and its compatibility checks |
| Dependencies | Exact shared libraries/frameworks carried in the package, their versions and source locations |
| Licenses | The actual licenses and notices that apply to every redistributed component |
| Asset integrity | Published asset filename, byte count, and SHA-256 generated from the final uploaded file |
| Validation | Target hardware/OS and the component smoke-test results |

## Voice source

The voice runtime is based on [antirez/qwen-asr](https://github.com/antirez/qwen-asr), but n0is uses a snapshot protocol extension. The unmodified upstream source alone does not identify the binary that the app expects. Publish the corresponding modified runtime source or a patch with each applicable runtime release and retain the upstream license.

Maintainers can export the actual source, its patch, and a per-file provenance record with:

```sh
python3 scripts/export_voice_source.py /path/to/qwen-asr --version 0.1.0 --output-dir dist
```

This helper accepts only the expected public upstream repository and exports its tracked files with the current tracked modifications. It excludes untracked weights, build artifacts, and the Git database. The generated archive records its protocol, exact upstream revision, changed files, and source-file checksums.

The initial model is [Qwen/Qwen3-ASR-0.6B](https://huggingface.co/Qwen/Qwen3-ASR-0.6B). Its model card identifies an Apache-2.0 license. Pin and record the model revision and every distributed file's actual hash.

## Rug and Qt

Rug's source carries an MIT license. The public asset also needs the appropriate notices and source information for its bundled Qt modules and other dependencies. The license for Rug does not replace the licenses for those dependencies. Record the actual Qt modules and versions used by the build. [Qt licensing](https://doc.qt.io/qt-6/licensing.html)

## App binary

The n0is app's distribution terms are separate from runtime component licenses. Publishing this release repository does not by itself publish the private application source or grant a license to that source.

