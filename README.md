# Fluidd on GitHub Pages

Serve the prebuilt [Fluidd](https://github.com/fluidd-core/fluidd) frontend at
**https://fluidd.mahenzon.ru/**. Your browser connects directly to your printers
at home; GitHub only serves the static website.

Target repository: **[mahenzon/fluidd-site](https://github.com/mahenzon/fluidd-site)**,
with `master` as the default branch.

The workflow runs **only** via **Actions → Deploy Fluidd → Run workflow**.
Pushing a commit never downloads a release or deploys the site. There are no
scheduled updates. Leave `version` empty or set it to `latest` for the latest
stable release; enter a stable tag such as `v1.37.7` to pin a version or roll back.
Drafts and prereleases are rejected. `v1.37.7` was verified as the latest stable
release on 2026-11-02; the workflow resolves it again on each manual run.

## One-time setup, when ready to publish

The local branch is `master`. No GitHub repository, remote, deployment, or DNS
record is required to prepare or test these files locally.

1. Create **`mahenzon/fluidd-site`** as a public GitHub repository for free Pages hosting. Push
   this project's `master` branch when ready and make `master` the default branch.
   GitHub owner and repository name are not hardcoded in the workflow.
2. In **Settings → Pages**, select **GitHub Actions** as the publishing source.
   Set **Custom domain** to `fluidd.mahenzon.ru` and save it **before changing DNS**.
3. At your DNS provider, add a **CNAME** for `fluidd` pointing to
   `mahenzon.github.io`. Do not include `https://`, a repository name, or a URL path.
   If the provider offers a proxy, use DNS-only while provisioning the certificate.
4. Enable **Enforce HTTPS** in Pages settings when the certificate is ready.
   The workflow checks that Pages reports `fluidd.mahenzon.ru` at the site root;
   it also accepts HTTP in Pages metadata while HTTPS is being enabled.
   It fails if the configured domain is different. No repository variable, deployed
   `CNAME` file, Jekyll build, or personal access token is needed.
5. Open **Actions → Deploy Fluidd → Run workflow**, choose `master`, and run it.
   The deployment environment and run summary show the resulting website URL
   and the resolved release/source commit.

Optional domain ownership verification is available in your GitHub account's
Pages settings; see [GitHub's custom-domain guide](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site).

## Connect a home printer

1. On the printer, append the exact website origin to the **existing**
   `[authorization]` / `cors_domains` list in `moonraker.conf`, preserving its
   current entries:

   ```ini
   [authorization]
   cors_domains:
       # Keep the existing entries here.
       https://fluidd.mahenzon.ru
   ```

2. Restart Moonraker. Open https://fluidd.mahenzon.ru/ from your home connection
   and add the printer through Fluidd, for example `http://192.168.1.50:7125`.
3. Grant the browser's local-network permission if prompted. Confirm that printer
   status updates and a harmless control, such as refreshing temperature data,
   work before treating connectivity as verified.

Keep Moonraker authentication enabled and retain the existing `trusted_clients`.
No VPN, tunnel, reverse proxy, public Moonraker endpoint, or printer port
forwarding is part of this setup.

An HTTPS website talking to an HTTP printer or `ws://` socket can be blocked by
mixed-content or local-network rules. Support varies by browser and version.
Check the browser console/network panel for the actual failure: CORS, denied
local-network permission, mixed content, or an unreachable address. A successful
Pages deployment does not prove that the browser can reach a printer. Do not
disable browser security or broaden Moonraker access to bypass an error.

## What gets published

The workflow downloads the release's **`fluidd.zip`** asset, never a source
archive as the website, and extracts it into a temporary publishing directory.
The packaging script preserves unrelated `config.json` fields, including themes,
and sets:

```json
{
  "hosted": true,
  "endpoints": [],
  "blacklist": ["fluidd.xyz", "fluidd.net", "fluidd.mahenzon.ru"]
}
```

Existing blacklist entries are retained. The custom hostname is derived from
the configured Pages URL and checked against `FLUIDD_HOSTNAME` at the top of the
workflow. Blacklisting it prevents Fluidd from probing the static host and its
`:7130` endpoint for Moonraker. If you change the domain later, update that one
workflow setting, Pages settings, DNS, and the printers' CORS origins.

Fluidd uses relative asset paths and hash routing; no server-side SPA fallback
is needed. Compiled assets and upstream notices remain unchanged. A small
**License & source** disclosure provides the GPL text, an exact-commit
corresponding-source archive, the packaging script, and a dated description of
the config/index changes. The notice is embedded in the homepage because
Fluidd's service worker redirects other HTML pages into the app. Downloads also
have immutable upstream source/license links. These files are generated for
each deployment, not committed to this repository.

## Local verification

From the repository root, run:

```sh
python3 -m unittest discover -s tests -v
actionlint .github/workflows/deploy-fluidd.yml
```

`actionlint` is an optional local tool; the Python tests use only the standard
library. To package an actual downloaded release without GitHub or deployment:

```sh
python3 scripts/prepare_site.py \
  --release-zip /path/to/fluidd.zip \
  --source-archive /path/to/fluidd-COMMIT.tar.gz \
  --output /tmp/fluidd-preview \
  --pages-url https://fluidd.mahenzon.ru/ \
  --hostname fluidd.mahenzon.ru \
  --tag v1.37.7 --commit FULL_40_CHARACTER_SOURCE_COMMIT
python3 -m http.server 8080 --directory /tmp/fluidd-preview
```

Use the source commit resolved from that release's tag and download
`https://codeload.github.com/fluidd-core/fluidd/tar.gz/COMMIT` for the source
archive. The output directory must not already exist. Open http://localhost:8080/
for a static preview; local HTTP does not reproduce production HTTPS/network
restrictions.

After deployment, check the homepage and assets, `/config.json`, a hash route
such as `/#/settings`, and the **License & source** downloads. Finally test one
printer from home.

Sources: [Fluidd releases](https://github.com/fluidd-core/fluidd/releases),
[Fluidd configuration](https://docs.fluidd.xyz/configuration/),
[Moonraker authorization](https://moonraker.readthedocs.io/en/latest/configuration/#authorization),
[GitHub Pages Actions](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
