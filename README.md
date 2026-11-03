# im85288 Kodi add-ons

A Kodi repository for [SiloKodiConnect](https://github.com/im85288/SiloKodiConnect) and the
[Skyline](https://github.com/im85288/SiloSkyline) skin. Kodi installs and updates both from here.

## Install

1. Kodi: Settings > System > Add-ons: turn on **Unknown sources**.
2. Settings > File manager > Add source: `https://im85288.github.io/kodi-repository/`.
3. Add-ons > Install from zip file: that source, then `repository.im85288.kodi.zip`.
4. Add-ons > Install from repository > im85288 Kodi add-ons: SiloKodiConnect, then Look and feel > Skin > Skyline.

Add-ons installed from a zip before the repository: install them again from the repository (step 4),
so Kodi updates them from here.

## How it's published

[`build.py`](build.py) takes each add-on's latest GitHub release zip, and the repository add-on from
[`repository.im85288.kodi/`](repository.im85288.kodi), and lays them out as Kodi reads a repository
(`addons.xml`, its md5, `zips/<id>/<id>-<version>.zip` with a `.sha256`, and their art). The
[Publish](.github/workflows/publish.yml) workflow runs it hourly and on each push, and serves the result
with GitHub Pages. A new release reaches Kodi within the hour; run Publish by hand to send it at once.

To change the repository add-on, raise its version in its `addon.xml`: Kodi updates it like any other.
