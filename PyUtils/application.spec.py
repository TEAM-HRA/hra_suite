# -*- mode: python -*-

from pkgutil import walk_packages
import sys

#set up additional packages
hidden_packages = os.environ.get("HIDDEN_PACKAGES")
hidden_imports = []
if not ( hidden_packages == None or
	len(hidden_packages)==0 or hidden_packages == '${hidden_packages}'):
	packages = list(walk_packages())
	#for importer, modname, ispkg in pkgutil.walk_packages():
   	# 	print "Found submodule %s (is a package: %s)" % (modname, ispkg)
	for _package in hidden_packages.split(";"): # packages are separated by ';' sign
		if ( len(_package) > 0 ):
           	# add only if name of a package starts as _package name and 
            # the package is a module type
			hidden_imports[len(hidden_imports):] = [package[1] 
													for package in packages 
													if package[1].startswith(_package)]


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

a = Analysis([start_script],
             #pathex=['src', '.'],
             hiddenimports=hidden_imports,
             hookspath=None)

#set up additional eggs into eggs directory
eggs = os.environ.get("EGGS")
if not ( eggs == None or len(eggs)==0 or eggs == '${eggs}'):
	for egg_name in eggs.split(";"): # eggs are separated by ';' sign
		if ( len(egg_name) > 0 ):
			name = egg_name.split("\\")[-1]
			a.zipfiles += [('eggs/' + name, egg_name, 'ZIPFILE',)]		

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
