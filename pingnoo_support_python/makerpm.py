#!/bin/env python3

# Copyright (C) 2019 Adrian Carpenter
#
# This file is part of Pingnoo (https://github.com/nedrysoft/pingnoo)
#
# An open-source cross-platform traceroute analyser.
#
# Created by Adrian Carpenter on 07/02/2021.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import io
import subprocess
import glob
import os
import re
import shutil
import string
import argparse

def execute(command):
    output = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return(output.returncode, output.stdout.decode('utf-8')+output.stderr.decode('utf-8'))

def findPackage(library):
	result, output = execute(f'yum provides {library}')

	#if not output:
	#	return None

	lines = output.splitlines()

	if len(lines):
		parts = lines[1].split(':')

		file = parts[0].rstrip()

		result, output = execute(f'yum info {file}')

		#lines = output.splitlines()

		nameRegex = re.compile(r"Name\s*:\s*(?P<name>.*)")

		lines = output.splitlines()

		for line in lines:
			result = nameRegex.match(line.rstrip())


			if result:
				return result.group('name')

	return None


def rpm_create(buildArch, buildType, version, release):
	controlTemplate = ""

	with open("rpm/pingnoo.spec.in", 'r') as controlFile:
		controlTemplate = string.Template(controlFile.read())

		controlFile.close()

	rpmFolder = f'pingnoo-{version}-{release}.{buildArch}'

	buildRoot = f'bin/{buildArch}/Deploy/rpm//BUILDROOT/{rpmFolder}'

	# remove previous dpkg build tree if it exists

	if os.path.exists(f'bin/{buildArch}/Deploy/rpm'):
		shutil.rmtree(f'bin/{buildArch}/Deploy/rpm')

	os.makedirs(f'bin/{buildArch}/Deploy/rpm/BUILD')
	os.makedirs(f'bin/{buildArch}/Deploy/rpm/BUILDROOT')
	os.makedirs(f'bin/{buildArch}/Deploy/rpm/RPMS')
	os.makedirs(f'bin/{buildArch}/Deploy/rpm/SOURCES')
	os.makedirs(f'bin/{buildArch}/Deploy/rpm/SPECS')
	os.makedirs(f'bin/{buildArch}/Deploy/rpm/SRPMS')

	os.makedirs(f'{buildRoot}/usr/local/bin/pingnoo')
	os.makedirs(f'{buildRoot}/usr/share/icons/hicolor/512x512/apps')
	os.makedirs(f'{buildRoot}/usr/share/applications')
	os.makedirs(f'{buildRoot}/usr/share/doc/pingnoo')
	os.makedirs(f'{buildRoot}/etc/ld.so.conf.d')

	# copy data + binaries into the deb tree

	shutil.copy2(f'bin/{buildArch}/{buildType}/Pingnoo', f'{buildRoot}/usr/local/bin/pingnoo')
	shutil.copy2(f'src/app/images/appicon-512x512-.png', f'{buildRoot}/usr/share/icons/hicolor/512x512/apps/pingnoo.png')

	shutil.copytree(f'bin/{buildArch}/{buildType}/Components', f'{buildRoot}/usr/local/bin/pingnoo/Components', symlinks=True)

	for file in glob.glob(f'bin/{buildArch}/{buildType}/*.so'):
		shutil.copy2(file, f'{buildRoot}/usr/local/bin/pingnoo')

	shutil.copy2(f'dpkg/pingnoo.conf', f'{buildRoot}/etc/ld.so.conf.d')
	shutil.copy2(f'dpkg/copyright', f'{buildRoot}/usr/share/doc/pingnoo')
	shutil.copy2(f'dpkg/Pingnoo.desktop', f'{buildRoot}/usr/share/applications')

	# discover the dependencies

	dependencies = set()
	packagesMap = dict()
	packages = set()
	ignore = set()

	# create list of all shared libraries that the application uses (and at the same time create hashes)

	for filepath in glob.iglob(f'{buildRoot}/usr/local/bin/pingnoo/**/*', recursive=True):
		if os.path.isdir(filepath):
			continue

		ignore.add(os.path.basename(filepath))

		soRegex = re.compile(r"\s*(?P<soname>.*)\s=>")

		resultCode, resultOutput = execute(f'ldd {filepath}')

		for line in io.StringIO(resultOutput):
			if not line:
				continue

			result = soRegex.match(line.rstrip())

			if not result:
				continue

			dependencies.add(result.group("soname"))

	# find which package provides the libraries

	for dep in dependencies:
		if not dep in  packagesMap:
			if dep in ignore:
				continue

			package = findPackage(dep)

			if package:
				packagesMap[dep] = package

				packages.add(package)

	# generate a string of the dependencies

	dependencyList = ''

	for package in packages:
		if not dependencyList:
			dependencyList = package
		else:
			dependencyList = dependencyList+", "+package			

	# create the spec file from the tempalte

	controlFileContent = controlTemplate.substitute(version=version, release=release, dependencies=dependencyList)

	with open(f'bin/x86_64/Deploy/rpm/SPECS/pingnoo.spec', 'w') as controlFile:
		controlFile.write(controlFileContent)

		controlFile.close()

	head_tail = os.path.split(__file__)

	buildCommand = f'rpmbuild --define "_topdir {head_tail[0]}/bin/x86_64/Deploy/rpm" -v -bb bin/x86_64/Deploy/rpm/SPECS/pingnoo.spec'

	resultCode, resultOutput = execute(buildCommand)

	if resultCode==0:
		return(0)

	return(1)

def main():
	parser = argparse.ArgumentParser(description='rpm build script')

	parser.add_argument('--arch',
						choices=['x86_64'],
						type=str,
						default='x86_64',
						nargs='?',
						help='architecture type to deploy')

	parser.add_argument('--type',
						choices=['Release', 'Debug'],
						type=str,
						default='Release',
						nargs='?',
						help='architecture type to deploy')

	parser.add_argument('--version', type=str, nargs='?', help='version')
	parser.add_argument('--release', type=str, nargs='?', help='release')

	args = parser.parse_args()

	rpm_create(args.arch, args.type, args.version, args.release)

if __name__ == "__main__":
	main()
