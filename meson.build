project('com.github.bilelmoussaoui.Authenticator',
	version: '0.2.5',
  meson_version: '>= 0.42',
  license: 'GPL+-3.0',
  default_options: ['prefix=/usr','is_devel=false']
)
python = import('python3')
gnome  = import('gnome')
i18n   = import('i18n')

if get_option('profile') == 'development'
  profile = 'Devel'
  name_suffix = ' (Development)'
else
  profile = ''
  name_suffix = ''
endif

application_id = 'com.github.bilelmoussaoui.Authenticator@0@'.format(profile)
datadir = get_option('datadir')

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

libgd_dep = dependency('gdlib', required : false)

if not libgd_dep.found()
  libgd_proj = subproject('libgd',
    default_options: [
      'with-introspection=true',
      'with-notification=true',
      'static=false',
      'pkgdatadir=' + DATA_DIR,
      'pkglibdir=' + LIB_DIR
    ]
  )

  libgd_dep = libgd_proj.get_variable('libgd_dep')
endif

# Configuration params
conf = configuration_data()
conf.set('APP_ID', application_id)
conf.set('DATA_DIR', DATA_DIR)
conf.set('LOCALE_DIR', LOCALE_DIR)
conf.set('PYTHON_DIR', join_paths(get_option('prefix'), python.sysconfig_path('purelib')))
conf.set('PYTHON_EXEC_DIR', join_paths(get_option('prefix'), python.sysconfig_path('stdlib')))
conf.set('VERSION', meson.project_version())
conf.set('ENABLE_QRSCANNER', get_option('enable_zbar'))
conf.set('LIB_DIR', LIB_DIR)
conf.set('PROFILE', profile)
conf.set('NAME_SUFFIX', name_suffix)

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

configure_file(
  input: 'Authenticator/widgets/window.py.in',
  output: 'window.py',
  configuration: conf,
  install_dir : join_paths(python.sysconfig_path('purelib'),
                            'Authenticator/widgets')
)

configure_file(
  input: 'Authenticator/utils.py.in',
  output: 'utils.py',
  configuration: conf,
  install_dir : join_paths(python.sysconfig_path('purelib'),
                            'Authenticator')
)

configure_file(
  input: 'Authenticator/application.py.in',
  output: 'application.py',
  configuration: conf,
  install_dir : join_paths(python.sysconfig_path('purelib'),
                            'Authenticator')
)

install_subdir(
  'Authenticator',
  install_dir: python.sysconfig_path('purelib'),
  exclude_files: [
    'widgets/about.py.in',
    'widgets/window.py.in',
    'utils.py.in',
    'application.py.in'
  ]
)

meson.add_install_script('meson_post_install.py')
