- Fix undo button on clean database doesn't work as exepcted. It still removes the accounts
- Rework the login widget design
- Set a color for the elementary appcenter/elementary headerbar.
- Create a collection (libsecret) for authenticator to avoid saving authenticator stuff on the default collection.
- Clean the base code
- Rewrite comments
- Add a debian packaging folder to the application itself
- Mirror the gitlab repository on Github
- Push to elementary appcenter

# elementary dependencies
libglib2.0-0
gir1.2-glib-2.0
libsecret-1.0
gir1.2-secret-1
gpg
python3-gnupg
python3-pyotp
python3-gi
