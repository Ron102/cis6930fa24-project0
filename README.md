
  

# cis6930fa24 -- Project 0 --

  

**Name: Ronit Bali**

  

# Assignment Description

  

This is my project 0 submission. My python package extracts data from Norman Police Report Website as a pdf, creates a sqlite database and table, adds the pdf contents to the database table and finally outputs the "Nature" field along with their individual frequencies (how many times each Nature occurs). The website contains three types of summaries **arrests, incidents and case summaries**. We only have to collect the **incidents** pdf. 


  
  

# How to install

If the package is locally stored on the system, then it can be installed directly by specifying the path

  

    pipenv install /path

  

To install the package in editable mode to make changes which are immediately reflected without reinstalling, use -e before the file path

  

    pipenv install -e /path

  

## How to run

  
In the Python package, the user can run the file by passing a url in the command line following the command:

```
pipenv run python project0/main.py --incidents <url>
```
To run the pytest file (test_main.py) run the following command

```
pipenv run python -m pytest
```

Video tutorial:
[cis6930fa24_project0_ronitbali.webm](https://uflorida-my.sharepoint.com/:v:/g/personal/ronitbali_ufl_edu/EezW1WR0039DpDF3HGiN6tYBzb4aFco-NciQhG5YuGaiyQ?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=2IYUpU)

Where *project0* is the directory and *main.py* is the main python file to be executed.


  

## Functions

  
  

#### main.py

  

*main(url)* - This function takes the pdf url as an argument parsed in the command line, and  calls other functions in the program. 

  

*fetchincidents(url)* - This function uses urllib.request to request for the pdf provided by the url, and downloads the pdf as "downloaded_file.pdf". 

  

*extractincidents(pdf_path)* - This function takes the path of the downloaded pdf and uses pypdf to extract all relevent pdf data and return it as a list of strings. The first few lines which are not part of the incident table are removed, along with the last line which is not relevant.



*createdb()* - This function creates a sqlite database in the *resources* directory and creates a table called **incidents** with the following columns:

```
incident_time

incident_number

incident_location

nature

incident_ori
```

 if the table already exists, it deletes the table and creates a fresh table. 

  
*populatedb(db_path, incidents)* - This function uses regex (Regular Expression) to extract    the table field data as required and inserts it into the **incidents** table. 

*status(db_path)* - This function prints all *Natures* along with the number of times they have occurred in the table. The list is sorted alphabetically and case sensitively by the nature, and each field of the row is separated by the pipe character (|).

For example, an output could be of the type:
```
Abdominal Pains/Problems|2
Alarm|14
Animal at Large|2
Animal Complaint|2
Animal Inured|1
Animal Vicious|1
Assult EMS Needed|2
```

#### test_main.py

  

*test_fetchincidents(mocker)* - This function tests mocks the urlopen method in the *fetchincidents()* function to simulate the downloading of the pdf, and checks if it was successfully created.

  

*test_extractincidents(mock_pdf_reader)* - This function uses MagicMock to create a mock pdf page and checks if the extracted result from the *extractincidents()* function matches the mock result. 

  

*test_createdb()* - This function tests if the database file is created in path and whether a table named *incidents* is created inside the database.

  

*test_field_offices()* - This function tests whether the *field offices* field is successfully extracted and matches the mock output mentioned.

  

*test_populatedb()* - This function calls the *populatedb()* function and checks if data is correctly inserted in the table by inserting sample incidents in the table and checking if they are correct.

*test_status()* - This function calls the *populatedb()* function to fill the table with sample incidents and checks if they are printed in the correct format **(Nature|frequency)**
  

## Bugs and Assumptions

  

Some bugs and assumptions can be encountered/should be kept in mind while executing the program:

  

1) The location of the downloaded pdf file along with the database have to be kept in mind while running the program. The pdf file is downloaded in the *project0* directory and is named as **downloaded_file.pdf**, whereas the database is created in the *resources* directory and is named is as **normanpd.db**

2) The output of the *status()* function can vary depending upon the pdf passed. Some "Nature" values were of a different format as specified in the function, so the output can differ. 

3) All required libraries and packages should be installed with correct versions to avoid runtime errors.