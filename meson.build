project('com.github.bilelmoussaoui.Authenticator', 'c',
	version: '3.32.2',
  meson_version: '>= 0.50',
  license: 'GPL+-3.0'
)
gnome  = import('gnome')
i18n   = import('i18n')

# This doesn't work yet. It's doesn't find the python3 from the sandboxed env first
# python = import('python')
# python3 = python.find_installation('python3')
python = import('python3')
python3 = python.find_python()
if not python3.found()
    error('No valid python3 binary found')
else
    message('Found python3 binary')
endif



dependency('glib-2.0')
dependency('gobject-2.0')
dependency('gobject-introspection-1.0')
dependency('gtk+-3.0', version: '>=3.16')
dependency('libsecret-1')
dependency('zbar', version: '>= 0.20.1')
find_program('glib-compile-schemas', required: true)
find_program('gtk-update-icon-cache', required: false)
find_program('update-desktop-database', required: false)

gettext_package = 'Authenticator'
profile = get_option('profile')
profile_suffix = ''
name_suffix = ''
version_suffix = ''
if profile != 'default'
  gettext_package += profile
  if profile == 'beta'
    name_suffix = ' (Beta)'
    profile_suffix = 'Beta'
  else
    name_suffix = ' (Development)'
    profile_suffix = 'Devel'
  endif
  vcs_tag = run_command('git', 'rev-parse', '--short', 'HEAD').stdout().strip()
  if vcs_tag == ''
    version_suffix = '-devel'
  else
    version_suffix = '-@0@'.format (vcs_tag)
  endif
endif


application_id = 'com.github.bilelmoussaoui.Authenticator@0@'.format(profile_suffix)
localedir = get_option('prefix') / get_option('localedir')
pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
libexecdir = get_option('prefix') / get_option('libexecdir')
pythondir = get_option('prefix') / python.sysconfig_path('purelib')

podir = meson.source_root() / 'po'

if profile != 'default'
    # Setup pre-commit hook for ensuring coding style is always consistent
    message('Setting up git pre-commit hook..')
    run_command('cp', '-f', 'hooks/pre-commit.hook', '.git/hooks/pre-commit')
endif


subdir('data')
subdir('po')
subdir('src')
meson.add_install_script('build-aux/meson_post_install.py')
