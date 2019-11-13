import os
import sys

import re
#pattern = re.compile("^([A-Z][0-9]+)+$")
#pattern.match(string)

def write2file(content, filename):
    resultfile = open(filename, 'w+')
    #return the header to the top of the file
    resultfile.seek(0)
    #clear file content
    resultfile.truncate(0)
    #re-write the content
    wsize = resultfile.write(''.join(content))
    #wsize = ifile.write(newContent)
    resultfile.flush()
    resultfile.close()
    return

def GetFilesList(rootdir):
    fileList = []
    for root, subFolders, files in os.walk(rootdir):
        for file in files:
            iFileName = file.strip()
            iMiddleNames = file.split('.')
            extensions = ['c', 'h', 'cpp']
            if iMiddleNames[-1] not in extensions:
                continue
            fileList.append(root + "\\" + iFileName)
    return fileList

def GetFilesExceptSomePathList(rootdir, excluedList):
    fileList = []
    for root, subFolders, files in os.walk(rootdir):
        for file in files:
            iFileName = file.strip()
            #rindex = iFileName.
            iMiddleNames = file.split('.')
            extensions = ['c', 'h', 'cpp']
            if iMiddleNames[-1] not in extensions:
                continue
            if iFileName in excludedList:
                continue
            fileList.append(root + "\\" + iFileName)
    return fileList


def GetSpecificedFileList(rootdir, dirKeyList):
    fileList = []
    for root, subFolders, files in os.walk(rootdir):
        iroot = root
        iroot = iroot.strip()
        iroot_sub = iroot.split('\\')
        bfilefound = True
        for idirKey in dirKeyList:
            if idirKey not in iroot_sub:
                #print('skip dirs:', root)
                bfilefound = False
                break
        if bfilefound == False:
            continue
        #print(keyDir, 'dirs:', root)
        #if 'os' in iroot_sub:
        #    continue
        for file in files:
            iFileName = file.strip()
            #rindex = iFileName.
            iMiddleNames = file.split('.')
            extensions = ['c', 'h', 'cpp']
            if iMiddleNames[-1] not in extensions:
                continue
            fileList.append(root + "\\" + iFileName)
    return fileList

def Replace(files, oldStr, newStr):
    for file in files:
        ifile = open(file, 'r+')

        fcontent = ifile.read()
        icount = fcontent.find(oldStr)
        if icount == -1:
            continue;
        print(icount, " ", file)
        newContent = fcontent.replace(oldStr, newStr)
        #return the header to the top of the file
        ifile.seek(0)
        #clear file content
        ifile.truncate(0)
        #re-write the content
        wsize = ifile.write(''.join(newContent))
        #wsize = ifile.write(newContent)
        ifile.flush()
        ifile.close()
    return

def Find(files, oldStr):
    for file in files:
        ifile = open(file, 'r+')

        lines = ifile.readlines()
        lineNum = 0
        for line in lines:
            lineNum += 1
            index = line.find(oldStr)
            if index != -1:
                print(file, "line No.", lineNum)
                print(line, '\r\n')
        ifile.close()
    return

def FindUserFeatureKey(files):
    uffile = open('mos_utilities_userfeature.txt', 'r+')
    uflines = uffile.readlines()
    ufKey = ""
    ufKeyList=[]
    minStrSize = 10000
    minstr=''
    for line in uflines:
        str = line.strip()
        index = str.find(',')
        if index != -1:
            str = str[:index]
        strSize = len(str)
        if strSize == 0:
             continue
        if not str.startswith('__'):
            continue
        if strSize < minStrSize:
            minStrSize = strSize
            minstr = str
        ufKeyList.append(str)
    uffile.close()
    print('min str: ',  minstr, ':', minStrSize)

    #keystr = '__'
    keydics = {}
    for file in files:
        ifile = open(file, 'r+')

        lines = ifile.readlines()
        lineNum = 0
        for line in lines:
            lineNum += 1
            sline = line.strip()

            if sline.startswith('//') or sline.startswith('#') or sline.startswith('typedef') or sline.startswith('using') or sline.startswith('/*'):
                continue
            index = sline.find('//')
            if index != -1:
                sline = sline[:index]
                sline = sline.strip()
            if len(sline) < minStrSize:
                continue
            if sline.find('__') == -1 or (sline.find('_USER_FEATURE') == -1 and sline.find('__VPHAL') == -1):
                continue

            iKey = 0
            for iufKey in ufKeyList:
                index = sline.find(iufKey)
                if index != -1:
                    keyInfo = {}
                    if iufKey in keydics:
                        keyInfo = keydics[iufKey]
                        keyInfo["file"] = keyInfo["file"] + '\n' + file + ':' + line
                        keyInfo["count"] += 1
                        keydics[iufKey] = keyInfo
                    else:
                        keyInfo["count"] = 1
                        keyInfo["file"] = file + ':' + line
                        keydics[iufKey] = keyInfo
                    break

    content = ''
    for iufKey in ufKeyList:
        keyInfo = {}
        keyInfo = keydics[iufKey]

        content = content + '\n\r' + iufKey + ': ' + '%d' %(keyInfo['count']) + '\n\r' + keyInfo['file'] + '\r\n'
        if keyInfo["count"] == 1:
            print("%s count is: %d"  %(iufKey, keyInfo["count"]))

    write2file(content, 'result.txt')
    return

