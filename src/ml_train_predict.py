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
            self.Algorithm = j['Algorithm']
            if j['Algorithm'].lower() == 'decisiontree':
                if 'class_weight' in list(j['DT_parameters'].keys()):
                    if type(j['DT_parameters']['class_weight']) == dict:
                        new_weights = {
                                       0:j['DT_parameters']['class_weight']["0"],
                                       1: j['DT_parameters']['class_weight']["1"],
                                       2: j['DT_parameters']['class_weight']["2"]
                                       }
                    
                if 'max_depth' in list(j['DT_parameters'].keys()):
                    if 'class_weight' in list(j['DT_parameters'].keys()):
                        self.algo = tree.DecisionTreeClassifier(max_depth=j['DT_parameters']['max_depth'],
                                                                class_weight=new_weights)
                    else:
                        self.algo = tree.DecisionTreeClassifier(max_depth=j['DT_parameters']['max_depth'])
                else:
                    if 'class_weight' in list(j['DT_parameters'].keys()):
                        self.algo = tree.DecisionTreeClassifier(class_weight=new_weights)
                    else:
                        self.algo = tree.DecisionTreeClassifier()

            elif j['Algorithm'].lower() == 'logisticregression':
                if 'class_weight' in list(j['LG_parameters'].keys()):
                    if type(j['LG_parameters']['class_weight']) == dict:
                        new_weights = {
                                       0:j['LG_parameters']['class_weight']["0"],
                                       1: j['LG_parameters']['class_weight']["1"],
                                       2: j['LG_parameters']['class_weight']["2"]
                                       }
                if 'solver' in list(j['LG_parameters'].keys()):
                    if 'multi_class' in list(j['LG_parameters'].keys()):
                        if 'class_weight' in list(j['LG_parameters'].keys()):
                            self.algo = LogisticRegression(solver=j['LG_parameters']['solver'], 
                                                           multi_class=j['LG_parameters']['multi_class'],
                                                           class_weight=new_weights)
                        else:
                            self.algo = LogisticRegression(solver=j['LG_parameters']['solver'], 
                                                           multi_class=j['LG_parameters']['multi_class'])
                    else:
                        self.algo = LogisticRegression(solver=j['LG_parameters']['solver'])
                else:
                    if 'multi_class' in list(j['LG_parameters'].keys()):
                        if 'class_weight' in list(j['LG_parameters'].keys()):
                            self.algo = LogisticRegression(multi_class=j['LG_parameters']['multi_class'],
                                                           class_weight=new_weights)
                        else:
                            self.algo = LogisticRegression(multi_class=j['LG_parameters']['multi_class'])
                    else:
                        if 'class_weight' in list(j['LG_parameters'].keys()):
                            self.algo = LogisticRegression(class_weight=new_weights)
                        else:
                            self.algo = LogisticRegression()   
            

            elif j['Algorithm'].lower() == 'svm':
                if 'class_weight' in list(j['SVM_parameters'].keys()):
                    if type(j['SVM_parameters']['class_weight']) == dict:
                        new_weights = {
                                       0:j['SVM_parameters']['class_weight']["0"],
                                       1: j['SVM_parameters']['class_weight']["1"],
                                       2: j['SVM_parameters']['class_weight']["2"]
                                       }
                if 'kernel' in list(j['SVM_parameters'].keys()):
                    if 'class_weight' in list(j['SVM_parameters'].keys()):
                        self.algo = svm.SVC(kernel=j['SVM_parameters']['kernel'],
                                                    class_weight=new_weights)
                    else:
                        self.algo = svm.SVC(kernel=j['SVM_parameters']['kernel'])
                else:
                    if 'class_weight' in list(j['SVM_parameters'].keys()):
                        self.algo = svm.SVC(class_weight=new_weights)
                    else:
                        self.algo = svm.SVC()

        self.split_ratio = j['split_ratio']

        self.Y = df['Ticket Type']
        self.X = df[features]
#
# reserve a random test set (10%) first before splitting . Use the rest of 90% for train & eval
#
        self.X1, self.X_test, self.Y1, self.Y_test = train_test_split(self.X, self.Y, test_size=0.1, stratify=self.Y)
        self.Y_testnp = self.Y_test.to_numpy()


    def train_test_split(self):

        self.X_train, self.X_val, self.Y_train, self.Y_val = train_test_split(self.X1, self.Y1, test_size=self.split_ratio, stratify=self.Y1)
        self.Y_valnp = self.Y_val.to_numpy()
    
    def train(self):
        self.algo = self.algo.fit(self.X_train, self.Y_train)

    def predict(self):
        self.predictions = self.algo.predict(self.X_test)
    
    def classification_report(self):
        print(classification_report(self.predictions, self.Y_testnp))
    
    def confusion_matrix(self):
        print(confusion_matrix(self.Y_testnp, self.predictions))