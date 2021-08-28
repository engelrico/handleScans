import os
import sys
import errno
import hashlib
import shutil
import time
import datetime
from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
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

def get_page_content(pdf_path):
    text=""
    output_string = StringIO()
    with open(pdf_path, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)
            text=text+" "+output_string.getvalue()
    return text


def findKeywordsInFile(fileName,keywords):
    keywordsInFile = []
    position=0
    page_text=get_page_content(fileName)

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

def getNewFileName(fname,filename_keywords):
    filename_date=""
    head_tail = os.path.split(fname)
    tail=head_tail[1]
    newFileName=""
    if tail[:8].isdigit():
        tmp_date=int(tail[:8])
        if 19000101 <= tmp_date <= 21001231:
            filename_date=str(tmp_date)
            filename_md5=getFileInfo_md5(fname)
            newFileName=head_tail[0]+"/"+filename_date+"_["+filename_keywords+"]_"+filename_md5+".pdf"
        else:
            filename_date=getFileInfo_creationDate_fromFile(fname)
            newFileName=head_tail[0]+"/"+filename_date+"_"+tail
    else:
        filename_date=getFileInfo_creationDate_fromFile(fname)
        newFileName=head_tail[0]+"/"+filename_date+"_"+tail
    return newFileName

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Invalid Numbers of Arguments. Script will be terminated. [whichFolder] [keywordlist]')
    else:
        dirName = str(sys.argv[1])
        keywordlistFilename = str(sys.argv[2])
        print('look into folder:',dirName)


        fileArray = giveFileNamesInDirectory(dirName)
        size=len(fileArray)
        print('numberOfFilesFound',size)

        print('keywords:',keywordlistFilename)
        keywords=giveKeywordlist(keywordlistFilename)
        size=len(keywords)
        print('numberOfKeywordsFound',size)

        for file in fileArray:
           keywordsInFile=findKeywordsInFile(file,keywords)
           filename_keywords=getKeywordString(keywordsInFile)
           print('filename_keywords:'+filename_keywords)
           newFileName=getNewFileName(file,filename_keywords);
           print('new filename'+newFileName)
           moveFile2FolderWithYearName(file)
        print('finished')
