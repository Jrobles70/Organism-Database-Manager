import pandas as pd
import sqlite3
import xlrd
from seqToDb import *

class addNewSeq(seqToDB):
    def __init__(self, newFile= 'data/seq_data_target_lines-jan2017.tsv', db = 'worms.db'):
        conn = sqlite3.connect(db)
        seqToDB.__init__(self, fi = newFile, dbConn = conn)

    def addNew(self):
        count = 0
        self.createCursor()

        self._c.execute("SELECT strain_name FROM strain")
        names = self._c.fetchall()
        strainID = len(names)

        for index, row in self._df2.iterrows():
            if (index,) not in names:  
                print('Adding ' + index)
                self._c.execute('INSERT INTO strain VALUES(?,?)', (strainID, index))
                # Index is the name of the Strain and row is the whole sequence
                for val in row:
                    self._c.execute('INSERT INTO seq VALUES(?,?,?,?)', (self._positions[count], self._chrome[count], strainID, val))
                    count += 1
                
                strainID += 1
                count = 0
            
        self.closeCursor()
        print('Done!')

class addNewStarve(seqToDB):
    def __init__(self, newFile, db = 'worms.db'):
        seqToDB.__init__(self, starvFile = newFile, dbName = db)
        
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
                
            #If strain is in starvation check dates
            self._c.execute("SELECT individual_id, date FROM starvation WHERE strain_id = ?", (strainId,))
            data = self._c.fetchall()
            #If not in starvation add all
            if (self._sheet.cell_value(row, 0), self._sheet.cell_value(row, 2)) not in data:
                self._c.execute('INSERT INTO starvation VALUES(?,?,?,?,?,?,?,?)', (self._sheet.cell_value(row, 0), strainId, self._sheet.cell_value(row, 2), self._sheet.cell_value(row, 3), self._sheet.cell_value(row, 4), self._sheet.cell_value(row, 5), self._sheet.cell_value(row, 6), self._sheet.cell_value(row, 7)))
                print("Adding " + currStrain)
            else:
                print(currStrain + " not added")

        self.closeCursor()
        print('Done!')