def MOS_DECLARE_UF_KEY_DBGONLY_Statistics(dir):
    suffix = ['__MEDIA_USER_FEATURE_VALUE_', '__VPHAL_','__MOS_USER_FEATURE_KEY']
    postfix = ['_ID', '_G12']
    token = ''
    bfound = False
    ufStatsDics = {}
    for file in files:
        if file.find('agnostic') == -1 :
            continue
        if file.find('util') == -1 :
            continue
        ifile = open(file, 'r+')

        lines = ifile.readlines()

        for line in lines:
            line = line.strip()

            if bfound == True:
                keyStr = line[:-1]
                if token == '':
                    print('token error')
                if keyStr not in ufStatsDics:
                    keyIdList = [token]
                    ufStatsDics[keyStr] = keyIdList
                else:
                    keyIdList = ufStatsDics[keyStr]
                    keyIdList.append(token)
                    ufStatsDics[keyStr] = keyIdList
                token = ''
                bfound = False
                continue

            if not line.startswith('MOS_DECLARE_UF_KEY_DBGONLY('):
                continue

            str = ''
            index = line.find('__')
            if index != -1:
                token = line[index : -1] # the last one is ','
                bfound = True
            else:
                print('error , file: ', file, ' : ', line )
        ifile.close()
    content = ''

    for ufkey,value in ufStatsDics.items():
        if len(value) > 1:
            print('{ufkey}:{value}'.format(ufkey = ufkey, value = value))
        ids = ''
        for ivalue in value:
            ids = ids + ', ' + ivalue

        content = content + '\n\r' + ufkey + ': '+' %d' %(len(value)) + ids + '\r\n'

    write2file(content, 'result.txt')

    return

if __name__ == '__main__':
    #for iarg in sys.argv[1:]:
    #    index = iarg.find('rootdir:')
    #    if index != -1:
    #        rootdir = iarg[index + 8:]
    #    index = iarg.find('newStr:')
    #rootdir = sys.argv[2]
    #newStr  = sys.argv[3]
    #oldStr  = sys.argv[4]

    #rootdir = "C:\\projects\\VPG\gfx-driver\\Source\\media\\media_embargo\\media_driver_next\\agnostic\\common\\codec\\hal"
    #rootdir = ['C:\\projects\\VPG\\gfx-driver\\Source\\media\\media_driver\\media_driver_next\\agnostic\\common\\shared',
    #           'C:\\projects\\VPG\\gfx-driver\\Source\\media\\media_driver\\media_driver_next\\agnostic\\common\\os',
    #           'C:\\projects\\VPG\\gfx-driver\\Source\\media\\media_driver\\media_driver_next\\linux\\common\\os']
    rootdir = ['C:\\projects\\VPG\\gfx-driver\\Source\\media']

    replace = False
    userfeature = False  #given a uf list to count its usig frequency
    newStr = "MosUtilities::MosSecureStringPrint"
    oldStr= "MOS_SecureStringPrint"
    ufdeclareStat = True    #pick up the uf declared with same name
    for idir in rootdir:
        if replace:
            #dirKey = ['os', 'media_driver_next']
            dirKey = ['media_driver_next']
            mosFiles = GetSpecificedFileList(idir, dirKey)
        files = GetFilesList(idir)
        excludedList = ['mos_utilities_next.cpp']
        uffiles = GetFilesExceptSomePathList(idir, excludedList)
    #for ifile in files:
    #    print(ifile)

    if replace:
        Replace(mosFiles, oldStr, newStr)
    elif userfeature:
        FindUserFeatureKey(uffiles)
    elif ufdeclareStat:
        MOS_DECLARE_UF_KEY_DBGONLY_Statistics(files)
    else:
        Find(files, 'MOS_FillMemory')

