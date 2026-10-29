#!/usr/bin/env python3
"""Generate an install manifest from completed local release archives.

Usage: python3 scripts/make_manifest.py release-input.local.json --output dist/manifest-macos-arm64.json
No upload occurs. File paths in the recipe are relative to the recipe file.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
import tarfile
from urllib.parse import quote, urlsplit

MAX_ASSET_BYTES = 2 * 1024 ** 3
COMPONENT_IDS = {"ollama", "voice", "rug"}
DEFAULT_REPOSITORY = "MassiveNoobie/n0is-releases"


def fail(message):
    raise ValueError(message)


def token(value, name):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._+-]{0,95}", value):
        fail(f"{name} must be a nonempty version/tag token")
    return value


def https(value, name):
    if not isinstance(value, str):
        fail(f"{name} must be an HTTPS URL")
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
        fail(f"{name} must be an HTTPS URL without credentials or fragment")
    return value


def relative(value, name):
    if not isinstance(value, str) or not value or "\\" in value:
        fail(f"{name} must be a relative archive path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or str(path) == ".":
        fail(f"{name} must stay inside the archive")
    return str(path)


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def check_archive(path, entrypoint):
    entries = {}
    with tarfile.open(path, "r:gz") as archive:
        for member in archive:
            # A leading ./ is harmless; paths that escape the root are not.
            name = str(PurePosixPath(member.name))
            if name == "." and member.isdir():
                continue
            relative(name, "archive member")
            if member.ischr() or member.isblk() or member.isfifo():
                fail(f"unsupported archive member: {name}")
            if member.issym() or member.islnk():
                if not member.linkname or PurePosixPath(member.linkname).is_absolute() or "\\" in member.linkname:
                    fail(f"unsafe archive link: {name}")
                target = posixpath.normpath(posixpath.join(posixpath.dirname(name) if member.issym() else "", member.linkname))
                if target == ".." or target.startswith("../"):
                    fail(f"archive link escapes its root: {name}")
            entries[name] = member
    if entrypoint not in entries:
        fail(f"entrypoint {entrypoint!r} is absent from {path.name}")
    if entries[entrypoint].isdir():
        fail(f"entrypoint {entrypoint!r} is a directory")


def build_manifest(recipe, base, repository=DEFAULT_REPOSITORY):
    if not isinstance(recipe, dict):
        fail("recipe must be a JSON object")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        fail("repository must have owner/name form")
    if recipe.get("schema_version") != 1:
        fail("schema_version must be 1")
    release = token(recipe.get("release"), "release")
    if release.lower() in {"latest", "main", "master", "draft"}:
        fail("release must be an immutable release tag")
    if recipe.get("platform") != "macos-arm64":
        fail("this release contract currently supports macos-arm64 only")
    minimum_os = recipe.get("minimum_os")
    if not isinstance(minimum_os, str) or not re.fullmatch(r"\d+\.\d+(?:\.\d+)?", minimum_os):
        fail("minimum_os must be an explicit OS version")
    components = []
    seen = set()
    for source in recipe.get("components", []):
        if not isinstance(source, dict):
            fail("each component must be a JSON object")
        component_id = source.get("id")
        if component_id not in COMPONENT_IDS or component_id in seen:
            fail("component IDs must be unique ollama, voice, and rug")
        seen.add(component_id)
        path_value = source.get("file")
        if not isinstance(path_value, str) or not path_value:
            fail(f"{component_id}: provide the completed local archive in file")
        path = (base / path_value).resolve(strict=True)
        if not path.is_file():
            fail(f"{component_id}: file is not a regular file")
        size = path.stat().st_size
        if size <= 0 or size >= MAX_ASSET_BYTES:
            fail(f"{component_id}: asset must be nonempty and smaller than 2 GiB")
        if source.get("format") != "tar.gz":
            fail(f"{component_id}: format must be tar.gz")
        entrypoint = relative(source.get("entrypoint"), f"{component_id} entrypoint")
        check_archive(path, entrypoint)
        url = source.get("url") or f"https://github.com/{repository}/releases/download/{quote(release, safe='')}/{quote(path.name, safe='')}"
        component = {
            "id": component_id,
            "version": token(source.get("version"), f"{component_id} version"),
            "url": https(url, f"{component_id} URL"),
            "sha256": sha256(path),
            "bytes": size,
            "entrypoint": entrypoint,
            "format": "tar.gz",
            "source_url": https(source.get("source_url"), f"{component_id} source_url"),
            "license_url": https(source.get("license_url"), f"{component_id} license_url"),
        }
        if component_id == "voice":
            if source.get("protocol") != "neo-asr-snapshots-v1":
                fail("voice protocol must be neo-asr-snapshots-v1")
            component["protocol"] = source["protocol"]
        if component_id == "rug":
            if source.get("host_abi") != 1:
                fail("Rug host_abi must be 1")
            component["host_abi"] = 1
        components.append(component)
    if seen != COMPONENT_IDS:
        fail("a complete manifest needs ollama, voice, and rug archives")
    models = []
    tags = set()
    for model in recipe.get("models", []):
        if not isinstance(model, dict):
            fail("each model must be a JSON object")
        tag = model.get("tag")
        if not isinstance(tag, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/-]*", tag) or ":" not in tag or tag in tags:
            fail("models need unique explicit Ollama tags")
        tags.add(tag)
        roles = model.get("roles")
        if not isinstance(roles, list) or not roles or any(not isinstance(x, str) or not re.fullmatch(r"[a-z][a-z0-9_-]*", x) for x in roles) or len(set(roles)) != len(roles):
            fail(f"{tag}: roles must be unique nonempty role names")
        models.append({"tag": tag, "roles": roles, "source_url": https(model.get("source_url"), f"{tag} source_url"),
                       "license_url": https(model.get("license_url"), f"{tag} license_url")})
    if not models:
        fail("a complete manifest needs the selected Neo/Rug models")
    return {"schema_version": 1, "release": release, "platform": "macos-arm64", "minimum_os": minimum_os,
            "components": components, "models": models}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("recipe", type=Path)
    p.add_argument("--repository", default=DEFAULT_REPOSITORY)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    try:
        manifest = build_manifest(json.loads(args.recipe.read_text()), args.recipe.resolve().parent, args.repository)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.output.with_name(args.output.name + ".tmp")
        temporary.write_text(json.dumps(manifest, indent=2) + "\n")
        temporary.replace(args.output)
    except (ValueError, OSError, tarfile.TarError) as error:
        p.exit(1, f"manifest not generated: {error}\n")
    print(json.dumps({"manifest": str(args.output), "release": manifest["release"], "components": len(manifest["components"])}))


if __name__ == "__main__":
    main()

