ui_config = configuration_data()
ui_config.set('APP_ID', application_id)
ui_config.set('VERSION', meson.project_version() + version_suffix)

ui_preconfigured_files = files(
  'resources/gtk/ui/about_dialog.ui.in',
  'resources/gtk/ui/settings.ui.in',
  'resources/gtk/ui/window.ui.in',
)
ui_dependencies = []
foreach ui_file: ui_preconfigured_files
  ui_dependencies += configure_file(
    input:  ui_file,
    output: '@BASENAME@',
    configuration: ui_config
  )
endforeach

gnome.compile_resources(
  application_id,
  meson.project_name() + '.gresource.xml',
  gresource_bundle: true,
  install_dir: pkgdatadir,
  install: true,
  dependencies: ui_dependencies
)

# Install gschema
gschema_conf = configuration_data()
gschema_conf.set('APP_ID', application_id)
gschema_conf.set('GETTEXT_PACKAGE', gettext_package)
gschema_conf.set('SCHEMA_PATH', '/com/github/bilelmoussaoui/Authenticator' + profile_suffix + '/')

configure_file(
  configuration: gschema_conf,
  input: meson.project_name() + '.gschema.xml.in',
  install_dir: get_option('datadir') / 'glib-2.0' / 'schemas',
  output: '@0@.gschema.xml'.format(application_id)
)

# GNOME Shell Search Provider Service
search_service_provider_conf = configuration_data()
search_service_provider_conf.set('APP_ID', application_id)
search_service_provider_conf.set('LIBEXECDIR', libexecdir)
configure_file(
  configuration: search_service_provider_conf,
  input: meson.project_name() + '.SearchProvider.service.in',
  install_dir: get_option('datadir') / 'gnome-shell' / 'search-providers',
  output: '@0@.SearchProvider.service'.format(application_id)
)
# GNOME Shell Search Provider
search_provider_conf = configuration_data()
search_provider_conf.set('APP_ID', application_id)
search_provider_conf.set('PROFILE_SUFFIX', profile_suffix)
configure_file(
  configuration: search_provider_conf,
  input: meson.project_name() + '.SearchProvider.ini.in',
  install_dir: join_paths(get_option('datadir'), 'gnome-shell', 'search-providers'),
  output: '@0@.SearchProvider.ini'.format(application_id)
)

# FreeDesktop Desktop File
desktop_conf = configuration_data()
desktop_conf.set('APP_ID', application_id)
desktop_file = i18n.merge_file(
  'desktop',
  input: configure_file(
    input: meson.project_name() + '.desktop.in.in',
    output: '@BASENAME@',
    configuration: desktop_conf
  ),
  output: '@0@.desktop'.format(application_id),
  po_dir: podir,
  type: 'desktop',
  install: true,
  install_dir: get_option('datadir') / 'applications'
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
appdata_conf.set('APP_ID', application_id)
appdata_conf.set('GETTEXT_PACKAGE', gettext_package)
appdata_file = i18n.merge_file(
  'appdata',
  input: configure_file(
    input: meson.project_name() + '.appdata.xml.in.in',
    output: '@BASENAME@',
    configuration: appdata_conf
  ),
  output: '@0@.appdata.xml'.format(application_id),
  po_dir: podir,
  install: true,
  install_dir: get_option('datadir') / 'metainfo'
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
