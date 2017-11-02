from os import listdir
import argparse
from addNewData import addNewSeq

def main(folder):
    addNew = addNewSeq()
    try:
        listdir(folder)
    except FileNotFoundError:
        print("{} not found in directory".format(folder))
        return

    for filename in listdir(folder):
        print("adding all .vcf files in {}".format(folder))
        if ".vcf" in filename:
            addNew.readVCF(folder, filename)
    print("Done!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Read VCF folder.')
    parser.add_argument('VCF_folder', type=str,
                        help='folder with vcf files to read')

    arg = vars(parser.parse_args())
    main(arg["VCF_folder"])
