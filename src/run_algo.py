from clean_data import CruiseData
from ml_train_predict import MLPipeline
import sys
import argparse
parser = argparse.ArgumentParser()

if __name__ == "__main__":
    parser.add_argument("-c", "--config_file", default="src/config.yaml", required=False, help="Config file name")
    parser.add_argument("-d", "--db_path", default="./data", required=False, help="DB path")
    args = parser.parse_args()
    
#
# instantiate CruiseData and clean it
#
    cruisedata = CruiseData(args.db_path)
    cruisedata.remove_cols()
    cruisedata.duplicate_handling()
    cruisedata.null_handling()
    cruisedata.feature_engineering()
    cruisedata.merge_dataframes()

    mlpipeline = MLPipeline(args.config_file)

    print(cruisedata.df_merge.columns)