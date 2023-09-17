import pandas as pd
import sqlite3
import numpy as np


class CruiseData():
    def __init__(self, path):
        conn = sqlite3.connect(path+"/cruise_pre.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        print(f"Table Name : {cursor.fetchall()}")
        self.df_pre = pd.read_sql_query('SELECT * FROM cruise_pre', conn)

        conn2 = sqlite3.connect(path+"/cruise_post.db")
        cursor2 = conn2.cursor()
        cursor2.execute("SELECT name FROM sqlite_master WHERE type='table';")
        print(f"Table Name : {cursor2.fetchall()}")
        self.df_post = pd.read_sql_query('SELECT * FROM cruise_post', conn2)


    
    def remove_cols(self):
        drop_cols = ['Source of Traffic', 'Embarkation/Disembarkation time convenient',
            'Ease of Online booking', 'Gate location', 'Logging']
        self.df_pre.drop(drop_cols, axis=1, inplace=True)
        print(drop_cols, "removed")
    

    def duplicate_handling(self):

        for df in [self.df_pre, self.df_post]:
            df['num_na']=0
            df['num_na'] = df.apply(lambda x: x.isna().sum(), axis=1)

            df_dup = df[df['Ext_Intcode'].duplicated()]
            todrop = []
            for ind, r2 in df_dup.iterrows():
                max_na = df[df['Ext_Intcode']==r2['Ext_Intcode']]['num_na'].max()
                dfx = df[(df['Ext_Intcode']==r2['Ext_Intcode']) & (df['num_na']==max_na)]
                if len(dfx) > 1:
                    todrop.append(dfx.index[0])
                else:
                    todrop.append(dfx.index[0])
        #print(dfx.index[0])
            df.drop(todrop, inplace=True)
            df.drop(['num_na'], inplace=True, axis=1)
        print("Duplicated Ext_Intcode rows removed from cruise_post and cruise_pre dataframe")

    def null_handling(self):
#
#  null and invalid values handling (df_pre)
#
        nulls_ = self.df_pre[self.df_pre['Date of Birth'].isna()].shape[0]
        self.df_pre = self.df_pre[self.df_pre['Date of Birth'].isna()==False].copy()
        print(nulls_, "rows dropped from cruise_pre dataframe - Null Date of Birth")

        nulls_ = self.df_pre[self.df_pre['Gender'].isna()].shape[0]
        self.df_pre = self.df_pre[self.df_pre['Gender'].isna()==False].copy()
        print(nulls_, "rows dropped from cruise_pre dataframe - Null Gender")

        self.df_pre['YOB'] = self.df_pre.apply(lambda x: int(x['Date of Birth'].split("/")[-1]) if "/" in x['Date of Birth']
                                 else int(x['Date of Birth'].split("-")[0]), axis=1)

        self.df_pre = self.df_pre[self.df_pre['YOB']>1920].copy()
        print(self.df_pre[self.df_pre['YOB']>1920].shape[0], "rows dropped from cruise_pre dataframe - Age > 102")

        self.df_pre.drop(['Date of Birth'], axis=1, inplace=True)

        cat_col_words = ['Onboard Wifi Service', 'Onboard Dining Service', 'Onboard Entertainment']
        cat_col_num = ['Online Check-in', 'Cabin Comfort', 'Cabin service', 'Baggage handling',
                     'Port Check-in Service', 'Onboard Service', 'Cleanliness']
        for c in cat_col_words:
            self.df_pre[c].fillna('N_A',inplace=True)
            print(c, "fill null rows with N_A")

        for c in cat_col_num:
            self.df_pre[c].fillna(0,inplace=True)
            print(c, "fill null rows with 0")

#
#  df_post
#
        nulls_2 = self.df_post[self.df_post['Ticket Type'].isna()].shape[0]
        self.df_post = self.df_post[self.df_post['Ticket Type'].isna()==False].copy()
        print(nulls_2,"rows dropped from cruise_post dataframe, null ticket type")
        self.df_post['Cruise Name'] = self.df_post.apply(lambda x: 'Blastoise' if x['Cruise Name'] in ['blastoise', 'blast0ise', 'blast'] else x['Cruise Name'], axis=1)
        self.df_post['Cruise Name'] = self.df_post.apply(lambda x: 'Lapras' if x['Cruise Name'] in ['IAPRAS', 'lapras', 'lap'] else x['Cruise Name'], axis=1)
        print("Standardized Cruise Names to Lapras and Blastoise")
#
# For Cruise Name fillna based on the ratio of the 2 cruise names
#

        nullvalues = self.df_post[self.df_post['Cruise Name'].isna()].shape[0]
#
# check the ratio of response and fillna based on this ratio
#
        valcnt = self.df_post[self.df_post['Cruise Name'].isna()==False]['Cruise Name'].value_counts().to_dict()
        nonnull_values = self.df_post[self.df_post['Cruise Name'].isna()==False].shape[0]
        valnum = {}
        newvalue=0
        for k in valcnt:
            print(valcnt[k])
            valratio = valcnt[k]/nonnull_values
            newvalue = newvalue + valratio*nullvalues
            valnum = {**valnum, **{k:newvalue}}
    
        cnt = 0
        keys_ = list(valnum.keys())
        for ind, r in self.df_post[self.df_post['Cruise Name'].isna()].iterrows():
            if cnt < valnum[keys_[0]]+1:
                self.df_post.loc[ind, 'Cruise Name']= keys_[0]
            else:
                self.df_post.loc[ind, 'Cruise Name']= keys_[1]
            cnt+=1
        
        print("Fill null values of Cruise Names accordingly based on ratios of available data")
        
        self.df_post['Entertainment'].fillna(2, inplace=True)
        self.df_post['WiFi'].fillna(2, inplace=True)
        print("Fill null values with 2 for cruise_post dataframe Entertainment and Wifi columns")

        self.df_post = self.df_post[self.df_post['Cruise Distance'].isna()==False].copy()
        print("cruise_post dataframe rows with Cruise Distance Null Values dropped")


    def merge_dataframes(self):
        self.df_merge = self.df_pre.merge(self.df_post, how='inner', on='Ext_Intcode')
        columns_int = ['Onboard Wifi Service', 'Onboard Dining Service', 'Onboard Entertainment',
                       'Online Check-in', 'Cabin Comfort', 'Cabin service', 'Baggage handling',
                       'Port Check-in Service', 'Onboard Service', 'Cleanliness', 'WiFi','Dining', 'Entertainment',
                       'Gender', 'Cruise Name', 'Ticket Type', 'age']

        for c in columns_int:
            self.df_merge[c] = self.df_merge[c].astype(np.int8)
        
        self.df_merge.drop(['index_x', 'index_y', 'Ext_Intcode', 'YOB'], axis=1, inplace=True)
        print("cruise_pre and cruise_post dataframes merged. Categorical columns changed to int8 type. Columns not need in pipeline removed")

        
        


    def feature_engineering(self):

#
# df_pre - get age from YOB & bin ages, categorize using 0-5
#

        cat_col_words = ['Onboard Wifi Service', 'Onboard Dining Service', 'Onboard Entertainment']
        catvalue=-1
        for indx, rowx in self.df_pre.iterrows():
            for c in cat_col_words:
                value = rowx[c]
                if value=='N_A':
                    catvalue = 0
                elif value=='Not at all important':
                    catvalue = 1
                elif value=='A little important':
                    catvalue = 2
                elif value=='Somewhat important':
                    catvalue = 3
                elif value=='Very important':
                    catvalue =  4
                elif value=='Extremely important':
                    catvalue = 5
                
                if catvalue != -1:
                    self.df_pre.loc[indx, c] = catvalue

        print("Cruise_pre dataframe - Changed str categorical columns ",cat_col_words," to numeric ")

# gender 0 - Male, 1 - Female
        self.df_pre['Gender'] = self.df_pre.apply(lambda x: 0 if x['Gender']=='Male' else 1, axis=1)
        print("Cruise_pre dataframe - Changed Gender column to numeric")

# get age from YOB
        self.df_pre['age'] = self.df_pre.apply(lambda x: 2023-x['YOB'], axis=1)
        self.df_pre['age'] = self.df_pre.apply(categorize_age, axis=1)
        print("cruise_post dataframe - Bin ages to 5 bins")
#
# df_post - categorize columns (Ticket & Cruise Name), standardize distance values and normalize it
#

        self.df_post['Cruise Name'] = self.df_post.apply(lambda x: 0 if x['Cruise Name']=='Blastoise' else 1, axis=1)
        print("cruise_post dataframe - Change cruise names to numeric categories")

#Ticket type 0 - Standard, 1 - Deluxe, 2 - Luxury
        self.df_post['Ticket Type'] = self.df_post.apply(ticket_num, axis=1)  
        print("cruise_post dataframe - Change ticket type numeric categories")
        
#
# Cruise Distance change to float and in KM. -ve distances change to positive
#
        self.df_post['Distance_type'] = self.df_post.apply(lambda x: x['Cruise Distance'].split(" ")[-1] 
                                 if x['Cruise Distance']!=None else x['Cruise Distance'], axis=1)
        
        self.df_post['Cruise Distance'] = self.df_post.apply(lambda x: int(x['Cruise Distance'].split(" ")[0]) if x['Cruise Distance']!=None 
                            else x['Cruise Distance'], axis=1)
        
        self.df_post['Cruise Distance'] = self.df_post.apply(lambda x: x['Cruise Distance']*-1 
                                                             if x['Cruise Distance']<0 else x['Cruise Distance'], axis=1)
        self.df_post['Cruise Distance'] = self.df_post.apply(lambda x: int(x['Cruise Distance']*1.60934) 
                                                             if x['Distance_type']=='Miles' else x['Cruise Distance'], axis=1)
        dist_stats = self.df_post['Cruise Distance'].agg(['min','max', 'mean'])
        self.df_post['Cruise Distance'] = self.df_post.apply(lambda x: (x['Cruise Distance']-dist_stats['min'])/(dist_stats['max']-dist_stats['min']), axis=1)
        self.df_post.drop('Distance_type', axis=1, inplace=True)

        print("cruise_post dataframe - standardardized Cruise Distance to KM and normalize to 0-1")
        
  

def ticket_num(row):
    if row['Ticket Type'] == 'Standard':
        return 0
    elif row['Ticket Type'] == 'Deluxe':
        return 1
    elif row['Ticket Type']=='Luxury':
        return 2

def categorize_age(r):
    if r['age'] < 25:
        return 0
    elif r['age'] < 35:
        return 1
    elif r['age'] < 45:
        return 2
    elif r['age'] < 55:
        return 3
    else:
        return 4
    