# Fluidd on GitHub Pages

**[Open Fluidd](https://fluidd.mahenzon.ru/)** · **[HTTP for iOS/iPadOS](http://fluidd.mahenzon.ru/)**

Control Klipper printers on your home network. Your browser connects directly to
Moonraker; printers stay local.

## Connect a printer

1. Join your printer's network. For HTTPS, use **Chrome 147+** and allow **Local
   network access**. On iPhone or iPad, use HTTP as described below.
2. Append `*://fluidd.mahenzon.ru` to the existing `[authorization]` → `cors_domains`
   list in `moonraker.conf`, then restart Moonraker. Keep other entries and settings.
3. Add your printer in Fluidd, for example `http://192.168.1.50:7125`.

`*://` allows both HTTP and HTTPS Fluidd website origins. It does not change the
printer's protocol or bypass browser mixed-content rules.

## iOS and iPadOS

On older iPhones and iPads, open **[Fluidd over HTTP](http://fluidd.mahenzon.ru/)**
and keep `http://` in the address bar when connecting to an HTTP printer. The
compatibility fix handles missing `AbortSignal.any()` on iOS and iPadOS 16.
Tested on an iPad running 16.6.1. Browsers on those versions share WebKit, so
switching browsers alone does not help. Safari blocks the HTTPS site from
reaching plain HTTP/WebSocket printers; CORS cannot override that restriction.

## Deploy or update

1. Open **[Deploy Fluidd](https://github.com/mahenzon/fluidd-site/actions/workflows/deploy-fluidd.yml) → Run workflow**.
2. Choose `master` and `latest` for the **latest stable Fluidd release**, or a tag
   such as `v1.37.7` to select a version or roll back.
3. Run it and wait for success. The summary links to the site.

Pushes do not deploy. The site's **License & source** panel provides the license and source.

## Host your own copy

1. Use a public repository with default branch `master`. Set `FLUIDD_HOSTNAME` in
   [the workflow](.github/workflows/deploy-fluidd.yml) to your hostname;
   use `*://YOUR_HOSTNAME` in Moonraker.
2. In **Settings → Pages**, choose **GitHub Actions** and save your custom domain before changing DNS.
3. Set its DNS **CNAME** to `<YOUR_GITHUB_OWNER>.github.io` and run the workflow.
   Leave **Enforce HTTPS** off to support HTTP access from iPhones and iPads.
