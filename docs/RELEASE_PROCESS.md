# Runtime release process

1. Build each component for a specific supported platform. For the first release this is `macos-arm64`.
2. Assemble runtime archives with stable relative layouts. Carry required shared libraries and license notices; exclude local configuration, credentials, databases, training records, and user files.
3. Verify the actual component interfaces. The voice runtime must support `--neo-protocol` and return `neo-asr-snapshots-v1`. Rug must expose the host interface used by this n0is release. The Ollama runtime must start successfully and expose the API expected by the app.
4. Verify the packages on a clean target machine. A build that resolves libraries from `/opt/homebrew`, `/usr/local`, or a developer's home directory is not a portable public asset. System libraries are allowed.
5. Record the exact source revisions, modifications, build configuration, minimum OS version, and included licenses. A local checkout path is not a public source reference.
6. Generate byte counts and SHA-256 checksums from the completed files. Never type checksums or download sizes by hand. Every release asset must be smaller than 2 GiB.
7. Create a draft GitHub release, attach all assets and its manifest, and verify the uploaded bytes. Test the app's setup flow against the draft's equivalent local test endpoint before publishing.
8. Publish the complete release. Update a channel selector only after the published manifest and every asset resolve and the installation smoke tests pass.

Never replace an asset under an existing release tag to ship different bytes. Use a new release tag and retain the old release for rollback and reproducible installation.

Do not publish a placeholder manifest containing made-up hashes or URLs that do not resolve. Do not publish an untested platform or mark a partial install ready.

## Required checks

- Fresh install with no developer tools or existing runtimes.
- Existing installation with compatible components already present.
- Interrupted download and retry.
- Corrupted bytes or mismatched checksum; existing working component remains usable.
- Unsupported platform and incompatible component version; clear, actionable status.
- Offline startup with previously installed components.
- Neo model listing and a local inference request.
- Voice protocol check and a small prerecorded transcription test without requiring microphone access.
- Rug library loading, required host symbols, and a small document/tool operation.

These are release validation requirements. They are not an assertion that the initial repository foundation already passes them.


## Catalog channel

Keep the tested runtime-pack release marked Latest: the app reads its `manifest-macos-arm64.json` asset. App previews are prereleases and must not replace that Latest runtime catalog. A future stable app release must retain the catalog asset or leave the runtime pack marked Latest.
