import io
import hashlib
import json
from pathlib import Path
import stat
import tarfile
import tempfile
import unittest
import zipfile

from scripts.prepare_site import prepare_site


class PrepareSiteTests(unittest.TestCase):
    commit = "b2edab5bc690f5265a5aa1e56ae3f67669053fd4"
    hostname = "fluidd.mahenzon.ru"

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.release = self.root / "fluidd.zip"
        self.source = self.root / "source.tar.gz"
        self.output = self.root / "site"
        self.config = {"hosted": False, "endpoints": ["http://printer:7125"],
                       "blacklist": ["fluidd.xyz"], "theme": {"presets": ["original"]},
                       "futureSetting": {"enabled": True}}
        self.write_release()
        with tarfile.open(self.source, "w:gz") as archive:
            license_bytes = b"Original upstream license\n"
            member = tarfile.TarInfo(f"fluidd-{self.commit}/LICENSE")
            member.size = len(license_bytes)
            archive.addfile(member, io.BytesIO(license_bytes))

    def write_release(self):
        with zipfile.ZipFile(self.release, "w") as archive:
            archive.writestr("index.html", '<html><head><script type="module" src="./assets/app.js">'
                             '</script></head><body><div id="app"></div></body></html>')
            archive.writestr("config.json", json.dumps(self.config))
            archive.writestr("assets/app.js", "/* upstream notice */ console.log('Fluidd')")
            archive.writestr("sw.js", 'precacheAndRoute([{"revision":"upstream-index",'
                             '"url":"index.html"},{"revision":null,"url":"assets/app.js"}]);')

    def prepare(self, **overrides):
        arguments = dict(release_zip=self.release, source_archive=self.source,
                         output=self.output, pages_url=f"https://{self.hostname}/",
                         hostname=self.hostname, tag="v1.37.7", commit=self.commit)
        arguments.update(overrides)
        prepare_site(**arguments)

    def test_package_preserves_config_assets_and_corresponding_source(self):
        self.prepare()
        config = json.loads((self.output / "config.json").read_text())
        self.assertTrue(config["hosted"])
        self.assertEqual(config["endpoints"], [])
        self.assertEqual(config["blacklist"], ["fluidd.xyz", self.hostname])
        self.assertEqual(config["theme"], self.config["theme"])
        self.assertEqual(config["futureSetting"], self.config["futureSetting"])
        self.assertEqual((self.output / "assets/app.js").read_text(),
                         "/* upstream notice */ console.log('Fluidd')")
        self.assertEqual((self.output / "COPYING").read_bytes(), b"Original upstream license\n")
        self.assertEqual((self.output / "fluidd-source.tar.gz").read_bytes(), self.source.read_bytes())
        index = (self.output / "index.html").read_text()
        self.assertIn('<details id="fluidd-distribution"', index)
        self.assertIn('href="./fluidd-source.tar.gz" download', index)
        self.assertIn(self.commit, index)
        self.assertTrue((self.output / "prepare_site.py").is_file())

    def test_compatibility_shim_runs_before_fluidd_and_invalidates_cached_index(self):
        self.prepare()
        index = (self.output / "index.html").read_text()
        shim = (self.output / "browser_compat.js").read_text()
        self.assertIn(shim, index)
        self.assertLess(index.index("AbortSignal.any"), index.index('<script type="module"'))
        revision = hashlib.sha256(index.encode("utf-8")).hexdigest()
        worker = (self.output / "sw.js").read_text()
        self.assertIn(f'"revision":"{revision}","url":"index.html"', worker)
        self.assertIn('{"revision":null,"url":"assets/app.js"}', worker)
        self.assertNotIn('"upstream-index"', worker)

    def test_missing_or_ambiguous_index_precache_entry_is_rejected(self):
        for entries in ([], [{"revision": "one", "url": "index.html"},
                            {"revision": "two", "url": "index.html"}]):
            with self.subTest(entries=entries):
                archive_path = self.root / f"worker-{len(entries)}.zip"
                with zipfile.ZipFile(self.release) as source, zipfile.ZipFile(archive_path, "w") as target:
                    for entry in source.infolist():
                        content = ("precacheAndRoute(" + json.dumps(entries) + ");").encode() \
                            if entry.filename == "sw.js" else source.read(entry)
                        target.writestr(entry, content)
                with self.assertRaisesRegex(ValueError, "index.html precache entry"):
                    self.prepare(release_zip=archive_path, output=self.root / f"bad-worker-{len(entries)}")

    def test_existing_hostname_is_not_duplicated(self):
        self.config["blacklist"].append(self.hostname)
        self.write_release()
        self.prepare()
        config = json.loads((self.output / "config.json").read_text())
        self.assertEqual(config["blacklist"].count(self.hostname), 1)

    def test_wrong_pages_domain_or_origin_is_rejected(self):
        for url in ("https://owner.github.io/repo/", f"ftp://{self.hostname}/",
                    f"https://{self.hostname}/repo/", f"https://{self.hostname}:443/"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                self.prepare(pages_url=url)
        self.assertFalse(self.output.exists())

    def test_http_pages_metadata_is_accepted_before_https_enforcement(self):
        self.prepare(pages_url=f"http://{self.hostname}/")
        config = json.loads((self.output / "config.json").read_text())
        self.assertIn(self.hostname, config["blacklist"])

    def test_unsafe_release_archive_is_rejected(self):
        for name, mode in (("../escape", stat.S_IFREG), ("link", stat.S_IFLNK)):
            with self.subTest(name=name):
                with zipfile.ZipFile(self.release, "a") as archive:
                    member = zipfile.ZipInfo(name)
                    member.external_attr = (mode | 0o777) << 16
                    archive.writestr(member, "target")
                with self.assertRaises(ValueError):
                    self.prepare(output=self.root / f"rejected-{mode}")
                self.write_release()
        self.assertFalse((self.root / "escape").exists())


if __name__ == "__main__":
    unittest.main()
