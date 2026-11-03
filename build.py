#!/usr/bin/env python3
"""Build the repository's site: each add-on's latest GitHub release, and
the repository add-on itself, laid out as Kodi reads a repository.

    site/addons.xml, addons.xml.md5     every add-on's manifest
    site/zips/<id>/<id>-<version>.zip    and its .sha256
    site/zips/<id>/<asset>               icon, fanart, screenshots

Usage: build.py [site]   (GITHUB_TOKEN, if set, lifts the API's rate limit)
"""
import hashlib
import io
import json
import os
import shutil
import sys
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
REPOSITORY = 'repository.im85288.kodi'
# The add-ons published, by their GitHub repository; each release carries <id>-<version>.zip.
SOURCES = [('im85288/SiloKodiConnect', 'plugin.video.silokodiconnect'),
           ('im85288/SiloSkyline', 'skin.silo.skyline')]


def fetch(url, accept='application/vnd.github+json'):
    request = urllib.request.Request(url, headers={'Accept': accept, 'User-Agent': 'kodi-repository'})
    token = os.environ.get('GITHUB_TOKEN')
    if token and url.startswith('https://api.github.com/'):
        request.add_header('Authorization', 'Bearer ' + token)
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def latest_zip(repo, addon_id):
    """The latest release's add-on zip, as bytes."""
    release = json.loads(fetch('https://api.github.com/repos/%s/releases/latest' % repo))
    for asset in release['assets']:
        if asset['name'].startswith(addon_id + '-') and asset['name'].endswith('.zip'):
            return fetch(asset['browser_download_url'], accept='application/octet-stream')
    raise SystemExit('%s %s has no %s zip' % (repo, release['tag_name'], addon_id))


def folder_zip(addon_id):
    """The repository add-on, zipped from its folder here."""
    data = io.BytesIO()
    with zipfile.ZipFile(data, 'w', zipfile.ZIP_DEFLATED) as archive:
        folder = os.path.join(ROOT, addon_id)
        for name in sorted(os.listdir(folder)):
            archive.write(os.path.join(folder, name), '%s/%s' % (addon_id, name))
    return data.getvalue()


def publish(site, addon_id, data):
    """Lay out one add-on's zip, hash and assets; returns its manifest."""
    archive = zipfile.ZipFile(io.BytesIO(data))
    manifest = ET.fromstring(archive.read('%s/addon.xml' % addon_id))
    if manifest.get('id') != addon_id:
        raise SystemExit('%s: the zip holds %s' % (addon_id, manifest.get('id')))
    folder = os.path.join(site, 'zips', addon_id)
    os.makedirs(folder, exist_ok=True)
    name = '%s-%s.zip' % (addon_id, manifest.get('version'))
    with open(os.path.join(folder, name), 'wb') as handle:
        handle.write(data)
    with open(os.path.join(folder, name + '.sha256'), 'w') as handle:
        handle.write(hashlib.sha256(data).hexdigest())
    # Kodi shows an add-on's art before it's installed from <datadir>/<id>/<path>.
    for asset in manifest.iterfind('extension/assets/*'):
        if asset.text:
            target = os.path.join(folder, asset.text.strip())
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, 'wb') as handle:
                handle.write(archive.read('%s/%s' % (addon_id, asset.text.strip())))
    print('%s %s' % (addon_id, manifest.get('version')))
    return manifest


def main(site):
    shutil.rmtree(site, ignore_errors=True)
    os.makedirs(site)
    manifests = [publish(site, REPOSITORY, folder_zip(REPOSITORY))]
    manifests += [publish(site, addon_id, latest_zip(repo, addon_id)) for repo, addon_id in SOURCES]
    index = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<addons>\n'
             + ''.join(ET.tostring(manifest, encoding='unicode').strip() + '\n' for manifest in manifests)
             + '</addons>\n').encode('utf-8')
    with open(os.path.join(site, 'addons.xml'), 'wb') as handle:
        handle.write(index)
    with open(os.path.join(site, 'addons.xml.md5'), 'w') as handle:
        handle.write(hashlib.md5(index).hexdigest())
    # The repository add-on's zip at the top too, for a first install by URL.
    shutil.copy(os.path.join(site, 'zips', REPOSITORY, '%s-%s.zip' % (REPOSITORY, manifests[0].get('version'))),
                os.path.join(site, REPOSITORY + '.zip'))
    with open(os.path.join(site, 'index.html'), 'w') as handle:
        handle.write('<!doctype html><meta charset="utf-8"><title>im85288 Kodi add-ons</title>'
                     '<p>A Kodi repository. Install <a href="%s.zip">%s.zip</a> '
                     '(Add-ons &gt; Install from zip file), then its add-ons from it.</p>\n' % (REPOSITORY, REPOSITORY))


if __name__ == '__main__':
    main(os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'site')))
