#!/usr/bin/env python

# Copyright 2015 Sascha Schirra
#
# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ropper is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from threading import Thread
import subprocess
import argparse
import sys
import os
import shutil
import time
import psutil

PIN_PATH = './pin'
PIN_TOOL = 'tool/bbltool.so'

def get_files(dir, path=None, extension=None):
    """
    Returns a list of filenames
    
    Arg:
        arg1 (str): directory name
        arg2 (str): path which should be added to the filename in the resultlist
        arg3 (str): a file extension which should filtered for
    """
    
    if not os.path.exists(dir):
        print('path does not exist: %s' % dir)
        exit(1)
    if os.path.isfile(dir):
        print('path has to be a directory')
        exit(1)

    listdir = os.listdir(dir)
    if extension:
        listdir = [ f for f in listdir if f.endswith(extension)]

    if path:
        return [ path + os.path.sep + f for f in listdir]
    return listdir

def read_bbl_file(file, libs):
    to_return = {}
    with open(file) as f:
        for line in f:
            lib, offsets = line.strip().split(': ')

            if not libs or lib.split(os.path.sep)[-1] in libs:
                offsets = offsets.split(',')

                if offsets[-1] == '':
                    offsets = offsets[:-1]

                offsets = [ int(offset) for offset in offsets ]

                to_return[lib] = set(offsets)

    return to_return

def create_bbl_file_for_file(app_string, file, output, cwd, kill=False):
    if not os.path.exists(output):
        os.mkdir(output)

    print file,'....',
    sys.stdout.flush()

    for content in enumerate(app_string):
        if content[1] == '%FILE%':
            app_string[content[0]] = (cwd + '/' + file)
            

    cmd = [PIN_PATH + '/pin', '-ifeellucky', '-t' , PIN_TOOL ,'-o',cwd + '/' + output + '/' + file.split('/')[-1] + '.bbl', '--']
    cmd.extend(app_string)
    f = open(os.devnull, 'w')
   
    p = subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if kill:
        psp = psutil.Process(p.pid)
        old = psp.cpu_times()[0]
        
        while True:
            if psp.children():
                child = psp.children()[-1]
            else:
                child = psp
            time.sleep(1)
            
            if old == psp.cpu_times()[0]:
                p.terminate()
                break;
            old = psp.cpu_times()[0]

        
        
    if p.wait():
        out = p.communicate()
        
        if out[0] or out[1]:
            print 'failed'
            if out[0]:
                print out[0]
            else:
                print out[1]
            
            return 
    print 'finished'        
    
    


def get_count_of_unique_elements(sets, cover):
    """
    Looks for count of unique elements in the sets
    Arg:
        arg1 (dict): dict containint as key lib names and as value a set
        arg2 (dict): dict containint as key lib names and as value a set

    Returns:
        int: number of unique elements
    """
    
    def count(f1, f2):
        uniqueElementCount = 0

        for key in f1:
            if key in f2:
                s = f1[key] - f2[key]
                uniqueElementCount += len(s)
            else:
                uniqueElementCount += len(f1[key])

        return uniqueElementCount
    
    return count(sets, cover)


def update(all, new):
    
    for lib in new:
        if lib in all:
            all[lib] |= new[lib] # if lib in all-dict, update the coverage
        else:
            all[lib] = new[lib] # if lib not in all-dict, add it to the dict

def coverage(bbls):
    """
    Looks for the smallest set of files with the best coverage

    Arg:
        args1 (dict): Dictionary containing the filename as key and as value a list of sets containing the basicblock addresses

    Returns:
        list: list of bbl filenames
    """
    result = []
    most = ['',0] # [filename, count_of_uniques]
    cover = {}
    count = 0
    found_one = False

    while bbls:
        count = 0
        found_one = False
        for bbl in bbls:
            count_of_uniques = get_count_of_unique_elements(bbls[bbl], cover)
            if count_of_uniques >= most[1]:
                most[0] = bbl
                most[1] = count_of_uniques
                found_one = True
            
        if not found_one:
            break
            
        update(cover, bbls[most[0]])
        result.append(most[0])
        
        del bbls[most[0]]
        most = ['',0]

    return result


def get_used_libraries(files):
    """
    Looks for the used libraries in the coverage files
    
    Returns:
		list: all used libs
    """
    to_return = []

    for libs in files.values():
        for lib in libs:
            if lib not in to_return:
                to_return.append(lib)

    return sorted(to_return)


def main(argv):
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
epilog="""example:
Create only coverage files. So it is possible to generate the coverage files on different machines.
coverage.py --files files --bbls bbls --application /usr/bin/evince %FILE% --terminate


Create coverage files and the minimum set of files
coverage.py --files files --bbls bbls --application /usr/bin/evince %FILE% --set set --terminate


Only create the minimum set, when you have existing coverage files.
coverage.py --files files --bbls bbls --set set 


List all used libraries
coverage.py --bbls bbls --list-libraries


Create a set with the best coverage over just a few libs
coverage.py --files files --bbls bbls --set set --only libc.so.6,evince,libjpeg.so.62

""")
    group = parser.add_mutually_exclusive_group(required=True)
    
    parser.add_argument('-f', '--files', metavar='<files>', help='path to files')
    group.add_argument('-a', '--application', metavar='<application string>', help='application string', nargs="+")
    parser.add_argument('-b', '--bbls', required=True,metavar='<output path>', help='the path where the code coverage files should be saved')
    group.add_argument('-s', '--set', metavar='<output path>', help='the path where the minimum set of files should be saved')
    group.add_argument('-l', '--list-libraries', action='store_true',help='prints all the touched libraries used by the application')
    parser.add_argument('-t', '--terminate', action='store_true',help='terminates the process if this idling')
    parser.add_argument('--only', metavar='<libs>',help='a comma separated list which libraries should only use for code coverage analysis')
    
    
    
    args = parser.parse_args(argv)

    if args.set and not args.files:
        parser.error('-s/--set requires -f/--files')
        exit(1)
        
    if args.application and not args.files:
        parser.error('-a/--application requires -f/--files')
        exit(1)

    files_to_analyse = None
    if args.files:
        files_to_analyse = get_files(args.files, path=args.files)

    

    if args.application and files_to_analyse:
        for file in files_to_analyse:

            create_bbl_file_for_file(args.application, file, args.bbls, os.getcwd(), args.terminate)

    files = get_files(args.bbls)
    bbls_per_file = {}
    
    for file in files:
        libs = None
        if args.only:
            libs = args.only.split(',')
        bbls = read_bbl_file(args.bbls + os.path.sep + file, libs)
        if bbls:
            bbls_per_file[file] = bbls
    
    if not bbls_per_file:
        print 'No bbls loaded, maybe because of the libs:', args.only

    if args.list_libraries:
        print('\n'.join([f.split(os.path.sep)[-1] for f in get_used_libraries(bbls_per_file)]))
        exit(0)

    if args.set:
        mset = coverage(bbls_per_file)
        #remove .bbl from the end
        mset = [f.replace('.bbl','') for f in mset]

        if not os.path.exists(args.set):
            os.mkdir(args.set)

        for f in mset:
            shutil.copyfile(args.files + os.path.sep + f, args.set + os.path.sep + f)

        print('\n'.join(mset))




if __name__ == '__main__':
    main(sys.argv[1:])
