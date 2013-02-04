import os
import subprocess
import codecs

RESOURCES = os.path.dirname(os.path.abspath(__file__))
SOURCES = os.path.join(RESOURCES,'sources')
if not os.path.exists(SOURCES):
    print('Checking out latest source tree')
    subprocess.check_output(['git', 'clone', 'git://github.com/devsnd/cherrymusic.git', SOURCES])
GITPATH = os.path.join(SOURCES,'.git')

def downloadtags():
    print('updating repo...')
    print(subprocess.check_output(['git','--git-dir='+GITPATH, '--work-tree='+SOURCES, 'pull']).split())
    print('DOWNLOADING tagged master versions')
    print('Getting Version info...')
    TAGS=subprocess.check_output(['git','--git-dir='+GITPATH, '--work-tree='+SOURCES, 'tag']).split()
    TAGS=map(lambda x:codecs.decode(x,'UTF-8'),TAGS)
    VERSIONPATH = os.path.join(RESOURCES,'versions')
    if not os.path.exists(VERSIONPATH):
        os.makedirs(VERSIONPATH)
    
    for i in TAGS:
        dldest = os.path.join(VERSIONPATH, 'cherrymusic-'+i+'.tar.gz')
        dlsource = 'https://github.com/devsnd/cherrymusic/tarball/'+i
        if os.path.exists(dldest):
            print('version '+i+' already downloaded, skipping.')
        else:
            print('downloading version '+i+'...')
            dlcmd = 'wget -nv -O '+dldest+' '+dlsource
            try:
                print(codecs.decode(subprocess.check_output(dlcmd.split()),'UTF-8'))
            except subprocess.CalledProcessError:
                print('ERROR donwloading file! https://github.com/devsnd/cherrymusic/tarball/'+i)
                exit(1)
    print('done.')
    
downloadtags()
