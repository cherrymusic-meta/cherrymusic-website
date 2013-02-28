#!/usr/bin/python3
import os
import subprocess
import codecs
import re

RESOURCES = os.path.dirname(os.path.abspath(__file__))
SOURCES = os.path.join(RESOURCES,'sources')
if not os.path.exists(SOURCES):
    print('Checking out latest source tree')
    subprocess.check_output(['git', 'clone', 'git://github.com/devsnd/cherrymusic.git', SOURCES])
GITPATH = os.path.join(SOURCES,'.git')
VERSIONPATH = os.path.join(RESOURCES,'versions')

def utf8(x):
    return codecs.decode(x,'UTF-8')

def downloadtags():
    print('updating repo...')
    print(utf8(subprocess.check_output(['git','--git-dir='+GITPATH, '--work-tree='+SOURCES, 'pull'])))
    print('DOWNLOADING tagged master versions')
    print('Getting Version info...')
    TAGS=subprocess.check_output(['git','--git-dir='+GITPATH, '--work-tree='+SOURCES, 'tag']).split()
    TAGS=map(utf8,TAGS)
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
    print('adding all versions to repo...')
    print(utf8(subprocess.check_output(['git','add',VERSIONPATH+'/*'])))
    print('done.')
    
def generateWebsite():
    with open('index.html','w') as index:
        index.write(readFile('head.html'))
        index.write("""
            <!---- DO NOT CHANGE THE INDEX FILE. 
                    IT IS GENERATED AUTOMATICALLY.
            ------>
""")
        index.write(generateDownload())
        index.write(readFile('sources.html'))
        index.write(readFile('screenshots.html'))
        index.write(generateChanges())
        index.write(readFile('about.html'))
        index.write(readFile('tail.html'))
    
def readFile(filename):
    with open(filename,'r') as fh:
        return fh.read()

def generateDownload():
    get_version_by_filename = lambda x: re.findall('(\d\.\d+(\.\d+)?)',x)[0][0]
    filetolink = lambda x : 'http://www.fomori.org/cherrymusic/versions/'+x
    listify = lambda x : '<li><a href="'+filetolink(x)+'">version '+get_version_by_filename(x)+'</a></li>'
    allversions = sorted(os.listdir(VERSIONPATH),reverse=True,key=lambda x :int(re.sub('\D','',x)))
    with open('download.html') as dl:
        dldata = dl.read()
        dldata = dldata.replace("<!--LATEST_VERSION_URL-->",filetolink(allversions[0]))
        dldata = dldata.replace("<!--LATEST_VERSION_NUMBER-->",get_version_by_filename(allversions[0]))
        dldata = dldata.replace("<!--OLD_VERSIONS-->",'\n'.join(map(listify, allversions[1:])))
        return dldata
        
def generateScreenshots():
    return ''

def generateChanges():
    ret = '<div class="accordion-group">'
    with open(SOURCES+'/CHANGES','r') as changelog:
        currentVersion = ''
        for line in changelog.readlines():
            if(line.startswith('0')):
                if not currentVersion == '':
                    ret += '''</ul></div></div>'''
                currentVersion = line
                htmlVersion = line.split()[0].replace('.','-')
                ret += """
            <div class="accordion-heading">
                <a class="accordion-toggle" data-toggle="collapse" data-parent="#accordion2" href="#collapse{1}">
                    <p>{0}</p>
                </a>
            </div>
            <div id="collapse{1}" class="accordion-body collapse">
                <div class="accordion-inner">
                    <ul>""".format(currentVersion,htmlVersion)
            elif line.startswith(' - '):
                ret += '<li>'+line[3:]+'</li>'
    ret += '''</ul></div></div>'''
    ret += '</div>'
    return readFile('changes.html').replace('<!--CHANGELOG-->',ret)

    
downloadtags()
generateWebsite()
