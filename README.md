# Fluidd on GitHub Pages

**[Open Fluidd](https://fluidd.mahenzon.ru/)** — a web interface for Klipper 3D printers.
Your browser connects directly to Moonraker on your home network. Your printers
do not need to be exposed to the internet.

## Connect a printer

1. Use **Chrome 147+** on the same network as your printer. Allow **Local network
   access** for this site when prompted.
2. Add the site's origin to the existing `cors_domains` list in your printer's
   `moonraker.conf`, keeping its other entries, then restart Moonraker:

   ```ini
   [authorization]
   cors_domains:
       # Keep your existing entries here.
       https://fluidd.mahenzon.ru
   ```

3. Open Fluidd and add your printer's address, for example `http://192.168.1.50:7125`.

Other browsers or older versions may block HTTP printers as mixed content.
Keep Moonraker authentication and `trusted_clients` unchanged.

## Deploy or update

1. Open **[Actions → Deploy Fluidd](https://github.com/mahenzon/fluidd-site/actions/workflows/deploy-fluidd.yml)**
   and select **Run workflow**.
2. Choose `master`. Use `latest` for the **latest stable Fluidd release**, or a
   release tag such as `v1.37.7` to select a specific version or roll back.
3. Run the workflow and wait for it to succeed. The run summary links to the site.

Deployments are manual. Pushing commits does not update the site.
The site's **License & source** panel provides Fluidd's license and corresponding source.

## Host your own copy

1. Put these files in a public repository with `master` as its default branch.
   Set `FLUIDD_HOSTNAME` in [the workflow](.github/workflows/deploy-fluidd.yml) to
   your domain; use that domain in the printer's CORS entry too.
2. In **Settings → Pages**, choose **GitHub Actions** and save your custom domain
   **before changing DNS**.
3. Point the subdomain's DNS **CNAME** to `<YOUR_GITHUB_OWNER>.github.io`.
   Enable **Enforce HTTPS** when the certificate is ready, then run the workflow.
