import json
import pandas as pd
from sklearn import tree, svm
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report
import numpy as np


class MLPipeline():
    def __init__(self, cfgfile, df):
        f = open(cfgfile)
        x = f.read()
        j = json.loads(x)
        features = j['ML_Features'].split(",")
        features = [x.strip() for x in features]
        if 'Date of Birth' in features:
            features.remove('Date of Birth')
            features.append('age')
        for f in features:
            if f in list(df.columns) == False:
                print("Error: feature ", f, "not in dataframe")
                return
    
        if j['Algorithm'].lower() not in ['decisiontree','logisticregression','svm']:
            print("Algorithm", j['Algorithm'], "not supported")
            return
        else:
            if j['Algorithm'].lower() == 'decisiontree':
                self.algo = tree.DecisionTreeClassifier()
            elif j['Algorithm'].lower() == 'logisticregression':
                self.algo = tree.LogisiticRegression()
            elif j['Algorithm'].lower() == 'svm':
                self.algo = svm.SVC()

        self.split_ratio = j['split_ratio']
        self.Y = df['Ticket Type']
        self.X = df[features]


    def train_test_split(self):
        self.X_train, self.X_val, self.Y_train, self.Y_val = train_test_split(self.X, self.Y, stratify=Y)
        self.Y_valnp = self.Y_val.to_numpy()
    
    def train(self, X_train, Y_train):
        self.algo = self.algo.fit(X_train, Y_train)

    def predict(self, X_test):
        self.result = self.algo.predict(X_test)
    
    def classification_report(self)