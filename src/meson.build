

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
  input: 'Authenticator/models/settings.py.in',
  output: 'settings.py',
  configuration: conf,
  install_dir: join_paths(python.sysconfig_path('purelib'),
                            'Authenticator/models')
)

configure_file(
  input: 'Authenticator/widgets/window.py.in',
  output: 'window.py',
  configuration: conf,
  install_dir: join_paths(python.sysconfig_path('purelib'),
                            'Authenticator/widgets')
)

configure_file(
  input: 'Authenticator/utils.py.in',
  output: 'utils.py',
  configuration: conf,
  install_dir: join_paths(python.sysconfig_path('purelib'),
                            'Authenticator')
)

configure_file(
  input: 'Authenticator/application.py.in',
  output: 'application.py',
  configuration: conf,
  install_dir: join_paths(python.sysconfig_path('purelib'),
                            'Authenticator')
)

install_subdir(
  'Authenticator',
  install_dir: python.sysconfig_path('purelib'),
  exclude_files: [
    'models/settings.py.in',
    'widgets/window.py.in',
    'utils.py.in',
    'application.py.in'
  ]
)
