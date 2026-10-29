# Third-party components

Each downloadable component must carry its own applicable license and attribution files. This inventory describes sources; it does not substitute for the license text accompanying a particular release.

| Component | Source | License information |
| --- | --- | --- |
| Ollama runtime | [ollama/ollama](https://github.com/ollama/ollama) | [MIT license](https://github.com/ollama/ollama/blob/main/LICENSE); include the actual license for the redistributed version |
| Qwen ASR runtime | [antirez/qwen-asr](https://github.com/antirez/qwen-asr) | Include its upstream license and source/patch details for n0is protocol modifications |
| Qwen3-ASR-0.6B weights | [Official Qwen model card](https://huggingface.co/Qwen/Qwen3-ASR-0.6B) | Apache-2.0 per model card; retain the pinned revision's license and notices |
| Neo language models | Official model distribution selected by the manifest | Model-specific; do not substitute Ollama's MIT license for the model's license |
| Rug | Corresponding released Rug source | MIT; retain the source license supplied with each release |
| Qt and its dependencies | [Qt licensing](https://doc.qt.io/qt-6/licensing.html) | Depends on modules and distribution; include actual notices and corresponding source information for the released build |

No downloaded models, third-party binaries, or private application code are covered by an assumed blanket license from this repository.
