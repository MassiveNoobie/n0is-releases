"""Release contract checks using small local archives, without network access."""
import copy
import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

from make_manifest import build_manifest


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        components = []
        for component_id, entrypoint in [("ollama", "ollama"), ("voice", "qwen_asr"), ("rug", "PlugIns/libneon_rug.dylib")]:
            path = self.root / f"{component_id}.tar.gz"
            self.archive(path, entrypoint)
            component = {"id": component_id, "version": "0.1.0", "file": path.name, "entrypoint": entrypoint,
                         "format": "tar.gz", "source_url": "https://github.com/test-owner/source", "license_url": "https://github.com/test-owner/source/blob/v1/LICENSE"}
            if component_id == "voice":
                component["protocol"] = "neo-asr-snapshots-v1"
            if component_id == "rug":
                component["host_abi"] = 1
            components.append(component)
        self.recipe = {"schema_version": 1, "release": "runtime-0.1.0", "platform": "macos-arm64", "minimum_os": "26.0",
                       "components": components, "models": [{"tag": "qwen2.5:1.5b", "roles": ["neo", "drafter"],
                       "source_url": "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct", "license_url": "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct/blob/main/LICENSE"}]}

    def tearDown(self):
        self.temporary.cleanup()

    def archive(self, path, entrypoint, extra=None):
        with tarfile.open(path, "w:gz") as archive:
            member = tarfile.TarInfo(entrypoint)
            member.size = 7
            member.mode = 0o755
            archive.addfile(member, io.BytesIO(b"runtime"))
            if extra:
                archive.addfile(extra)

    def test_integrity_is_generated_from_the_completed_archive(self):
        result = build_manifest(self.recipe, self.root, "test-owner/n0is-fixtures")
        for component in result["components"]:
            data = (self.root / f"{component['id']}.tar.gz").read_bytes()
            self.assertEqual(component["sha256"], hashlib.sha256(data).hexdigest())
            self.assertEqual(component["bytes"], len(data))
            self.assertNotIn("file", component)
            self.assertEqual(component["url"], f"https://github.com/test-owner/n0is-fixtures/releases/download/runtime-0.1.0/{component['id']}.tar.gz")
        self.assertEqual(result["models"], self.recipe["models"])

    def test_missing_asset_and_entrypoint_are_rejected(self):
        recipe = copy.deepcopy(self.recipe)
        recipe["components"][0]["entrypoint"] = "not-in-this-archive"
        with self.assertRaisesRegex(ValueError, "absent"):
            build_manifest(recipe, self.root)
        recipe["components"][0]["file"] = "missing.tar.gz"
        with self.assertRaises(FileNotFoundError):
            build_manifest(recipe, self.root)

    def test_duplicate_or_missing_components_cannot_be_called_complete(self):
        for components in [self.recipe["components"][:2], [self.recipe["components"][0]] * 3]:
            recipe = dict(self.recipe, components=components)
            with self.assertRaises(ValueError):
                build_manifest(recipe, self.root)

    def test_unsupported_platform_or_voice_protocol_is_rejected(self):
        recipe = copy.deepcopy(self.recipe)
        recipe["platform"] = "windows-arm64"
        with self.assertRaisesRegex(ValueError, "macos-arm64"):
            build_manifest(recipe, self.root)
        recipe = copy.deepcopy(self.recipe)
        recipe["components"][1]["protocol"] = "unknown-protocol"
        with self.assertRaisesRegex(ValueError, "voice protocol"):
            build_manifest(recipe, self.root)

    def test_archive_escape_and_absolute_links_are_rejected(self):
        for name in ["../outside", "/outside"]:
            self.archive(self.root / "voice.tar.gz", "qwen_asr", tarfile.TarInfo(name))
            with self.assertRaises(ValueError):
                build_manifest(self.recipe, self.root)
        link = tarfile.TarInfo("bad-link")
        link.type = tarfile.SYMTYPE
        link.linkname = "/outside"
        self.archive(self.root / "voice.tar.gz", "qwen_asr", link)
        with self.assertRaisesRegex(ValueError, "unsafe archive link"):
            build_manifest(self.recipe, self.root)

    def test_relative_framework_links_are_allowed(self):
        link = tarfile.TarInfo("Frameworks/QtCore.framework/QtCore")
        link.type = tarfile.SYMTYPE
        link.linkname = "Versions/A/QtCore"
        self.archive(self.root / "rug.tar.gz", "PlugIns/libneon_rug.dylib", link)
        result = build_manifest(self.recipe, self.root)
        self.assertEqual(result["components"][2]["host_abi"], 1)

    def test_non_https_url_and_credential_urls_are_rejected(self):
        for url in ["http://example.com/runtime", "https://user:password@example.com/runtime"]:
            recipe = copy.deepcopy(self.recipe)
            recipe["components"][0]["url"] = url
            with self.assertRaisesRegex(ValueError, "HTTPS"):
                build_manifest(recipe, self.root)


if __name__ == "__main__":
    unittest.main()
