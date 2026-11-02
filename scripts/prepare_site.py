"""Package an upstream Fluidd release for the configured GitHub Pages domain."""

import argparse
from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import tarfile
from urllib.parse import urlsplit
import zipfile


def prepare_site(release_zip, source_archive, output, pages_url, hostname, tag, commit):
    url = urlsplit(pages_url)
    if (url.scheme != "https" or url.hostname != hostname or url.port is not None
            or url.username is not None or url.password is not None
            or url.path not in ("", "/") or url.query or url.fragment):
        raise ValueError(f"Set the Pages custom domain to {hostname} before deploying")
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("Expected a full upstream source commit SHA")

    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    with zipfile.ZipFile(release_zip) as archive:
        for member in archive.infolist():
            path = PurePosixPath(member.filename)
            if (path.is_absolute() or ".." in path.parts or "\\" in member.filename
                    or stat.S_ISLNK(member.external_attr >> 16)):
                raise ValueError(f"Unsafe release archive entry: {member.filename}")
        archive.extractall(output)

    index_path = output / "index.html"
    index = index_path.read_text(encoding="utf-8")
    if "</body>" not in index:
        raise ValueError("Expected index.html at the release archive root")
    config_path = output / "config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    blacklist = config.setdefault("blacklist", [])
    if not isinstance(blacklist, list) or any(not isinstance(item, str) for item in blacklist):
        raise ValueError("Expected config.json blacklist to be an array of hostnames")
    config["hosted"] = True
    config["endpoints"] = []
    if hostname not in blacklist:
        blacklist.append(hostname)
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    with tarfile.open(source_archive, "r:gz") as archive:
        license_file = archive.extractfile(f"fluidd-{commit}/LICENSE")
        if license_file is None:
            raise ValueError("The corresponding source archive is missing LICENSE")
        (output / "COPYING").write_bytes(license_file.read())
    shutil.copyfile(source_archive, output / "fluidd-source.tar.gz")
    shutil.copyfile(__file__, output / "prepare_site.py")

    date = datetime.now(timezone.utc).date().isoformat()
    # Inline the notice: Fluidd's service worker redirects other HTML pages to the app.
    notice = f"""<details id="fluidd-distribution" style="position:fixed;right:6px;bottom:2px;
z-index:10;background:#fff;color:#222;font:12px/1.5 sans-serif;max-width:calc(100vw - 12px)">
<summary style="cursor:pointer;padding:2px 6px">License &amp; source</summary>
<div style="padding:12px;max-width:30rem;max-height:60vh;overflow:auto">
<h2>Fluidd {escape(tag)}</h2>
<p>Fluidd is free software, distributed under the
<a href="https://github.com/fluidd-core/fluidd/blob/{commit}/LICENSE" target="_blank" rel="noopener">GNU GPL v3</a>
(<a href="./COPYING" download>download license</a>).
It comes without warranty; see the license for details.</p>
<p><a href="./fluidd-source.tar.gz" download>Download the corresponding source</a>
for the compiled application, including its build scripts and dependency lockfile.
<a href="https://github.com/fluidd-core/fluidd/archive/{commit}.tar.gz" target="_blank" rel="noopener">Upstream source mirror</a>.
Upstream commit: <a href="https://github.com/fluidd-core/fluidd/tree/{commit}" target="_blank" rel="noopener">{commit}</a>.</p>
<p>On {date}, this distribution changed <a href="./config.json" download>config.json</a>
to enable hosted mode, clear printer endpoints, and blacklist {escape(hostname)}.
It also added the license and source link to index.html. Compiled assets are unchanged.
The <a href="./prepare_site.py" download>packaging script</a> is provided alongside the source.</p>
</div></details>
"""
    index_path.write_text(index.replace("</body>", notice + "</body>", 1), encoding="utf-8")
    print(f"Prepared Fluidd {tag} for https://{hostname}/ from {commit}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ("release-zip", "source-archive", "output", "pages-url", "hostname", "tag", "commit"):
        parser.add_argument(f"--{option}", required=True)
    prepare_site(**vars(parser.parse_args()))
