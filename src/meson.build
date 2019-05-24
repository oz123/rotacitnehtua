bin_conf = configuration_data()
bin_conf.set('APP_ID', application_id)
bin_conf.set('GETTEXT_PACKAGE', gettext_package)
bin_conf.set('LOCALE_DIR', localedir)
bin_conf.set('PKGDATA_DIR', pkgdatadir)
bin_conf.set('PROFILE', profile)
bin_conf.set('PYTHON_DIR', pythondir)
bin_conf.set('PYTHON', python3.path())
configure_file(
  input: 'authenticator.py.in',
  output: 'authenticator',
  configuration: bin_conf,
  install_dir: get_option('bindir')
)

search_provider_bin_conf = configuration_data()
search_provider_bin_conf.set('APP_ID', application_id)
search_provider_bin_conf.set('PRFOILE_SUFFIX', profile_suffix)
search_provider_bin_conf.set('PYTHON_DIR', pythondir)
search_provider_bin_conf.set('PYTHON', python3.path())
configure_file(
  input: 'authenticator-search-provider.py.in',
  output: 'authenticator-search-provider',
  configuration: search_provider_bin_conf,
  install_dir: libexecdir
)

settings_model_conf = configuration_data()
settings_model_conf.set('APP_ID', application_id)
configure_file(
  input: 'Authenticator/models/settings.py.in',
  output: 'settings.py',
  configuration: settings_model_conf,
  install_dir: pythondir / 'Authenticator' / 'models'
)

application_conf = configuration_data()
application_conf.set('APP_ID', application_id)
application_conf.set('NAME_SUFFIX', name_suffix)
configure_file(
  input: 'Authenticator/application.py.in',
  output: 'application.py',
  configuration: application_conf,
  install_dir: pythondir / 'Authenticator'
)

install_subdir(
  'Authenticator',
  install_dir: pythondir,
  exclude_files: [
    'models/settings.py.in',
    'application.py.in'
  ]
)
