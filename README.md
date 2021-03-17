# Authenticator
<p>Two-factor authentication application built for GNOME using Python.</p>
## Why this fork?

The original maintainer has decided to take an OKayish app and re-write in rust.
I have nothing against this. He works on his spare time and I appreciate his choice
to work on this project and rewrite with rust. However, I feel this brings **me**
no real benefit. This only exist here to scratch my itch: have a working authenticator
on my Linux phone. The new rust version will not work with Wayland + Phosh, and I feel
like fixing this in Python will be easier than mastering rust. I might be wrong.

## Screenshots

![screenshot](data/screenshots/screenshot3.png)

## Features

- QR code scanner
- Beautiful UI
- Huge database of more than 560 supported services
- Keep your PIN tokens secure by locking the application with a password
- Automtically fetch an image for services using their favicon
- The possibility to add new services

## Hack on Authenticator
To build the development version of Authenticator and hack on the code
see the [general guide](https://wiki.gnome.org/Newcomers/BuildProject)
for building GNOME apps with Flatpak and GNOME Builder.

You are expected to follow our [Code of Conduct](/code-of-conduct.md) when participating in project
spaces.

## Credits

- We ship a database of providers based on [twofactorauth](https://github.com/2factorauth/twofactorauth), by the 2factorauth team
