project('com.github.bilelmoussaoui.Authenticator',
	version: '0.2.5',
  meson_version: '>= 0.42',
  license: 'GPL+-3.0',
  default_options: ['prefix=/usr','is_devel=false']
)
python = import('python3')
gnome  = import('gnome')
i18n   = import('i18n')

message('Looking for dependencies')
dependency('glib-2.0')
dependency('gobject-2.0')
dependency('gobject-introspection-1.0')
dependency('gtk+-3.0', version : '>=3.16')

python_bin = python.find_python()
if not python_bin.found()
    error('No valid python3 binary found')
else
    message('Found python3 binary')
endif

LIB_DIR = join_paths(get_option('prefix'), get_option('libdir'), meson.project_name())
LOCALE_DIR = join_paths(get_option('prefix'), get_option('localedir'))
DATA_DIR = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())


subproject('libgd',
  default_options: [
    'with-introspection=true',
    'with-notification=true',
    'static=false',
    'pkgdatadir=' + DATA_DIR,
    'pkglibdir=' + LIB_DIR
  ]
)

# Configuration params
conf = configuration_data()
conf.set('DATA_DIR', DATA_DIR)
conf.set('LOCALE_DIR', LOCALE_DIR)
conf.set('PYTHON_DIR', join_paths(get_option('prefix'), python.sysconfig_path('purelib')))
conf.set('PYTHON_EXEC_DIR', join_paths(get_option('prefix'), python.sysconfig_path('stdlib')))
conf.set('VERSION', meson.project_version())
conf.set('ENABLE_QRSCANNER', get_option('enable_zbar'))
conf.set('LIB_DIR', LIB_DIR)
conf.set('IS_DEVEL', get_option('is_devel'))

conf.set('libexecdir', join_paths(get_option('prefix'), get_option('libexecdir')))
conf.set('PYTHON', python_bin.path())

subdir('data')
subdir('po')


configure_file(
  input: 'authenticator.py.in',
  output: 'authenticator',
  configuration: conf,
  install_dir: get_option('bindir')
)

configure_file(
  input: 'authenticator-search-provider.py.in',
  output: 'authenticator-search-provider',
  configuration: conf,
  install_dir: get_option('libexecdir')
)


configure_file(
  input: 'Authenticator/widgets/about.py.in',
  output: 'about.py',
  configuration: conf,
  install_dir : join_paths(python.sysconfig_path('purelib'),
                            'Authenticator/widgets')
)


install_subdir(
  'Authenticator',
  install_dir: python.sysconfig_path('purelib'),
  exclude_files: 'widgets/about.py.in'
)

meson.add_install_script('meson_post_install.py')
