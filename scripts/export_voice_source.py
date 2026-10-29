#!/usr/bin/env python3
"""Export the actual n0is-compatible qwen-asr source and patch for a release.

Only files already tracked in the expected public upstream repository are copied.
No .git directory, untracked model weights, build products, or app files are exported.
"""
import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tarfile

UPSTREAM = "https://github.com/antirez/qwen-asr"
PROTOCOL = "neo-asr-snapshots-v1"


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args])


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("runtime", type=Path)
    p.add_argument("--version", required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._+-]{0,95}", args.version):
        p.error("version must be a release token")
    root = args.runtime.resolve(strict=True)
    remote = git(root, "remote", "get-url", "origin").decode().strip().removesuffix(".git")
    if remote != UPSTREAM:
        p.error("runtime origin is not the expected public qwen-asr repository")
    revision = git(root, "rev-parse", "HEAD").decode().strip()
    names = sorted(x.decode() for x in git(root, "ls-files", "-z").split(b"\0") if x)
    changed = [x.decode() for x in git(root, "diff", "HEAD", "--name-only", "-z").split(b"\0") if x]
    files = {}
    links = {}
    for name in names:
        relative = PurePosixPath(name)
        if relative.is_absolute() or ".." in relative.parts or ".git" in relative.parts:
            p.error("unsafe tracked source path")
        source = root / name
        if source.is_symlink():
            target = os.readlink(source)
            try:
                source.resolve(strict=True).relative_to(root)
            except (ValueError, OSError):
                p.error("tracked source link escapes its root: " + name)
            if PurePosixPath(target).is_absolute():
                p.error("tracked source link is absolute: " + name)
            links[name] = target
            files[name] = target.encode()
            continue
        if not source.is_file():
            p.error("source export requires regular tracked files: " + name)
        files[name] = source.read_bytes()
    if b"neo-asr-snapshots-v1" not in files.get("main.c", b""):
        p.error("source does not include the required n0is voice protocol")
    patch = git(root, "diff", "--no-ext-diff", "--binary", "HEAD", "--")
    if b"/Users/" in patch:
        p.error("source patch includes a local user path; inspect before export")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    basename = f"n0is-qwen-asr-{args.version}"
    patch_path = args.output_dir / f"{basename}.patch"
    patch_path.write_bytes(patch)
    source_info = {
        "upstream": UPSTREAM, "upstream_revision": revision,
        "upstream_source": f"{UPSTREAM}/tree/{revision}",
        "protocol": PROTOCOL, "changed_files": sorted(changed),
        "source_files": {name: digest(data) for name, data in files.items()},
        "source_symlinks": links,
        "patch_sha256": digest(patch), "license": "MIT",
        "build": ["make blas", "./qwen_asr --neo-protocol"],
    }
    notice = ("n0is voice runtime source\n\n"
              f"Upstream: {UPSTREAM} at {revision}\n"
              f"This source includes n0is snapshot-protocol changes ({PROTOCOL}).\n"
              "Changed files: " + ", ".join(sorted(changed)) + "\n"
              "The upstream MIT license is retained in LICENSE.\n"
              "This archive contains runtime source only; model weights are distributed separately.\n")
    files["N0IS-SOURCE.json"] = (json.dumps(source_info, indent=2) + "\n").encode()
    files["N0IS-NOTICE.txt"] = notice.encode()
    archive_path = args.output_dir / f"{basename}-source.tar.gz"
    with archive_path.open("wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as compressed:
        with tarfile.open(fileobj=compressed, mode="w") as archive:
            for name, data in sorted(files.items()):
                entry = tarfile.TarInfo(f"{basename}/{name}")
                entry.size = len(data)
                entry.mode = 0o755 if name.endswith((".sh", ".py")) else 0o644
                entry.mtime = entry.uid = entry.gid = 0
                if name in links:
                    entry.type = tarfile.SYMTYPE
                    entry.linkname = links[name]
                    entry.size = 0
                    archive.addfile(entry)
                else:
                    archive.addfile(entry, io.BytesIO(data))
    source_info["source_archive"] = {"file": archive_path.name, "sha256": digest(archive_path.read_bytes()), "bytes": archive_path.stat().st_size}
    source_info["patch"] = {"file": patch_path.name, "sha256": digest(patch), "bytes": len(patch)}
    provenance_path = args.output_dir / f"{basename}-provenance.json"
    provenance_path.write_text(json.dumps(source_info, indent=2) + "\n")
    print(json.dumps({"archive": str(archive_path), "patch": str(patch_path), "provenance": str(provenance_path),
                      "tracked_source_files": len(names), "changed_files": sorted(changed)}))


if __name__ == "__main__":
    main()
