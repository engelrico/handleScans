import os
import sys
import errno
import PyPDF2
import hashlib
import shutil
import time
import datetime
from datetime import datetime


def giveFileNamesInDirectory(dirName):
    fileArray = []
    for file in os.listdir(dirName):
        if file.endswith(".pdf"):
            fileArray.append(os.path.abspath(dirName+"/"+file))
    return fileArray

def giveKeywordlist(fileName):
    lines = []
    text_file = open(fileName, "r")
    lines = text_file.readlines()
    text_file.close()
    #remove newLines and blanks
    lines = [item.strip() for item in lines]
    return lines

def get_page_content(page):
    rsrcmgr = PDFResourceManager()
    output = StringIO()
    device = TextConverter(rsrcmgr, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    interpreter.process_page(page)
    return output.getvalue()


def findKeywordsInFile(fileName,keywords):
    keywordsInFile = []
    position=0
    page_text=""
    # open the pdf file
    object = PyPDF2.PdfFileReader(fileName)
    # get number of pages
    NumPages = object.getNumPages()
    for i in range(0, NumPages):
        PageObj = object.getPage(i)
        page_text = page_text+PageObj.extractText().lower()

    for keyword in keywords:
        if keyword in page_text:
            keywordsInFile.append(keyword)
    return keywordsInFile

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def getKeywordString(foundKeywords):
    keywordString=""
    foundKeywords=foundKeywords[0:4]
    keywordString='.'.join(str(x) for x in foundKeywords)
    return keywordString

def getFileInfo_md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def getFileInfo_creationDate_fromFile(fname):
    creationDate=datetime.fromtimestamp(os.path.getctime(fname)).strftime("%Y%m%d" )
    return creationDate


def getYearFolderName(fname):
#when was this file created
    creationDate=getFileInfo_creationDate_fromFile(fname)
#we take only the year
    yearFromMetadata=int(creationDate[:4])
    year=yearFromMetadata
#split the full filepath into directory=head and filename=tail
    head_tail = os.path.split(fname)
#if the fileName was generate some time ago it could contain the 'better' creationdate
    if head_tail[1][:4].isdigit():
        yearFromFileName=int(head_tail[1][:4])
        if 1990 <= yearFromFileName <= 2100 and yearFromFileName < yearFromMetadata:
            year=yearFromFileName
    return year


def moveFile2FolderWithYearName(fname):
    year=getYearFolderName(fname)
    #split the full filepath into directory=head and filename=tail
    head_tail = os.path.split(fname)
#lets build the destinationFileName
    destinationPath=head_tail[0] +"/"+ str(year) + "/"
    destination= destinationPath + head_tail[1]
    print("###move: ",fname,"   ",destination)
    make_sure_path_exists(destinationPath)
    #shutil.move(fname,destination)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Invalid Numbers of Arguments. Script will be terminated.')
    else:
        dirName = str(sys.argv[1])
        print('look into folder:',dirName)
        fileArray = giveFileNamesInDirectory(dirName)
        fileArraySize=len(fileArray)
        print('numberOfFilesFound',fileArraySize)
        for file in fileArray:
           moveFile2FolderWithYearName(file)
        print('finished')
