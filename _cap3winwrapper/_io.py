import csv

def _read_design(pathToDesign,listOfTemplates):
    """
    Reads a sequencing reads design file: a tab-separated file in which each
    line either begins with # (a comment line, ignored) or begins with the
    name of a sequencing template followed by entries for each sequencing
    read, in the format RUN_READ. READ but not RUN may contain the underscore
    character.

    pathToDesign: the path to the design file
    listOfTemplates: a list of template names to read. Lines not containing
        a name in this list are skipped, and if a template is not found in
        the design file a ValueError is raised. If None, all non-comment
        lines are read.

    Returns a dictionary in which each key TEMPLATE returns a list of 
    RUN_READ:FIRST-LAST.
    """

    if listOfTemplates is not None:
        setTmp=set(listOfTemplates)
    else:
        setTmp=None

    fileDes=open(pathToDesign,"r")
    linesDes=fileDes.readlines()
    fileDes.close()

    # Make a dict of reads, removing comment lines and unspecified templates
    dictDes={}
    for line in linesDes:
        if line[0]!="#":
            lineSpl=line.strip().split("\t")
            if (setTmp is None) or \
                    ((setTmp is not None) and (lineSpl[0] in setTmp)):
                dictDes[lineSpl[0]]=lineSpl[1:]

    # Check that all templates are found in the dict
    if setTmp is not None:
        setTmpDes=set(dictDes.keys())
        for tmp in setTmp:
            if tmp not in setTmpDes:
                raise ValueError(
                        "".join(["Template ",tmp," not found in design file"]))

    return dictDes

def _write_cap_sh(name,pathToCAP3,dictDes):
    """
    Writes a .sh executable that can be read by Cygwin 32-bit, allowing
    the user to run CAP3 to assemble the contigs for each template in
    a design dictionary.

    name: the name of the executable, ending in .sh
    pathToCAP3: the path to the CAP3 executable, but not containing .sh
    dictDes: the design dictionary generated by _read_design

    Writes the executable to 'name'.
    """

    lines=list()
    lTemp=list(dictDes.keys())
    for temp in lTemp:
        line="".join([pathToCAP3," ",temp," > ",temp,".out &","\n"])
        lines.append(line)
    sh=open(name,mode="w",newline="\n")
    sh.writelines(lines)
    sh.close()

