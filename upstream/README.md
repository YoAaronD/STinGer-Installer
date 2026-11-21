# Upstream proposals: build and test on AD1

Two small changes to MiSTer itself that make a tate arcade cab nicer for everyone, not just STinGer.
Each one is a patch file in this folder. The plan for both: build it, run it on a cab, then open a pull request with photos.

| Patch | Repo | Size | What it does |
| --- | --- | --- | --- |
| `main-menu_start_dir.patch` | [Main_MiSTer](https://github.com/MiSTer-devel/Main_MiSTer) (base `fb7d444`) | 19 lines, 4 files | New MiSTer.ini option `menu_start_dir=_Arcade`: the core list opens in that folder instead of the SD root |
| `kernel-fbcon-rotation.patch` | [Linux-Kernel_MiSTer](https://github.com/MiSTer-devel/Linux-Kernel_MiSTer) (base `2917c67b8`) | 1 line | Turns on the kernel's text-console rotation, so Update All and other scripts can be shown upright on a tate monitor |

Both were written and compile-checked here, but neither has been built for ARM or run on a MiSTer yet.
**Test on a spare SD card.** If something goes wrong, put the card in a PC and restore the backup file.

---

## 1. One-time setup: Ubuntu in WSL

In PowerShell (as admin), if WSL isn't installed yet:

```powershell
wsl --install -d Ubuntu
```

Reboot if asked, open **Ubuntu** from the Start menu, pick a username and password. Then in Ubuntu:

```bash
sudo apt update && sudo apt install -y build-essential git bc bison flex libssl-dev libelf-dev lzop u-boot-tools gh
git config --global user.name "YoAaronD"
git config --global user.email "YoAaronD@users.noreply.github.com"
cd ~
wget -c https://developer.arm.com/-/media/Files/downloads/gnu-a/10.2-2020.11/binrel/gcc-arm-10.2-2020.11-x86_64-arm-none-linux-gnueabihf.tar.xz
sudo tar xf gcc-arm-10.2-2020.11-x86_64-arm-none-linux-gnueabihf.tar.xz -C /opt
echo 'export PATH=/opt/gcc-arm-10.2-2020.11-x86_64-arm-none-linux-gnueabihf/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
arm-none-linux-gnueabihf-gcc --version    # should print 10.2.1
```

That's MiSTer's official cross-compiler (the one Main_MiSTer's Makefile expects).
Windows drives show up in Ubuntu under `/mnt/c`, so this repo is at `/mnt/c/cores/STinGer-Installer`.

---

## 2. Menu start folder (Main_MiSTer)

### Build

```bash
cd ~
git clone https://github.com/MiSTer-devel/Main_MiSTer.git
cd Main_MiSTer
git am /mnt/c/cores/STinGer-Installer/upstream/main-menu_start_dir.patch
make
ls -l bin/MiSTer      # the new MiSTer program
cp bin/MiSTer /mnt/c/cores/MiSTer-menu_start_dir
```

If `git am` complains, Main_MiSTer has moved on since the patch was made; tell Claude and it'll rebase the patch.

### Install on the test card

1. Card in the PC. Rename `MiSTer` (in the card's root) to `MiSTer.bak`.
2. Copy `C:\cores\MiSTer-menu_start_dir` to the card root and rename it to `MiSTer` (no extension).
3. In `MiSTer.ini`, under `[MiSTer]`, add: `menu_start_dir=_Arcade`
4. Card back in the cab, power on. **Don't run update or Update All during the test**: they put the official `MiSTer` back.

### What to check

- [ ] After boot, opening the core list lands inside Arcade (Core STGs / Other Shooting Games / Other Vertical Games)
- [ ] Back (or `..`) goes up to the root as normal
- [ ] Launch a game, open the core list from inside it: still opens next to that game
- [ ] Return to the menu: opens in Arcade again
- [ ] Comment the line out (`;menu_start_dir=_Arcade`), reboot: back to the old behavior (root)
- [ ] A wrong path (e.g. `menu_start_dir=_Nope`) just falls back to the root

**Undo:** delete `MiSTer`, rename `MiSTer.bak` back to `MiSTer`. (Or run update: it restores the official one.)

---

## 3. Rotated script console (kernel)

### Check the running kernel version first

Kernel modules (Wi-Fi, Bluetooth and so on) only load if the new kernel's version matches the card's.
Run Update All once on the test card first, so it has the latest Linux. Then over SSH (user `root`, password `1`):

```bash
ssh root@<cab IP>
uname -r          # e.g. 6.18.38
```

### Build

```bash
cd ~
git clone --depth=1 https://github.com/MiSTer-devel/Linux-Kernel_MiSTer.git
cd Linux-Kernel_MiSTer
make kernelversion    # must match uname -r from the cab; if not, tell Claude before going on
git am /mnt/c/cores/STinGer-Installer/upstream/kernel-fbcon-rotation.patch
export ARCH=arm CROSS_COMPILE=arm-none-linux-gnueabihf-
make MiSTer_defconfig
grep FRAMEBUFFER_CONSOLE_ROTATION .config     # CONFIG_FRAMEBUFFER_CONSOLE_ROTATION=y
make -j$(nproc) zImage
make intel/socfpga/socfpga_cyclone5_de10_nano.dtb
cat arch/arm/boot/zImage arch/arm/boot/dts/intel/socfpga/socfpga_cyclone5_de10_nano.dtb > zImage_dtb
cp zImage_dtb /mnt/c/cores/zImage_dtb-fbcon-rotation
```

(`--depth=1` keeps the download small. The kernel takes a while to build the first time.)

### Install on the test card

1. Card in the PC. In the `linux` folder, rename `zImage_dtb` to `zImage_dtb.bak`.
2. Copy `C:\cores\zImage_dtb-fbcon-rotation` into `linux`, renamed to `zImage_dtb`.
3. Open `linux\user-startup.sh` (create it if it isn't there) and add at the end:

   ```sh
   # STinGer: show Scripts-menu tools upright on a CCW tate monitor (needs fbcon rotation in the kernel)
   [ -w /sys/class/graphics/fbcon/rotate_all ] && echo 3 > /sys/class/graphics/fbcon/rotate_all
   ```

4. Card back in the cab, power on.

### What to check

- [ ] MiSTer boots normally, menu looks the same (rotation only touches the text console)
- [ ] Scripts → `update_all`: upright text. **Upside down?** Change `3` to `1` in user-startup.sh (the two directions are 1 and 3)
- [ ] Is it readable? A rotated 15 kHz screen is narrow (about 30 columns): note whether Update All's screens fit
- [ ] Wi-Fi / Bluetooth / controllers still work (proves the kernel modules still load)
- [ ] Without the user-startup line, scripts look exactly like before (rotation is off by default)
- [ ] Photo of Update All upright on the cab, for the pull request

**Undo:** in `linux`, delete `zImage_dtb` and rename `zImage_dtb.bak` back. If the cab doesn't boot, do this from the PC.

---

## 4. Pull requests (after the cab tests pass)

For each repo: fork it on GitHub (YoAaronD), push the branch, open the PR. From the build folders above:

```bash
gh auth login                       # once
gh repo fork --remote --remote-name fork
git checkout -b menu-start-dir      # kernel: fbcon-rotation
git push -u fork HEAD
gh pr create --fill                 # or write the description on github.com
```

Things to put in each PR description: what it does, that it's off by default, the cab it was tested on
(MiSTercade V2, tate CCW CRT), and a photo.

### Later: automatic rotation (Main_MiSTer)

Once the kernel change is in, the startup line can go away: Main_MiSTer already runs Scripts-menu tools on
text console 2 (`agetty ... tty2`), so it could set the console rotation itself whenever `osd_rotate` is 1 or 2.
That would make every tate cab's scripts upright with no setup at all. A small follow-up patch, worth proposing
only after the kernel change is accepted.
