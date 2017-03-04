#!/usr/bin/env python2
from androguard.misc import *
from sys import argv, exit
from os import makedirs
from os.path import exists

def usage():
    print 'usage: %s <apkfile> [<outputfolder>]' % argv[0]

def main():
    if len(argv) < 2:
        usage()
        exit(0)

    apk = argv[1]
    output = apk[:-4] if apk.endswith('.apk') or apk.endswith('.dex') else apk
    output += apk+'_decompiled'
    if len(argv) == 3:
        output = argv[2]

    if not exists(output):
        makedirs(output)

    if apk.endswith('.apk'):
        a, d, dx = AnalyzeAPK(apk)
    elif apk.endswith('.dex'):
        d, dx = AnalyzeDex(apk)

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
