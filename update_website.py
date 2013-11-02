#!/usr/bin/python3
import os
import subprocess
import codecs
import re
import shutil

RESOURCES = os.path.dirname(os.path.abspath(__file__))
PATH_SOURCES = os.path.join(RESOURCES, 'cherrymusic_sources')
GITPATH_SOURCES = os.path.join(PATH_SOURCES,'.git')
PATH_WIKI = os.path.join(RESOURCES,'wiki')
GITPATH_WIKI = os.path.join(PATH_WIKI,'.git')

MAIN_TEMPLATE = os.path.join(RESOURCES, 'template.html')
PAGES_SOURCE_PATH = os.path.join(RESOURCES, 'pages.src')
DEPLOY_PATH = os.path.join(RESOURCES, 'deploy')
ASSET_PATH =  os.path.join(RESOURCES, 'pages.assets')

SCREENSHOTDIR = os.path.join(ASSET_PATH, 'screenshots')
SCREENSHOTTHUMBS = os.path.join(SCREENSHOTDIR,'thumb')
SCREENSHOTSABS = os.path.join(RESOURCES,SCREENSHOTDIR)

VERSIONPATH = os.path.join(ASSET_PATH,'versions')

INDEX = 'Home'

if not os.path.exists(PATH_SOURCES):
    print('Checking out latest source repo')
    subprocess.check_output(['git', 'clone', 'git://github.com/devsnd/cherrymusic.git', PATH_SOURCES])
if not os.path.exists(PATH_WIKI):
    print('Checking out latest wiki repo')
    subprocess.check_output(['git', 'clone', 'git://github.com/devsnd/cherrymusic.wiki.git', PATH_WIKI])
if not os.path.exists(DEPLOY_PATH):
    os.mkdir(DEPLOY_PATH)

def utf8(x):
    return codecs.decode(x,'UTF-8')

def downloadtags():
    print('updating wiki repo...')
    print(utf8(subprocess.check_output(['git','--git-dir='+GITPATH_WIKI, '--work-tree='+PATH_WIKI, 'pull'])))
    print('updating sources repo...')
    print(utf8(subprocess.check_output(['git','--git-dir='+GITPATH_SOURCES, '--work-tree='+PATH_SOURCES, 'pull'])))
    print('DOWNLOADING tagged master versions')
    print('Getting Version info...')
    TAGS=subprocess.check_output(['git','--git-dir='+GITPATH_SOURCES, '--work-tree='+PATH_SOURCES, 'tag']).split()
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
    print('adding all master versions to website repo...')
    print(utf8(subprocess.check_output(['git','add',VERSIONPATH+'/*'])))
    print('done.')

def source_to_page_file_name(filename):
    if source_to_page_title(filename) == INDEX:
        return 'index.html'
    return filename[filename.index('.')+1:]

def source_to_page_title(filename):
    return filename[filename.index('.')+1:filename.rindex('.')]

def generateNavigation(filenames, active_file):
    htmlli = ''
    for filename in filenames:
        active = 'active' if filename == active_file else ''
        data = (active, source_to_page_file_name(filename), source_to_page_title(filename))
        htmlli += '\t<li class="%s"><a href="%s">%s</a></li>\n' % data
    return '<ul class="nav nav-tabs" id="myTab">\n' + htmlli + '</ul>\n'

def generateWebsite():
    main_template = readFile(MAIN_TEMPLATE)
    page_file_names = [p for p in sorted(os.listdir(PAGES_SOURCE_PATH)) if p.endswith('.html')]
    for page_file_name in page_file_names:
        page_file_path = os.path.join(PAGES_SOURCE_PATH, page_file_name)
        content = readFile(page_file_path)
        if '<!--SCREENSHOT-SECTION-->' in content:
            content = generateScreenshotSection(content)
        if '<!--CHANGELOG-->' in content:
            content = generateChanges(content)
        if '<!--DOWNLOAD-PAGE-->' in content:
            content = generateDownload(content)
        nav = generateNavigation(page_file_names, page_file_name)
        content = main_template.replace('<!--PAGE-CONTENT-->', content)
        content = content.replace('<!--NAVIGATION-->', nav)
        content = content.replace('<!--TITLE-->', source_to_page_title(page_file_name))
        deploy_page_file_name = source_to_page_file_name(page_file_name)
        writeFile(os.path.join(DEPLOY_PATH, deploy_page_file_name), content)

def readFile(filename):
    with open(filename,'r') as fh:
        return fh.read()

def writeFile(filename, content):
    with open(filename, 'w') as outfh:
        outfh.write(content)

def generateDownload(content):
    get_version_by_filename = lambda x: re.findall('(\d\.\d+(\.\d+)?)',x)[0][0]
    filetolink = lambda x : 'http://www.fomori.org/cherrymusic/versions/'+x
    listify = lambda x : '<li><a href="'+filetolink(x)+'">version '+get_version_by_filename(x)+'</a></li>'
    allversions = sorted(os.listdir(VERSIONPATH),reverse=True,key=lambda x :int(re.sub('\D','',x)))
    content = content.replace("<!--LATEST_VERSION_URL-->",filetolink(allversions[0]))
    content = content.replace("<!--LATEST_VERSION_NUMBER-->",get_version_by_filename(allversions[0]))
    content = content.replace("<!--OLD_VERSIONS-->",'\n'.join(map(listify, allversions[1:])))
    return content
        
def generateScreenshotSection(content):
    if not os.path.exists(SCREENSHOTTHUMBS):
        os.mkdir(thumbnaildir)
    return content.replace("<!--SCREENSHOT-SECTION-->",generateScreenshotList(192))

def resizeImage(imagepath,size):
    with open(os.devnull,'w') as devnull:
        imgsize = str(size[0])+'x'+str(size[1])
        cmd = ['convert', imagepath, '-resize', imgsize, 'png:-']
        im = subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        data = im.communicate()[0]
        return data

def generateScreenshotList(imgsize):
    print('Creating screenshot thumbnails, if necessary...')
    for shot in sorted(os.listdir(SCREENSHOTSABS)):
        screenshotfileabs = os.path.join(SCREENSHOTSABS,shot)
        screenshotfile = os.path.join(SCREENSHOTDIR,shot)
        screenshotthumb = os.path.join(SCREENSHOTTHUMBS,shot)
        if not os.path.exists(screenshotthumb) and screenshotfile.endswith('.png'):
            print('Creating thumbnail for '+shot)
            with open(screenshotthumb, 'wb') as thumbfile:
                thumbfile.write(resizeImage(screenshotfileabs, (imgsize,imgsize)))
                
    images = []
    for shot in sorted(os.listdir(SCREENSHOTSABS)):
        images.append( (os.path.join(SCREENSHOTDIR,shot), os.path.join(SCREENSHOTTHUMBS,shot)) )
    rethtml = ''
    for n in range(len(images)//4+1):
        rethtml += '<div class="row">'
        for image in images[n*4:n*4+4]:
            rethtml +='''
            <div class="span3">
                <a href="%s" class="screen" rel="lightbox" >
                <img height="%d" src="%s" /><br></a>
            </div>
            '''%(image[0],imgsize,image[1])
        rethtml += '</div>'    
    return rethtml

def generateChanges(content):
    ret = '<div class="accordion-group">'
    with open(PATH_SOURCES+'/CHANGES','r') as changelog:
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
    return content.replace('<!--CHANGELOG-->',ret)

if __name__ == '__main__':
    downloadtags()
    # remove old deployment
    shutil.rmtree(DEPLOY_PATH)
    # copy assets
    shutil.copytree(ASSET_PATH, DEPLOY_PATH)
    generateWebsite()
