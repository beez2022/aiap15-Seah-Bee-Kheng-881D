### Name: Seah Bee Kheng
### Email Address: bkseah2000@yahoo.com

### Folder Structure:
src:
- clean_data.py contains CruiseData class for data cleaning and feature engineering
- config.yml - allows configuration of features to be included and algorithm to use in the ML pipeline
- ml_train_predict.py - fitting/training of models, predict and report on predictions
- run_algo.py - called by run.sh and in turns run clean_data.py and ml_train_predict.py


### executing
- ./run.sh -c src/config.yaml -d ./data
- -c - config file full path, -d path to where cruise_pre & cruise_post reside
- modify algorithm and features to be used in the fitting through the config file
- 3 algorithms are supported "logisitcregression", "decisiontree", "svm"
- Can modify from existing list of features. Supported features are in listed in the original config.yaml
- run.sh calls run_algo.py - specifying config.yaml and path of database. by default config.yaml in src is used, path to db is in data directory
- run_algo.py calls clean_data.py and does the following:
    - connects to cruise_post and cruise_pre
    - remove duplicated Ext_Intcode rows
    - handles null and invalid values (e.g. year of birth in the 18xx, Cruise Distance negative and change to km)
    - feature engineering - determine age from DOB, normalize distance, bin ages, set categorical columns to numeric
- run_algo.py calls ml_train_predict.py and does the following:
    - 


### EDA Summary:
- Handling of Duplicate values - remove rows with duplicated Ext_Intcode that have more null values. retain the one with least null values
- Handling of erroneous data - e.g. cruise names mis-spellings, remove DOB that are invalid e.g. those with 18xx year, negative distances (change to positive)
- Standardizing of Cruise Distance to KM. Those in miles multiplied by 1.60934 and change to numeric value of distance.
- Handling of null values (some examples)
    - Null cruise names - fill null values with either Blastoise or Laprase by their ratios based on valid data
    - Null values & 0 of ordinal data (e.g. Onboard Wifi Service, Cleanliness) - assign 'N_A' or 0 - created another category instead of 5. The 0 or 'N_A' category usually means not filled in (no opinion) on this matter if null.
    - remove rows with null Gender or null DOB - as unable to fillna with anything meaningful
    - remove rows with null target column (Ticket Type) - its better not to fillna with a guess since this is our target column
- feature-engineering new columns (retain the same column names as much as possible):
    - determine age from DOB and bin ages into 5 equally spaced bins
    - distance values changed to KM and normalize with min-max scaler
    - categorize "word" categories to numeric-integer coded categories
    - Ticket Type - target column is changed to integer-coded as well 0 - Standard, 1 - Deluxe, 2 - Luxury

### Individual Column Processing
<table style="width80%">
<tr><th>Column Name</th><th>Processing</th>
<tr><td>Gender</td><td>encoded 0 - Male, 1 - Female</td>
