# Fluidd on GitHub Pages

**[Open Fluidd](https://fluidd.mahenzon.ru/)** to control Klipper printers on your
home network. Your browser connects directly to Moonraker; printers stay local.

## Connect a printer

1. Use **Chrome 147+** on your printer's network and allow **Local network access**.
2. Append `*://fluidd.mahenzon.ru` to the existing `[authorization]` → `cors_domains`
   list in `moonraker.conf`, then restart Moonraker. Keep other entries and settings.
3. Add your printer in Fluidd, for example `http://192.168.1.50:7125`.

`*://` accepts HTTP/HTTPS **Fluidd website origins**; `https://fluidd.mahenzon.ru`
also works. It does not control the printer's protocol or bypass mixed-content rules.
Other browsers may block HTTP printers.

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
3. Set its DNS **CNAME** to `<YOUR_GITHUB_OWNER>.github.io`, enable **Enforce HTTPS**
   when ready, then run the workflow.
