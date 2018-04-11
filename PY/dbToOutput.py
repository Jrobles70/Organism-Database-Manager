import sqlite3
import xlrd
import time
from math import ceil

"""
for each strain I will need:
    A list of starv times
    their whole sequence
"""

class writePheno():

    def __init__(self, starvFile = "Data/Edit_uFlx_spreadsheet.xlsx", output = 'Output/strain.ped', dbName = 'worms.db'):

        self._db = sqlite3.connect(dbName)
        self._f = open(output, "w+")
        workbook = xlrd.open_workbook(starvFile)
        self._sheet = workbook.sheet_by_index(2)

    def writeOutput(self, exclude=[]):
        """
        Creates a .ped pheno file for plink to read that has tab serpated columns that are:

        Creates a tsv pheno file for plink to read that has tab serpated columns that are:

        Strain name, Individual value, paternal ID, Maternal ID, Sex, Phenotype, Genotype
        paternal, maternal and sex are not important so are set to 0

        Time to run as of 1/30/18: 3 mis 21 secs
        """
        start = time.time()
        self._c = self._db.cursor()
        idIndex = 0

        constantString = "{}\t{}\t0\t0\t2\t{:.2f}\t{}" # formats in (strain name, id, pheno time, seqLine) later

        seqLine = ""
        survTimes = []

        strainsToUse = {}
        #  count is a Throwaway value to take care of the case of having multiple of the same strain
        # dictionary searches are very fast so this should make things quicker
        count = 0
        for row in range(1, self._sheet.nrows):
            # for each row in the spreadsheet the strain and date will be added to the dict if it is not in the dict yet
            strainName = self._sheet.cell_value(row, 1)
            date = self._sheet.cell_value(row, 2)
            if (strainName, date) not in strainsToUse.values():
                strainsToUse[str(count)] = (strainName, date)
                count += 1

        print("adding to file. This may take a few minutes....")
        
        for key in strainsToUse:
            strainName = strainsToUse[key][0]
            strainDate = strainsToUse[key][1]
            print(strainName, strainDate)
            print("Grabbing suvival times")
            self._c.execute("SELECT survival FROM starvation JOIN strain USING (strain_id) WHERE strain_name = ? and date = ?", (strainName, strainDate))
            
            first = self._c.fetchone() #list of pheno times
           
            if first is not None:
                
                survTimes = self._c.fetchall()
                survTimes.insert(0, first)
                
                #Makes sure there are pheno times for this strain
                print("Grabbing Genotype")
                self._c.execute("SELECT value FROM seq JOIN strain USING (strain_id) WHERE strain_name = ?", (strainName,))
                first = self._c.fetchone()
                
                if first is not None:
                    #Makes sure there are seq values for the strain
                    seqLi = self._c.fetchall()
                    seqLi.insert(0, first)

                    print("prepping " + strainName)
                    # TODO: CHECK TO MAKE SURE THAT THIS RUNS PROPERLY
                    seqLine = "\t".join([x[0] * 2 if x[0] != "?" else x[0][:-1] + "00" for x in seqLi])
                    print("done with prep")

                    for invidID in range(len(survTimes)):
                    # TODO: Check to make sure you dont need to exclude any strains
                        self._f.write(constantString.format(strainName, invidID + 1, survTimes[invidID][0], seqLine) + "\n")
                else:
                    # TODO: FIND OUT IF EVERY STRAIN HAS A STARVATION AND OR A GENOTYPE
                    print(strainName + " has no genotype")
            else:
                #TODO: FIND OUT IF EVERY STRAIN HAS A STARVATION AND OR A GENOTYPE
                print(strainName + " has no starvation")
        self._f.close()
        self._c.close()
        end = time.time()
        print("Done! Total time was " + str(end - start))

    def writeOutputRIL(self, exclude=[]):
        """
        Creates a .ped pheno file for plink to read that has tab serpated columns that are:

        Creates a tsv pheno file for plink to read that has tab serpated columns that are:

        Strain name, Individual value, paternal ID, Maternal ID, Sex, Phenotype, Genotype
        paternal, maternal and sex are not important so are set to 0

        Time to run as of 1/30/18: 3 mis 21 secs
        """
        print("starting RIL output")
        start = time.time()
        self._c = self._db.cursor()
        idIndex = 0

        constantString = "{}\t{}\t0\t0\t2\t{:.2f}\t{}"  # formats in (strain name, id, pheno time, seqLine) later

        seqLine = ""
        survTimes = []

        strainsToUse = {}
        #  count is a Throwaway value to take care of the case of having multiple of the same strain
        # dictionary searches are very fast so this should make things quicker
        count = 0
        for row in range(1, self._sheet.nrows):
            # for each row in the spreadsheet the strain and date will be added to the dict if it is not in the dict yet
            strainName = self._sheet.cell_value(row, 1)
            date = self._sheet.cell_value(row, 2)
            if (strainName, date) not in strainsToUse.values():
                strainsToUse[str(count)] = (strainName, date)
                count += 1

        print("adding to file. This may take a few minutes....")

        for key in strainsToUse:
            strainName = strainsToUse[key][0]
            strainDate = strainsToUse[key][1]
            print(strainName, strainDate)
            self._c.execute(
                "SELECT survival FROM starvation JOIN strain USING (strain_id) WHERE strain_name = ? and date = ?",
                (strainName, strainDate))

            first = self._c.fetchone()  # list of pheno times

            if first is not None:

                survTimes = self._c.fetchall()
                survTimes.insert(0, first)

                # Makes sure there are pheno times for this strain
                try:
                    self._c.execute("SELECT value FROM {}RIL".format(strainName))
                except sqlite3.OperationalError:
                    print("{} has no RIL data".format(strainName))
                    continue
                first = self._c.fetchone()

                if first is not None:
                    # Makes sure there are seq values for the strain
                    seqLi = self._c.fetchall()
                    seqLi.insert(0, first)

                    # TODO: CHECK TO MAKE SURE THAT THIS RUNS PROPERLY
                    seqLine = "\t".join([str(ceil(float(x[0])+1)) * 2 if '.' in x[0] else str((x[0]+1) * 2) if x[0] in '01' else x[0] * 2 for x in seqLi])

                    for invidID in range(len(survTimes)):
                        # TODO: Check to make sure you dont need to exclude any strains
                        self._f.write(
                            constantString.format(strainName, invidID + 1, survTimes[invidID][0], seqLine) + "\n")
                else:
                    # TODO: FIND OUT IF EVERY STRAIN HAS A STARVATION AND OR A GENOTYPE
                    print(strainName + " has no genotype")
            else:
                # TODO: FIND OUT IF EVERY STRAIN HAS A STARVATION AND OR A GENOTYPE
                print(strainName + " has no starvation")
        self._f.close()
        self._c.close()
        end = time.time()
        print("Done! Total time was " + str(end - start))

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

    def writeOutputRIL(self):
        self._c = self._db.cursor()
        print("Writing to file....")
        self._c.execute("SELECT position, chrom FROM A6140L100RIL")
        fileFormat = "{}\t{}\t0\t{}" # (chromosome, snpID, genetic distance, base pair pos)
        allValues = self._c.fetchall()

        for pos, chrom in allValues:
            self._g.write(fileFormat.format(chrom, chrom + "_" + pos, pos) + "\n")

        self._g.close()
        self._c.close()
        print("Done!")

