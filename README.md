<a href="https://flathub.org/apps/details/com.github.bilelmoussaoui.Authenticator">
<img src="https://flathub.org/assets/badges/flathub-badge-i-en.png" width="190px" />
</a>


# Authenticator
<img src="https://gitlab.gnome.org/World/Authenticator/raw/master/data/icons/hicolor/scalable/apps/com.github.bilelmoussaoui.Authenticator.svg" width="128" height="128" />
<p>Two-factor authentication code generator for GNOME. Created with love using Python and GTK+.</p>

## Screenshots

<p align="center">
<img align="center" src="data/screenshots/screenshot1.png" />
</p>

## Features

- QR code scanner
- Beautiful UI
- Huge database of (290+) websites/applications

## Installation

### Flatpak
You can install the `flatpak` package of the application from Flathub using
```
flatpak install flathub com.github.bilelmoussaoui.Authenticator
```

### Distribution packaging

- Pop!\_OS (18.10+): `gnome-authenticator`

### Building from source code
#### Dependecies

- `Python 3.3+`
- `Gtk 3.16+`
- `meson 0.42+`
- `ninja`
- `pyotp`
- `libsecret`

Those dependencies are only used if you build the application with QR code scanner support
- `Pillow`
- `pyzbar` depends on `zbar`
  - `libzbar-dev` on Ubuntu
  - `zbar` on Arch

1 - Clone the repository

```bash
git clone https://gitlab.gnome.org/World/Authenticator && cd ./Authenticator
```

2 - Install the dependencies

3 - Afterwards

```bash
meson builddir
sudo ninja -C builddir install
```

4 - You can run the application from the desktop file or from the terminal using
```bash
authenticator
```

## Flags

- `--version`
  Shows the version number of the application
- `--debug`
  Enable the debug logs


## Credits

- Database for applications/websites from [twofactorauth](https://github.com/2factorauth/twofactorauth), by the 2factorauth team
