from tkinter import *
from seqToDb import seqToDB
from tkinter import filedialog
from dbToOutput import *
import sqlite3

class wormGui(seqToDB):

    def __init__(self, db='worms.db'):
        self._db = sqlite3.connect("worms.db")
        root = Tk()
        root.geometry('700x200')
        root.title("Worm Database")
        self._DB = db

        # Add new sequence
        button = Button(root, text="Add new sequence", command=self.seqLoad).grid(row=2, column=0,sticky=W)
        # Add new starvation
        button = Button(root, text="Add new starvation", command=self.starveLoad).grid(row=3, column=0,sticky=W)
        # Call Plink
        #   Make ped
        #   
        button = Button(root, text="Make .PED file", command=self.makePed).grid(row=1, column=2,sticky=W)
        button = Button(root, text="Make .MAP file", command=self.makeMap).grid(row=1, column=3,sticky=W)
        button = Button(root, text="Call PLINK", command=self.callPlink).grid(row=6, column=0,sticky=W)

        root.mainloop()
        
    def addSeq(self):
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

    def addStarve(self):
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
            self._c.execute("SELECT strain_name, individual_id, date FROM starvation JOIN strain USING (strain_id) WHERE strain_id = ?", (strainId,))
            data = self._c.fetchall()
            #If not in starvation add all
            if (currStrain, self._sheet.cell_value(row, 0), self._sheet.cell_value(row, 2)) not in data and self._sheet.cell_value(row,2) is not None or "":
                self._c.execute('INSERT INTO starvation VALUES(?,?,?,?,?,?,?,?)', (self._sheet.cell_value(row, 0), strainId, self._sheet.cell_value(row, 2), self._sheet.cell_value(row, 3), self._sheet.cell_value(row, 4), self._sheet.cell_value(row, 5), self._sheet.cell_value(row, 6), self._sheet.cell_value(row, 7)))
                print("Adding " + currStrain)


        self.closeCursor()
        print('Done!')
        
    def seqLoad(self):
        fn = filedialog.askopenfilename()
        seqToDB.__init__(self, fi = fn, dbConn = self._db)
        self.addSeq()
        
    def starveLoad(self):
        fn = filedialog.askopenfilename()
        seqToDB.__init__(self, starvFile = fn,dbConn = self._db)
        self.addStarve()

    def makePed(self):
        excl = self.getExclude()
        pheno = writePheno(dbName=self._DB)
        pheno.writeOutput(exclude=excl)

    def makeMap(self):
        geno = writeGeno(dbName=self._DB)
        geno.writeOutput()

    def callPlink(self):
        self.createCursor()
        self._c.execute("plink --file strain")
        self.closeCursor()
        print('Done!')

    def getExclude(self, exclude='Data/exclude.tsv'):
        f = open(exclude, "r")
        exLi = []
        
        for line in f:
            ND = line.split("\t")
            name = ND[0]
            date = ND[1]
            exLi.append((name,date))
            
        f.close()
        return exLi
        
if __name__ == "__main__":
    wormGui()
