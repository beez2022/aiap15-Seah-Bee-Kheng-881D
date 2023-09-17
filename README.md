### Name: Seah Bee Kheng
### Email Address: bkseah2000@yahoo.com

### Folder Structure:
run.sh
src:
- clean_data.py contains CruiseData class for data cleaning and feature engineering
- config.yml - allows configuration of features to be used in the ML pipeline, select algorithm and set parameters:
    - 3 algorithms are supported "logisitcregression", "decisiontree", "svm"
    - Features to be used in ML Pipeline may be modified from existing list of features. Supported features are in listed in the original config.yaml
    - only parameters listed in the original config.yaml can be modified.
- ml_train_predict.py - fitting/training of models, predict and report on predictions
- run_algo.py - called by run.sh and in turns run clean_data.py and ml_train_predict.py


### executing
- bash ./run.sh 
- run.sh calls run_algo.py - specifying config.yaml and path of database. by default src/config.yaml and ./data
- run_algo.py calls clean_data.py and does the following:
    - connects to cruise_post and cruise_pre and instantiates CruiseData class
    - remove duplicated Ext_Intcode rows
    - handles null and invalid values (e.g. year of birth in the 18xx, Cruise Distance negative and change to km)
    - feature engineering - determine age from DOB, normalize distance, bin ages, set categorical columns to numeric
- run_algo.py calls ml_train_predict.py and does the following:
    - Instantiate MLPipeline class and reads config.yaml as json object and assigns them as class attributes
    - create a separate test dataset from the cleaned and merged data (10%)
    - calls train_test_split to get train & eval set
    - calls predict to make inferences on the test data set
    - print confusion matrix
    - print classification report (recall, precision, f1 score)
 

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
    - distance values changed to KM and normalized with min-max scaler
    - categorize "word" categories to numeric-integer coded categories
    - Ticket Type - target column is changed to integer-coded as well 0 - Standard, 1 - Deluxe, 2 - Luxury

### Individual Column Processing
<table style="width80%">
<tr><th>Column Name</th><th>Processing</th></tr>
<tr><td>Gender</td><td>encoded 0 - Male, 1 - Female</td></tr>
<tr><td>Date of Birth</td><td>create column named age from the year in DOB</td></tr>
<tr><td>Source of Traffic</td><td>removed</td></tr>
<tr><td>Onboard Wifi Service, Onboard Dining Service, Onboard Entertainment</td><td>null or 0 - N_A, 1 - Not at all important, 2 - A little important, 3 - Somewhat important, 4 - Very important, 5 - Extremely important</td></tr>
<tr><td>Embarkatation/Disembarkation time convenient</td><td>removed</td></tr>
<tr><td>Ease of Online Booking</td><td>removed</td></tr>
<tr><td>Gate location</td><td>removed</td></tr>
<tr><td>Logging</td><td>removed</td></tr>
<tr><td>Online Check-in, Cabin Comfort, Cabin Service, Baggage Handling, Port Check-in Service, Onboard Service, Cleanliness</td><td>0 or null changed to 0, others remained(indicating N_A)</td></tr>
<tr><td>Ext_Intcode</td><td>used this column to join the 2 dataframes cruise_pre & post</td></tr>
<tr><td>Cruise Name</td><td>categorize 0 - Blastoise, 1 - Lapras</td></tr>
<tr><td>Ticket Type</td><td>This is the target column, removed from features during fitting and prediction 0 - standard, 1 - Deluxe, 2 - Luxury</td></tr>
<tr><td>Cruise Distance</td><td>standardized to KM, remove rows with null cruise distance, negative values changed to positive, scale to [0,1] by minmaxscaler</td></tr>
<tr><td>WiFi, Entertainment</td><td>null values given the value of 2 to indicate N_A</td></tr>
<tr><td>Dining</td><td>No change</td></tr>
</table>

### Choice of Models
Models chosen are:
- DecisionTreeClassifier from sklearn
- LogisticRegression from sklearn
- svm from sklearn
<br>In the config.yaml file, specify 'decisiontree', 'logisticregression' or 'svm' in the Algorithm key.
DecisionTreeClassifier parameters specified in DT_parameters in dictionary format
LogisticRegression parameters specified in LG_parameters in dictionary format
SVM parameters specified in SVM_parameters in dictionary format
Only those parameters listed in the config.yaml file can be changed. </br>

#### DecisionTreeClassifier
DecisionTreeClassifier is easy to understand and interpret, it offers explanability since 
we are able to plot how the ML model derives at the prediction. This may bepreferable to other black-box methods
if transparancy is important

#### SVM
SVM classifier is flexible in that a different kernel can be chosen to delineate the data, thus is able to
model non-linear decision. Since it is based on boundary points, it can handle outliers better.

#### Logistic Regression
Logistic Regression is chosen because of its popularity

### Evaluation of Models
The models are evaluated primarily on Precision & Recall by printing the classification report
This checks for certain classes that may be (consistently) misclassified as another class (low precision)
If we see many Ticket Type 0 misclassified into Ticket Type 2 - we will get low recall for Ticket Type 0
and low precision for Ticket Type 2.
To ensure accuracy levels are more realistic, we should use a separate test set from the train/eval data,
so 10% of the data is taken from the cleaned data as test set. 

### Other Deployment Considerations
- As the classification reports for all 3 models seemed too optimistic models should be tested on a new set of data before deployment
- Single predictions vs Batch Predictions
- Providing endpoint for serving model (web-api or kafka)
- More robust handling of invalid inputs
- latency and throughput
- Cloud or on-prem implementation
- Provide feedback loop for necessary re-training of model with new data


