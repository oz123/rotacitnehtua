project('com.github.bilelmoussaoui.Authenticator', 'c',
	version: '3.31',
  meson_version: '>= 0.48',
  license: 'GPL+-3.0',
  default_options: ['prefix=/usr']
)
python = import('python3')
gnome  = import('gnome')
i18n   = import('i18n')

gettext_package = 'Authenticator'
profile = get_option('profile')
profile_suffix = ''
name_suffix = ''
if profile != 'default'
  gettext_package += profile
  if profile == 'beta'
    name_suffix = ' (Beta)'
    profile_suffix = 'Beta'
  else
    name_suffix = ' (Development)'
    profile_suffix = 'Devel'
  endif
endif


application_id = 'com.github.bilelmoussaoui.Authenticator@0@'.format(profile_suffix)

message('Looking for dependencies')
dependency('glib-2.0')
dependency('gobject-2.0')
dependency('gobject-introspection-1.0')
dependency('gtk+-3.0', version: '>=3.16')
dependency('libsecret-1')
dependency('zbar', version: '>= 0.20.1')

find_program('glib-compile-schemas', required: true)
find_program('gtk-update-icon-cache', required: false)
find_program('update-desktop-database', required: false)

python3 = python.find_python()
if not python3.found()
    error('No valid python3 binary found')
else
    message('Found python3 binary')
endif

LOCALE_DIR = join_paths(get_option('prefix'), get_option('localedir'))
PKGDATA_DIR = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
LIBEXEC_DIR = join_paths(get_option('prefix'), get_option('libexecdir'))


# Configuration params
conf = configuration_data()
conf.set('APP_ID', application_id)
conf.set('GETTEXT_PACKAGE', gettext_package)
conf.set('PKGDATA_DIR', PKGDATA_DIR)
conf.set('LOCALE_DIR', LOCALE_DIR)
conf.set('PYTHON_DIR', join_paths(get_option('prefix'), python.sysconfig_path('purelib')))
conf.set('PYTHON_EXEC_DIR', join_paths(get_option('prefix'), python.sysconfig_path('stdlib')))
conf.set('VERSION', meson.project_version())
conf.set('PROFILE', profile)
conf.set('NAME_SUFFIX', name_suffix)
conf.set('libexecdir', LIBEXEC_DIR)
conf.set('PYTHON', python3.path())

subdir('data')
subdir('po')
subdir('src')

meson.add_install_script('build-aux/meson_post_install.py')
