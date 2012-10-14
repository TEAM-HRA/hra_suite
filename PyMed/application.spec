# -*- mode: python -*-

application_name = os.environ["APPLICATION_NAME"]
start_script = os.environ["START_SCRIPT"]

console_type = os.environ.get("CONSOLE_TYPE","False")
if (console_type == None or len(console_type)==0) or console_type == '${console_type}':
	console_type = 'False'

build_type = os.environ.get("BUILD_TYPE", "F")
if (build_type == None or len(build_type)==0) or build_type == '${build.type}':
	build_type = "F"

a = Analysis([start_script],
             pathex=['src', '.'],
             hiddenimports=[],
             hookspath=None)

pyz = PYZ(a.pure)

# for DIR
if (build_type == "D"):
	exe = EXE(pyz,
				a.scripts,
				exclude_binaries=1,
				name=os.path.join('build\\' + application_name, application_name + '.exe'),
				#name=os.path.join('dist', application_name + '.exe'),
				debug=False,
				strip=None,
				upx=False,
				console=(console_type=='True') )

	coll = COLLECT(exe,
					a.binaries,
					a.zipfiles,
					a.datas,
					strip=None,
					upx=False,
					name=os.path.join('dist', application_name))            

	app = BUNDLE(coll,
	            name=os.path.join('dist', application_name + '.exe.app'))

if (build_type == "F"):
	# for FILE
	exe = EXE(pyz,
				a.scripts,
				a.binaries,
				a.zipfiles,
				a.datas,
				#name=os.path.join('build\\' + application_name, application_name + '.exe'),
				name=os.path.join('dist', application_name + '.exe'),
				debug=False,
				strip=None,
				upx=False,
				console=(console_type=='True') )

	app = BUNDLE(exe,
	             name=os.path.join('dist', application_name + '.exe.app'))
