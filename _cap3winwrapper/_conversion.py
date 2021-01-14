import os
import glob
from Bio import SeqIO

def _design2paths(dictDes,pathToReads):
    """
    Matches entries in a read design dictionary (generated by _read_design) to
    .ab1 sequence files and folders in a directory.

    dictDes: the design dictionary, in which keys named TEMPLATE return a list
        of entries in the form RUN_READ
    pathToReads: the directory to search

    Returns a dictionary in which each key TEMPLATE returns a list of paths to
    .ab1 files.
    """

    lTemp=list(dictDes.keys())
    dictPaths={}
    for temp in lTemp:
        lPaths=[]
        for read in dictDes[temp]:
            readSpl=read.split("_",1) # Split read name at first underscore
            if len(readSpl)!=2:
                raise ValueError(
                        "".join(["Read name ",read," does not contain _"]))
            pathPattern=os.path.join(
                    pathToReads,
                    "".join(["*",readSpl[0],"*"]),
                    "".join(["*",readSpl[1],"*",".ab1"]))
            pathExp=glob.glob(pathPattern)
            if len(pathExp)!=1:
                if len(pathExp)==0:
                    raise ValueError(
                            "".join(["Read ",read," does not match a file"]))
                elif len(pathExp)>1:
                    raise ValueError(
                            "".join(["Read ",read," matches multiple files"]))
            lPaths.append(pathExp[0])
        dictPaths[temp]=lPaths

    return dictPaths

def _ab2faqual(dictDes,dictPaths):
    """
    Using a design dictionary and a dictionary of .ab1 paths, constructs, for
    each .ab1 file, a .fa file (without file extension) and .qual file whose
    file name matches the dictionary key and whose sequence names match those
    in the design dictionary.

    dictDes: the design dictionary, in which keys named TEMPLATE return a list
        of entries in the form RUN_READ
    dictPaths: the paths dictionary, in which keys named TEMPLATE return a
        list of file paths in the same order as dictDes

    Writes the .fa and .qual files to the working directory.
    """

    lTemp=list(dictDes.keys())
    for temp in lTemp:

        # Read in all the .ab1 files sequenced from the template
        lSeq=list()
        for i in range(len(dictDes[temp])):
            lSeq.append(SeqIO.read(dictPaths[temp][i],"abi"))
            lSeq[i].id=dictDes[temp][i]

        # Write the .fa and .qual files using UNIX-style line endings
        fa=open(temp,mode="w",newline="\n")
        SeqIO.write(lSeq,fa,"fasta")
        fa.close()
        qual=open("".join([temp,".qual"]),mode="w",newline="\n")
        SeqIO.write(lSeq,qual,"qual")
        qual.close()
