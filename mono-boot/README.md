# Mono Boot — Minimalist Monochrome Plymouth Theme

A sleek, minimal, aesthetic black-and-white boot sequence designed to seamlessly match the monochrome Hyprlock screen and Waybar setup.

## ✨ Features

- **Pure Monochrome Aesthetic**: Pure white background (`#FFFFFF`) with stark black typography and borders (`#000000`).
- **Seamless System Cohesion**: Matches the 0px border radius, 1px hairline black borders, and JetBrainsMono / DejaVu Sans Mono typography used in `hyprlock.conf` and `waybar/style.css`.
- **Two Centered Styles**:
  - **Arch Silhouette (`arch`, default)**: High-resolution minimal black Arch Linux emblem with gentle breathing opacity, spaced typography `A R C H   L I N U X`.
  - **3D ASCII Donut (`donut`)**: Smooth 3D rotating ASCII donut identical to the centerpiece in `hyprlock.conf`.
- **Refined Progress Bar**: 1px sharp rectangular outline with smooth progressive fill and indeterminate scanning pulse.
- **Clean Status Line**: Systemd service and boot notifications formatted cleanly without noisy bracket clutter.
- **Fallback Password Dialog**: Minimalist rectangular prompt matching the Hyprlock password box.

---

## 📸 Previews

- `preview_boot.gif` — Animated preview of the Arch Silhouette edition.
- `preview_donut.gif` — Animated preview of the 3D ASCII Donut edition.

---

## 🛠️ Quick Start

### 1. Install & Apply to System
```bash
cd ~/dotfiles/mono-boot
sudo ./install.sh
```

The installer automatically:
1. Copies all theme assets and scripts to `/usr/share/plymouth/themes/mono-boot/`.
2. Verifies early KMS (`i915`) in `/etc/mkinitcpio.conf`.
3. Ensures `plymouth` hook is present in `HOOKS`.
4. Sets `mono-boot` as the default Plymouth splash.
5. Regenerates initramfs with `mkinitcpio -P`.
6. Verifies systemd-boot loader options.

### 2. Test Live Without Rebooting
```bash
sudo ./test.sh
```

### 3. Switch Between Styles
```bash
# Switch to 3D ASCII Donut
./switch-style.sh donut
sudo ./install.sh

# Switch to Arch Silhouette
./switch-style.sh arch
sudo ./install.sh
```
