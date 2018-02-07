import pandas as pd
import sqlite3
import xlrd
from os import listdir

# Need to add: Values from starvation excel
#              Finding more than one similar value in strains
#
class seqToDB:
    # This class takes in a string file name (defaulted to current data) and dbName
    # and adds it to a database
    # Files are given a default value to match location in my computer for now
    def __init__(self, dbConn, starvFile = 'Data/Edit_uFlx_spreadsheet.xlsx'):
        self._db = dbConn
        self.createCursor()
        # Creates workbook for grabbing data from the excel sheet
        workbook = xlrd.open_workbook(starvFile)
        self._sheet = workbook.sheet_by_index(2)

    def prepDB(self, tsvFile):

        df = pd.read_csv(tsvFile, delimiter='\t')
        # ref1 is the column of all position values
        df1 = df.set_index('pos_ws220').T
        self._df2 = df1.drop(df1.index[0])
        
        #chroPos is used to grab pos and chrom values
        #ref2 is the first sequence
        chroPos = df.set_index('ref_allele').T
        chrom = chroPos.drop(chroPos.index[1:])
        pos = chroPos.drop(chroPos.index[2:])
        pos = pos.drop(pos.index[0])
        
        # Creates an array to hold all the position values as strings
        self._chrome = []
        chromOptions = {'I' : '1',
                        'II' : '2',
                        'III' : '3',
                        'IV' : '4',
                        'V' : '5',
                        'X' : 'X'}
        
        self._chrome = [chromOptions[val] for index, row in chrom.iterrows() for val in row]

        for index, row in chrom.iterrows():
            for val in row:
                self._chrome.append(chromOptions[val])
                    
        self._positions = [str(val) for index, row in pos.iterrows() for val in row]

        
        # Creates the sequence and starvation table
        self._c.execute('CREATE TABLE IF NOT EXISTS strain(strain_id INTEGER PRIMARY KEY, strain_name TEXT)')
        self._c.execute('CREATE TABLE IF NOT EXISTS seq(position TEXT, chrom TEXT, strain_id INTEGER, value TEXT, FOREIGN KEY(strain_id) REFERENCES strain(strain_id))')
        self._c.execute('CREATE TABLE IF NOT EXISTS starvation(individual_id INTEGER, strain_id INTEGER , date TEXT, scanner TEXT, frame INTEGER, correction INTEGER, survival FLOAT, censor INTEGER, FOREIGN KEY(strain_id) REFERENCES strain(strain_id))')
        self.closeCursor()
        
    def createCursor(self):
        self._c = self._db.cursor()

    def closeCursor(self):
        self._db.commit()
        self._c.close()
        

    def addToDb(self):

        # Goes through the seq file and adds it into your database
        count = 0
        strainID = 0
        self.createCursor()
        
        print('Adding file to db...')
        
        for index, row in self._df2.iterrows():
            print("Adding " + index)
            self._c.execute('INSERT INTO strain VALUES(?,?)', (strainID, index))
            # Index is the name of the Strain and row is the whole sequence
            for val in row:
                self._c.execute('INSERT INTO seq VALUES(?,?,?,?)', (self._positions[count], self._chrome[count], strainID, val))
                count += 1
                
            strainID += 1
            count = 0
            
        self.closeCursor()
        print('Done!')

    def addStarvation(self):

        
        # Adds starvation file to your database
        self.createCursor()
        print('Adding file to db...')
        strainId = 0
        self._c.execute("SELECT * FROM strain")
        strainCount = len(self._c.fetchall())

        # Adds in value from each row
        for row in range(1, self._sheet.nrows):
            currStrain = self._sheet.cell_value(row, 1)
            self._c.execute("SELECT strain_id FROM strain WHERE strain_name = ?", (currStrain,))
            result = self._c.fetchall()

            if len(result) is 0:
                strainId = strainCount
                self._c.execute('INSERT INTO strain VALUES(?,?)', (strainCount, currStrain))
                strainCount += 1
            else:
                strainId = result[0][0]
        
            self._c.execute('INSERT INTO starvation VALUES(?,?,?,?,?,?,?,?)', (self._sheet.cell_value(row, 0), strainId, self._sheet.cell_value(row, 2), self._sheet.cell_value(row, 3), self._sheet.cell_value(row, 4), self._sheet.cell_value(row, 5), self._sheet.cell_value(row, 6), self._sheet.cell_value(row, 7)))

        self.closeCursor()
        print('Done!')

    def avgStarveTime(self, strain):
        # Takes a string arg for the strain and returns the average for that strain
        self.createCursor()
        self._c.execute("SELECT survival FROM starvation JOIN strain USING (strain_id) WHERE strain_name = ?", (strain,))
        result = self._c.fetchall()

        if len(result) is 0:
            print("{} not found in database".format(strain))
            return
        
        #Cleans up list that fecthall return
        totArr = [i[0] for i in result]
        avg = sum(totArr) / len(totArr)
        
        print("Average starvation time for {} is {:.2f} hours".format(strain, avg))
        self.closeCursor()

        #return avg
        
    def select(self, pos, val):
        # Selects a single value (ex. 'C') at a single positions across all Strains
        
        self.createCursor()
        self._c.execute("SELECT strain_name FROM strain JOIN seq USING (strain_id) WHERE position = ? AND value = ?", (pos, val))
        
        result = self._c.fetchall()
        
        print(str(len(result)) + " strains with {} at position {}".format(val, pos))
        
        for r in result:
            print(r[0])
            
        self.closeCursor()

    def readVCF(self, folder, vcf):
        f = open("{}/{}".format(folder, vcf), "r")
        try:
            lab = "{}/labsource.txt".format(folder)
            g = open(lab, "r")
            labName = g.read()
            strain = "{}_{}".format(vcf.split(".")[0], labName)
            g.close()
        except FileNotFoundError:
            print("No labsource file for {}".format(vcf.split(".")[0]))
        strain = vcf.split(".")[0]


        self.createCursor()
        # Checking to see if strain is in db already
        self._c.execute("SELECT strain_id FROM strain where strain_name = ?", (strain,))
        test = self._c.fetchall()
        if len(test) > 0:
            print("{} is already in db skipping...".format(strain))
            self.closeCursor()
            f.close()
            return

        print("adding {}".format(strain))
        self._c.execute("SELECT * FROM strain")
        strainCount = len(self._c.fetchall())
        self._c.execute('INSERT INTO strain VALUES(?,?)', (strainCount, strain))

        for line in f:
            if line[0] is not "#":
                vals = line.split()
                chrom = vals[0]
                val = vals[4]
                pos = vals[1]

                if val == ".":
                    val = "?"
                self._c.execute('INSERT INTO seq VALUES(?,?,?,?)',
                                (pos, chrom, strainCount, str(val)))

        self.closeCursor()
        f.close()
