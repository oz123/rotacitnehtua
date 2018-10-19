gnome.compile_resources(
  meson.project_name(),
  meson.project_name() + '.gresource.xml',
  gresource_bundle: true,
  source_dir: '.',
  install_dir: join_paths(datadir, meson.project_name()),
  install: true
)

install_data(
  meson.project_name() + '.gschema.xml',
  install_dir : join_paths(datadir, 'glib-2.0/schemas')
)

search_service_provider_conf = configuration_data()
search_service_provider_conf.set('appid', application_id)
search_service_provider_conf.set('profile', profile)
configure_file(
  configuration: search_service_provider_conf,
  input: files(meson.project_name() + '.SearchProvider.service.in'),
  install_dir: join_paths(datadir, 'gnome-shell', 'search-providers'),
  output: '@0@.SearchProvider.service'.format(application_id)
)

search_provider_conf = configuration_data()
search_provider_conf.set('appid', application_id)
search_provider_conf.set('profile', profile)
configure_file(
  configuration: search_provider_conf,
  input: files(meson.project_name() + '.SearchProvider.ini.in'),
  install_dir: join_paths(datadir, 'gnome-shell', 'search-providers'),
  output: '@0@.SearchProvider.ini'.format(application_id)
)


desktop_conf = configuration_data()
desktop_conf.set('icon', application_id)
desktop = i18n.merge_file(
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
  install_dir: join_paths(datadir, 'applications')
)

appdata_conf = configuration_data()
appdata_conf.set('appid', application_id)
appdata = i18n.merge_file(
  'appdata',
  input: configure_file(
    input: files(meson.project_name() + '.appdata.xml.in.in'),
    output: '@0@.appdata.xml.in'.format(application_id),
    configuration: appdata_conf
  ),
  output: '@0@.appdata.xml'.format(application_id),
  po_dir: join_paths(meson.source_root(), 'po'),
  install: true,
  install_dir: join_paths(datadir, 'appdata')
)


desktop_file_validate = find_program('desktop-file-validate', required:false)

if desktop_file_validate.found()
  test (
    'Validate desktop file',
    desktop_file_validate,
    args: join_paths(meson.current_build_dir(), '@0@.desktop'.format(application_id))
  )
endif

appstreamcli = find_program('appstream-util', required:false)

if appstreamcli.found()
  test (
    'Validate appdata file',
    appstreamcli,
    args: [
            'validate-relax',
            join_paths(meson.current_build_dir(), '@0@.appdata.xml'.format(application_id))
     ]
  )
endif

subdir('icons')
