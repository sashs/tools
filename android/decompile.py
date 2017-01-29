#!/usr/bin/env ipython2
from androlyze import *
from sys import argv
from os import makedirs
from os.path import exists

def usage():
    print 'usage: %s <apkfile> [<outputfolder>]' % argv[0]

def main():
    if len(argv) < 2:
        usage()

    apk = argv[1]
    output = apk[:-4] if apk.endswith('.apk') else apk
    output += apk+'_decompiled'
    if len(argv) == 3:
        output = argv[2]

    if not exists(output):
        makedirs(output)

    a, d, dx = AnalyzeAPK(apk)

    for cls in d.get_classes():
        name = cls.get_name()
        if name.startswith('L'):
            name = name[1:]
        if name.endswith(';'):
            name = name[:-1]

        path = output
        file = name
        if '/' in name:
            path += '/' + name[:name.rindex('/')]
            file = name[name.rindex('/')+1 :]



        if not exists(path):
            makedirs(path)
        with open(path + '/' + file + '.java', 'w') as f:

            f.write(cls.get_source())

if __name__ == '__main__':
    main()
