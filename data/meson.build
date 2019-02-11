about_dialog_conf = configuration_data()
about_dialog_conf.set('APP_ID', application_id)
about_dialog_conf.set('VERSION', meson.project_version())
gnome.compile_resources(
  application_id,
  meson.project_name() + '.gresource.xml',
  gresource_bundle: true,
  install_dir: join_paths(get_option('datadir'), meson.project_name()),
  install: true,
  dependencies: [configure_file(
    input: 'ui/about_dialog.ui.in',
    output: 'about_dialog.ui',
    configuration: about_dialog_conf
  ),
  configure_file(
    input: 'ui/window.ui.in',
    output: 'window.ui',
    configuration: about_dialog_conf
  )
  ]
)

# Install gschema
gschema_conf = configuration_data()
gschema_conf.set('app-id', application_id)
if get_option('profile') == 'development'
  gschema_conf.set('schema-path', '/com/github/bilelmoussaoui/Authenticator/')
else
  gschema_conf.set('schema-path', '/com/github/bilelmoussaoui/AuthenticatorDevel/')
endif
configure_file(
  configuration: gschema_conf,
  input: files(meson.project_name() + '.gschema.xml.in'),
  install_dir: join_paths(get_option('datadir'), 'glib-2.0', 'schemas'),
  output: '@0@.gschema.xml'.format(application_id)
)

# GNOME Shell Search Provider Service
search_service_provider_conf = configuration_data()
search_service_provider_conf.set('appid', application_id)
search_service_provider_conf.set('profile', profile)
search_service_provider_conf.set('libexecdir', LIBEXEC_DIR)
configure_file(
  configuration: search_service_provider_conf,
  input: files(meson.project_name() + '.SearchProvider.service.in'),
  install_dir: join_paths(get_option('datadir'), 'gnome-shell', 'search-providers'),
  output: '@0@.SearchProvider.service'.format(application_id)
)
# GNOME Shell Search Provider
search_provider_conf = configuration_data()
search_provider_conf.set('appid', application_id)
search_provider_conf.set('profile', profile)
configure_file(
  configuration: search_provider_conf,
  input: files(meson.project_name() + '.SearchProvider.ini.in'),
  install_dir: join_paths(get_option('datadir'), 'gnome-shell', 'search-providers'),
  output: '@0@.SearchProvider.ini'.format(application_id)
)

# FreeDesktop Desktop File
desktop_conf = configuration_data()
desktop_conf.set('appid', application_id)
desktop_file = i18n.merge_file(
  'desktop',
  input: configure_file(
    input: files(meson.project_name() + '.desktop.in.in'),
    output: '@0@.desktop.in'.format(application_id),
    configuration: desktop_conf
  ),
  output: '@0@.desktop'.format(application_id),
  po_dir: join_paths(meson.source_root(), 'po'),
  type: 'desktop',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'applications')
)
# Validate Desktop File
desktop_file_validate = find_program('desktop-file-validate', required: false)
if desktop_file_validate.found()
  test (
    'Validate desktop file',
    desktop_file_validate,
    args: desktop_file.full_path()
  )
endif

# Freedesktop AppData File
appdata_conf = configuration_data()
appdata_conf.set('appid', application_id)
appdata_file = i18n.merge_file(
  'appdata',
  input: configure_file(
    input: files(meson.project_name() + '.appdata.xml.in.in'),
    output: '@0@.appdata.xml.in'.format(application_id),
    configuration: appdata_conf
  ),
  output: '@0@.appdata.xml'.format(application_id),
  po_dir: join_paths(meson.source_root(), 'po'),
  install: true,
  install_dir: join_paths(get_option('datadir'), 'metainfo')
)
# Validate AppData File
appstream_util = find_program('appstream-util', required: false)
if appstream_util.found()
  test (
    'Validate appdata file',
    appstream_util,
    args: ['validate-relax', '--nonet', appdata_file.full_path()]
  )
endif

subdir('icons')
