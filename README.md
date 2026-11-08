# im85288 Kodi add-ons

A Kodi repository for [KodiConnectForSilo](https://github.com/im85288/KodiConnectForSilo) and the
[Skyline](https://github.com/im85288/Skyline) skin. Kodi installs and updates both from here.

## Install

1. Kodi: Settings > System > Add-ons: turn on **Unknown sources**.
2. Settings > File manager > Add source: `https://kodi.im85288.uk/`.
3. Add-ons > Install from zip file: that source, then `repository.im85288.kodi.zip`.
4. Add-ons > Install from repository > im85288 Kodi add-ons: KodiConnectForSilo, then Look and feel > Skin > Skyline.

Add-ons installed from a zip before the repository: install them again from the repository (step 4),
so Kodi updates them from here.

## How it's published

[`build.py`](build.py) takes each add-on's latest GitHub release zip, and the repository add-on from
[`repository.im85288.kodi/`](repository.im85288.kodi), and lays them out as Kodi reads a repository
(`addons.xml`, its md5, `zips/<id>/<id>-<version>.zip` with a `.sha256`, and their art). The
[Publish](.github/workflows/publish.yml) workflow runs it hourly and on each push, and serves the result
with GitHub Pages at `kodi.im85288.uk` (the old `im85288.github.io/kodi-repository/` address redirects
there). A new release reaches Kodi within the hour; run Publish by hand to send it at once.

Cloudflare proxies `kodi.im85288.uk` and redirects each add-on's zip
(`/zips/<id>/<id>-<version>.zip`) to the identical file on its GitHub release, so the releases' download
counts are Kodi's installs and updates:

```bash
gh api repos/im85288/KodiConnectForSilo/releases --jq '.[] | "\(.tag_name) \([.assets[].download_count] | add)"'
```

To change the repository add-on, raise its version in its `addon.xml`: Kodi updates it like any other.
