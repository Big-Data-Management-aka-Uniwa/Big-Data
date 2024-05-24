import json
import pandas as pd
from sklearn.cluster import KMeans
from sklearn import metrics
import matplotlib.pyplot as plt
from sklearn import datasets

class Clustering:

    PoliceKillingUS = None
    PovertyUS = None

    Joined = None

    def __init__(self):
        self.PoliceKillingUS = pd.read_csv('./datasets/ProcessedPoliceKillingUS.csv',encoding='utf-8')
        self.PoliceKillingUS = self.PoliceKillingUS[(self.PoliceKillingUS['date'] >= '2015-01-01') & (self.PoliceKillingUS['date'] <= '2016-12-31')]
        self.PovertyUS = pd.read_csv('./datasets/ProcessedPovertyUS.csv',encoding='utf-8')
        self.PovertyUS = self.PovertyUS[(self.PovertyUS['Year'] >=  2015 ) & (self.PovertyUS['Year'] < 2016 ) ]
        self.Joined = pd.merge(self.PoliceKillingUS,self.PovertyUS,left_on = 'state',right_on='Name',how='inner')
        self.Joined.to_csv('./datasets/Joined.csv')
        print(self.Joined)
    #def do_clustering(self):
       
    
if __name__ == "__main__":
    Clustering()
