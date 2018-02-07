# Organism Database Manager

## Required Python3 Libraries
pandas
sqlite3
xlrd

## Update: 2-6-18
When creating map and ped files the database will only use the strains that are in the 3rd sheet of data in the phenotype spreadsheet. I have also created a general manager that uses consolse commands rather than the gui. I was unhappy with how the gui looked so decided it was easier to use the console.

The console commands are as follows:
```
Justins-MacBook-Pro-4:PY jrobles$ python3 databaseManager.py --help
Usage: databaseManager.py [OPTIONS]

Options:
-newdb, --new_db TEXT      Create a new database using a genotype TSV file. Use -name and -strv to specify name and phenotype data if needed.Name defaults to worms.db and strv defaults to spreadsheet in ./Data

-addvcf, --add_vcf TEXT    Takes the location of a directory to add vcf files

-addtsv, --add_tsv TEXT    Takes the location of a new or updated tsv file to add to DB.DB can be specified using -name

-addstrv, --add_strv TEXT  Takes the location of a new or updated Phenotype spreadsheet to add to DBDB can be specified using -name

-P, --ped TEXT             Takes the location of the Phenotype file to create ped file for PLINK. Use -name  to specify the name if needed

-M, --map                  Creates map file for PLINK. No arguments needed

-name, --db_name TEXT      Creates a custom name for db using -newdb

-strv, --db_strv TEXT      Takes the location of the phenotype data to use to create new_db

--help                     Show this message and exit.
```

## Examples
### Creating a new Database
Note: The use of name is optional but the default is "worms.db"
```
python3 databaseManager.py -newdb <location of tsv file> -name test.db -strv <location of phenotype sheet>
```

### Adding a directory of VCF files
```
python3 databaseManager.py -addvcf <location of directory containing VCF files>
```

### Adding a new tsv file
```
python3 databaseManager.py -addtsv <location of tsv file>
```

### Add new phenotype data
```
python3 databaseManager.py -addstrv <location of phenotype spreadsheet>
```

### Create ped file for PLINK (Using only strains from the 3rd sheet of the spreadsheet)
Note: This will create a directory Output in the directory of this program and write the file there
```
python3 databaseManager.py -P <location of phenotype spreadsheet>
```

### Create map file
Note: This will create a directory Output in the directory of this program and write the file there
```
python3 databaseManager.py -M
```

Please let me know if you have any questions or problems!
