import click
import sqlite3
from seqToDb import seqToDB
from addVCF import add
from addNewData import addNewSeq, addNewStarve
from dbToOutput import writePheno, writeGeno
from dbSearch import search

@click.command()
@click.option('--new_db', '-newdb', default="", help="Create a new database using a genotype TSV file. "
                                                              "Use -name and -strv to specify name and phenotype data if needed."
                                                              "Name defaults to worms.db and strv defaults to spreadsheet in ./Data")
@click.option('--add_vcf', '-addvcf', default="", help="Takes the location of a directory to add vcf files")
@click.option('--add_tsv', '-addtsv', default='', help='Takes the location of a new or updated tsv file to add to DB.'
                                                       'DB can be specified using -name')
@click.option('--add_strv', '-addstrv', default="", help='Takes the location of a new or updated Phenotype spreadsheet to add to DB'
                                                         'DB can be specified using -name')
@click.option('--ped', '-P', default="", help='Takes the location of the Phenotype file to create ped file for PLINK. Use -name '
                                  ' to specify the name if needed')
@click.option('--pedr', '-PR', default="", help='Takes the location of the Phenotype file to create ped file for PLINK. Use -name '
                                  ' to specify the name if needed')
@click.option('--map', '-M', default=False, is_flag=True ,help='Creates map file for PLINK. No arguments needed')
@click.option('--mapr', '-MR', default=False, is_flag=True ,help='Creates map file for PLINK using RIL data. No arguments needed')
@click.option('--db_name', '-name', default='worms.db', help='Creates a custom name for db using -newdb')
@click.option('--db_strv', '-strv', default='Data/Edit_uFlx_spreadsheet.xlsx', help='Takes the location of the phenotype data to use to create new_db')
@click.option('--add_ril', '-addril', default="", help='Takes the location of the RIL data to add to DB')
@click.option('--searchp', '-search', default="" ,help='Takes position number and chromosome as input and searches database according to Heathers spreadsheet. Use with -chrome to add chromosome you are searching on')
@click.option('--chrome', '-chrome', default="",help='Use with -search to add chromosome you want to look at')


def main(new_db, add_vcf, add_tsv, add_strv, ped, pedr, map, mapr, db_name, db_strv, add_ril, searchp, chrome):
    if new_db is not "":
        conn = sqlite3.connect(db_name)
        new = seqToDB(conn, db_strv)
        new.prepDB(new_db)
        new.addToDb()
        new.addStarvation()

    elif add_vcf is not "":
        if db_name is not "":
            add(add_vcf, db_name)
        else:
            add(add_vcf)
    elif add_tsv is not "":
        seq = addNewSeq(add_tsv, db_name)
        seq.prepDB(add_tsv)
        seq.addNew()
    elif add_strv is not "":
        stv = addNewStarve(add_strv, db_name)
        stv.addStarvation()
    elif ped is not "":
        write_ped = writePheno(ped, dbName=db_name)
        write_ped.writeOutput()
    elif pedr is not "":
        write_ped = writePheno(pedr, dbName=db_name)
        write_ped.writeOutputRIL()
    elif map:
        write_geno = writeGeno()
        write_geno.writeOutput()
    elif mapr:
        write_geno = writeGeno()
        write_geno.writeOutputRIL()
    elif add_ril is not "":
        seq = addNewSeq(add_ril, db_name)
        seq.addRIL(add_ril)
    elif (searchp, chrome) is not ("", ""):
        search(chrome, searchp)



## What I need to implement
##
## Create New database, option = -new, calls seqToDb
## Takes a tsv file (for now) and excel sheet 3 like Heathers current file. Leave like this until need to change
##
## Add multiple vcf files, option = -vcf
## Takes the location or name of a directory containing vcf files to be added
##
## Add new data from tsv, option = -tsv
## Takes in the location of the file you would like to add to db. will only add strains not in db
##
## Add new starvation, option = -strv
## Takes location of new station file and will add from the 3 sheet of the file like how heather has it
##
## Write PED, option = -P
## Takes in 3 optional arguments, Starvation file, output name, dbName
##
## Write MAP, option -G
## takes no arguments just runs when called


if __name__ == "__main__":
    main()