# STinGer install images

Flash, boot, update: a vertical STG machine. Built on [Mr. Fusion](https://github.com/MiSTer-devel/mr-fusion) (GPLv3).

A STinGer image *is* Mr. Fusion, with two things swapped on its `MRFUSION` partition:
- `release.7z` also carries the flavor's `MiSTer.ini`, `downloader.ini` and MiSTercade mapping drop-in
- `splash.png` is STinGer's (the words come from `splash.txt`; shown over HDMI during install)

## Using one
1. Flash `STinGer-<flavor>.img.zip` with balenaEtcher, Win32 Disk Imager or similar.
2. Optional: put `wpa_supplicant.conf` (Wi-Fi) on the `MRFUSION` drive. Ethernet works without it.
3. Boot. Mr. Fusion installs MiSTer and reboots into the menu.
4. Scripts -> update. That pulls the cores, the ROMs Ongo ships, and the STinGer menu.

## Building
On Linux / WSL Ubuntu, from the repo root:
```bash
sudo apt install -y p7zip-full mtools unzip zip curl python3-pil
bash tools/build.sh                 # makes build/flavors/
bash installer/build_image.sh       # mistercade-v2, mistercade-v1, regular -> dist/
```
`MRF_ZIP=...` builds from a local Mr. Fusion zip. The Heber needs Heber's own Mr. Fusion fork:
`MRF_ZIP=<heber zip> bash installer/build_image.sh heber-ms2`.
