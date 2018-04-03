from os import listdir
import argparse
from addNewData import addNewSeq

def add(folder):
    addNew = addNewSeq()
    try:
        listdir(folder)
    except FileNotFoundError:
        print("{} not found in directory".format(folder))
        return
    print("adding all .vcf files in {}".format(folder))
    for filename in listdir(folder):
        if ".vcf" == filename[-4:]:
            addNew.readVCF(folder, filename)
    print("Done!")

