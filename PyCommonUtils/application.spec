# -*- mode: python -*-

application_name = os.environ["APPLICATION_NAME"]
start_script = os.environ["START_SCRIPT"]

console_type = os.environ.get("CONSOLE_TYPE","False")
if (console_type == None or len(console_type)==0) or console_type == '${console_type}':
	console_type = 'False'

build_type = os.environ.get("BUILD_TYPE", "F")
if (build_type == None or len(build_type)==0) or build_type == '${build.type}':
	build_type = "F"

debug_info = os.environ.get("DEBUG_INFO","False")
if (debug_info == None or len(debug_info)==0) or debug_info == '${debug_info}':
	debug_info = False
else:
    debug_info = (debug_info == 'True')

application_root = os.environ.get("APPLICATION_ROOT")
if (application_root == None or len(application_root)==0) or application_root == '${application.root}':
	application_root = ''
else:
	application_root += '/'

pathex = ['src', '.']
#add external eggs
for env_key in os.environ:
	if (env_key.startswith('EGG_')):
		value = os.environ.get(env_key)
		if ( not (value == None or len(value) == 0 or value.startswith('${egg.')) ):
			pathex.append(value)

a = Analysis([start_script],
             pathex=pathex,
             hiddenimports=[],
             hookspath=None)

pyz = PYZ(a.pure)

# for DIR
if (build_type == "D"):
	exe = EXE(pyz,
				a.scripts,
				exclude_binaries=1,
				name=os.path.join(application_root + 'build\\' + application_name, application_name + '.exe'),
				debug=debug_info,
				strip=None,
				upx=False,
				console=(console_type=='True') )

	coll = COLLECT(exe,
					a.binaries,
					a.zipfiles,
					a.datas,
					strip=None,
					upx=False,
					name=os.path.join(application_root + 'dist', application_name))            

	app = BUNDLE(coll,
	            name=os.path.join(application_root + 'dist', application_name + '.exe.app'))

# for FILE
if (build_type == "F"):
	exe = EXE(pyz,
				a.scripts,
				a.binaries,
				a.zipfiles,
				a.datas,
				name=os.path.join(application_root + 'dist', application_name + '.exe'),
				debug=debug_info,
				strip=None,
				upx=False,
				console=(console_type=='True') )

	app = BUNDLE(exe,
	             name=os.path.join(application_root + 'dist', application_name + '.exe.app'))
