import sqlite3

"""
for each strain I will need:
    A list of starv times
    their whole sequence
"""

class writePheno():

    def __init__(self, output = 'Output/strain.ped', dbName = 'worms.db'):

        self._db = sqlite3.connect(dbName)
        self._f = open(output, "w+")

    def writeOutput(self, exclude=[]):
        """
        Creates a .ped pheno file for plink to read that has tab serpated columns that are:

        Creates a tsv pheno file for plink to read that has tab serpated columns that are:

        Strain name, Individual value, paternal ID, Maternal ID, Sex, Phenotype, Genotype
        paternal, maternal and sex are not important so are set to 0

        """
        self._c = self._db.cursor()
        idIndex = 0

        constantString = "{}\t{}\t0\t0\t2\t{:.2f}\t{}" # formats in (strain name, id, pheno time, seqLine) later

        seqLine = ""
        survTimes = []
        self._c.execute("SELECT strain_name, strain_id FROM strain") #grabs list of strains
        strainLi = self._c.fetchall() #list of strains

        self._c.execute("SELECT strain_id, date FROM starvation")
        dates = self._c.fetchall()

        print("adding to file. This may take a few minutes....")
        
        for strainName, strainID in strainLi:
            self._c.execute("SELECT date, survival FROM starvation WHERE strain_id = ?", (str(strainID),))
            
            first = self._c.fetchone() #list of pheno times
           
            if first is not None:
                
                survTimes = self._c.fetchall()
                survTimes.insert(0, first)
                
                #Makes sure there are pheno times for this strain
                self._c.execute("SELECT value FROM seq WHERE strain_id = ?", (str(strainID),))
                first = self._c.fetchone()
                
                if first is not None:
                    #Makes sure there are seq values for the strain
                    seqLi = self._c.fetchall()
                    seqLi.insert(0, first)

                    seqLine = ""
                    print("adding " + strainName)
                    for i in seqLi:
                    # Makes the whole sequence a tab seperated String

                    #i[0] is location of letter [("C")]
                    
                        if i[0] is "?":
                            seqLine += "00\t"
                        else:
                            seqLine += i[0] * 2 + "\t"
                    
                    self._c.execute("SELECT individual_id FROM starvation WHERE strain_id = ?", (str(strainID),))
                    invidID = self._c.fetchall()
                    
                    print("done with prep")
                    for date, phenoTime in survTimes:
                        if((strainName,date) not in exclude):
                            self._f.write(constantString.format(strainName, invidID[idIndex][0], phenoTime, seqLine,))
                        else:
                            print("{} {} is excluded".format(strainName, date))
                        idIndex += 1
                        self._f.write("\n")

                        if(len(invidID) - 1 is idIndex):
                            idIndex = 0

            else:
                print(strainName + " has no starvation")
            strainCount = 1    
        self._f.close()
        self._c.close()
        print("Done!")

    def grabStrains(self, inputFile):
        print("Opening")
        g = open(inputFile, "r")
        for row in g:
            self.writeOutput(row)

        g.close()

    def checkDates(self, Li, ex):
        # True if not in exclude, 
        for i in Li:
            if i in ex:
                return False
        return True

class writeGeno():

    def __init__(self, output = "Output/strain.map", dbName = 'worms.db'):

        self._db = sqlite3.connect(dbName)
        self._g = open(output, "w+")
    
    def writeOutput(self):
        self._c = self._db.cursor()
        print("Writing to file....")
        self._c.execute("SELECT position, chrom FROM seq WHERE strain_id = 2")
        fileFormat = "{}\t{}\t0\t{}" # (chromosome, snpID, genetic distance, base pair pos)
        allValues = self._c.fetchall()

        for pos, chrom in allValues:
            self._g.write(fileFormat.format(chrom, chrom + "_" + pos, pos) + "\n")

        self._g.close()
        self._c.close()
        print("Done!")
