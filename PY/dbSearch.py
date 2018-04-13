import sqlite3
import xlrd

def search(chromosome, position, db='worms.db', starvFile='Data/Edit_uFlx_spreadsheet.xlsx'):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    workbook = xlrd.open_workbook(starvFile)
    sheet = workbook.sheet_by_index(2)
    strainName = {}

    for row in range(1, sheet.nrows):
        # for each row in the spreadsheet the strain and date will be added to the dict if it is not in the dict yet
        strainName[sheet.cell_value(row, 1)] = 0
    print("Strains with the alternate allele in chromosome {} in position {}".format(chromosome, position))
    for strain in strainName:
        try:
            c.execute("SELECT value FROM {}RIL WHERE chrom = {} AND position = {} AND value = '1.0'".format(strain, chromosome, position))
            if len(c.fetchall()) > 0:
                print(strain)
        except sqlite3.OperationalError:
            # This is bad practice but we do not care about tables that do not exist
            pass

    conn.commit()
    c.close()
