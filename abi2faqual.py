def abi2faqual(pathsAB1,seqNames,contName):
    """
    Def to convert a list of .ab1 files to a single .fasta file with matching .qual file
    By William D. Jones, 2020-05-31
    """

    #Import packages
    from Bio import SeqIO

    #Generate the complete SeqRecord list, with corrected names
    seqList=list()
    for i in range(len(pathsAB1)):
        seqList.append(SeqIO.read(pathsAB1[i],"abi"))
        seqList[i].id=seqNames[i] #Change the ID of the sequence using the specified names list

    #Write the .fasta file using UNIX-style line endings
    faFile=open(contName,mode="w",newline="\n")
    SeqIO.write(seqList,faFile,"fasta")
    faFile.close()
    qualFile=open(contName+".qual",mode="w",newline="\n")
    SeqIO.write(seqList,qualFile,"qual")
    qualFile.close()

#Import packages
import argparse
import csv
import os
import fnmatch

#Parse command-line arguments
parserMain=argparse.ArgumentParser()
parserMain.add_argument("designfile",help="Tab-separated design file containing the vector name and sequencing reads in the format RUNNAME_SAMPLENAME",type=str)
parserMain.add_argument("readpath",help="Parent path of the run directories containing .ab1 reads",type=str)
parserMain.add_argument("-c","--cap3run",help="Name of the CAP3 .sh executable to be generated by this program, followed by a space and the location of the CAP3 executable in Cygwin format without any executable extensions, example: MYCAP.sh /cygdrive/c/CAP3/cap3",type=str,nargs=2)
argsMain=parserMain.parse_args()

#Import the tab-separated variable file containing the design for the run
with open(argsMain.designfile,mode="r") as desHandle:
    desReader=csv.reader(desHandle,delimiter="\t")
    desData=list(desReader)

#Get the contig names, the read names, and the paths to the sequencing reads from the design file
contName=list()
seqNames=list()
readPaths=list()
for i in range(len(desData)):
    #Get the contig name
    contName.append(desData[i][0])
    #Get the names of the sequencing reads
    currSeqNames=list()
    for j in range(1,len(desData[i])):
        if desData[i][j]!="":
            currSeqNames.append(desData[i][j])
    seqNames.append(currSeqNames)
    #Use the names of the sequencing reads to construct the path to the reads
    currReadPaths=list()
    for j in range(len(seqNames[i])):
        currReadName=(seqNames[i][j]).split("_")
        seqFolder="DNACORE_REQ_"+currReadName[0]
        seqParPath=os.path.join(argsMain.readpath,seqFolder)
        seqPattern="*."+currReadName[1]+"_*.ab1"
        #Use the pattern to match the file, which if the read hierarchy is constructed correctly should be unique
        for currFile in os.listdir(seqParPath):
            if fnmatch.fnmatch(currFile,seqPattern):
                currReadPaths.append(os.path.join(seqParPath,currFile))
                break #Because the match should be unique
    readPaths.append(currReadPaths)

#Do the conversion and, if requested, construct the CAP3 batch file
batchLines=list()
batchName=argsMain.cap3run[0]
capPath=argsMain.cap3run[1]
for i in range(len(contName)):
    #Do the conversion
    abi2faqual(pathsAB1=readPaths[i],seqNames=seqNames[i],contName=contName[i])
    #Write the UNIX command for CAP3
    batchLines.append([capPath+" "+contName[i]+" > "+contName[i]+".out &"])
#Make the batch file
with open(batchName,mode="w",newline="\n") as batchFile:
    shWriter=csv.writer(batchFile,dialect="unix",quoting=csv.QUOTE_NONE)
    shWriter.writerows(batchLines)
