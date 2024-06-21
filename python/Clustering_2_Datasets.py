from os import system
import pandas as pd
from sklearn.cluster import KMeans
from sklearn import metrics
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import zscore

class Clustering:

    """
        Clustering Data 
    """
    def __init__(self):
        
        # Το αρχείο ../processed_datasets/ProcessedPoliceKillingUS.csv περιέχει τους καθαρούς αριθμούς και τα ποσοστά φόνων για τα έτη 2015 και 2016
        # Το αρχείο ../processed_datasets/ProcessedPovertyUS.csv περιέχει τους καθαρούς αριθμούς και τα ποσοστά σε φτώχια για τα έτη 2015 και 2016
        
        # Τα αρχεία με κατάληξη Avg_2015_2016 έχουν τα ποσοστά σε φτώχια και φόνων σε μέσο όρο των ετών 2015-2016
        
        # [Step 1] Load the processed datasets
        choice = 0
        while choice < 1 or choice > 7:
            system('clear')
            print("Choose the pair of datasets (Police Killing & Poverty) for clustering:")
            print("[1] 2015 in Rates")
            print("[2] 2016 in Rates")
            print("[3] 2015 in Numbers")
            print("[4] 2016 in Numbers")
            print("[5] 2015 in Logarithmic Normalization")
            print("[6] 2016 in Logarithmic Normalization")
            print("[7] 2015-2016 in Rates")
            choice = int(input("Enter your choice: "))

        if choice == 1 or choice == 3 or choice == 5:
            self.PoliceKillingUS = pd.read_csv('./processed_datasets/ProcessedPoliceKillingUS.csv', encoding='utf-8') 
            self.PoliceKillingUS = self.PoliceKillingUS[self.PoliceKillingUS['date'] == 2015] # filter for 2015 data
            self.PovertyUS = pd.read_csv('./processed_datasets/ProcessedPovertyUS.csv', encoding='utf-8')
            self.PovertyUS = self.PovertyUS[self.PovertyUS['Year'] == 2015] # filter for 2015 data
        elif choice == 2 or choice == 4 or choice == 6:
            self.PoliceKillingUS = pd.read_csv('./processed_datasets/ProcessedPoliceKillingUS.csv', encoding='utf-8') 
            self.PoliceKillingUS = self.PoliceKillingUS[self.PoliceKillingUS['date'] == 2016] # filter for 2016 data
            self.PovertyUS = pd.read_csv('./processed_datasets/ProcessedPovertyUS.csv', encoding='utf-8')
            self.PovertyUS = self.PovertyUS[self.PovertyUS['Year'] == 2016] # filter for 2016 data
        elif choice == 7:
            self.PoliceKillingUS = pd.read_csv('./datasets/PolliceKillingUS_Avg_2015_2016.csv', encoding='utf-8')
            self.PovertyUS = pd.read_csv('./datasets/PovertyUS_Avg_2015_2016.csv', encoding='utf-8')

        # [Step 2] Merge the datasets on 'state' and 'Name'
        self.Joined = pd.merge(self.PoliceKillingUS, self.PovertyUS, left_on='state', right_on='Name', how='outer')
        self.Joined.fillna(0, inplace=True)  # Replace missing values with 0
        self.Joined.loc[self.Joined['state'] == 0, 'state'] = self.Joined.loc[self.Joined['state'] == 0, 'Name']  # Replace missing state names
        self.Joined.to_csv('./Joined.csv', index=False)  # Save the joined dataset for reference

        # [Step 3] Create log-transformed columns for poverty and killings
       
        if choice == 1 or choice == 2:
            self.Joined['Log Poverty'] = self.Joined['Percent in Poverty'] # Ποσοστά σε φτώχια
            self.Joined['Log Killings'] = self.Joined['percentage']        # Ποσοστά φόνων
        elif choice == 3 or choice == 4:
            self.Joined['Log Poverty'] = self.Joined['Number in Poverty'] # Αριθμοί σε φτώχια
            self.Joined['Log Killings'] = self.Joined['count']            # Αριθμοί φόνων
        elif choice == 5 or choice == 6:
            self.Joined['Log Poverty'] = np.log1p(self.Joined['Number in Poverty']) # Αριθμοί σε φτώχια , καθαροί αριθμοί με Λογαριθμική κανονικοποίηση
            self.Joined['Log Killings'] = np.log1p(self.Joined['count'])            # Αριθμοί φόνων , καθαροί αριθμοί με Λογαριθμική κανονικοποίηση
        elif choice == 7:
            self.Joined['Log Poverty'] = self.Joined['Percent in Poverty Avg'] # Ποσοστά σε φτώχια μέσος όρος 2015-2016
            self.Joined['Log Killings'] = self.Joined['Avg Deaths in percentage'] # Ποσοστά φόνων μέσος όρος 2015-2016

        # [Step 4] Select the features for clustering
        self.X = self.Joined[['Log Poverty', 'Log Killings']]
        
        # [Step 5] Normalize the data using z-score normalization
        xV1 = zscore(self.X.iloc[:, 0])
        xV2 = zscore(self.X.iloc[:, 1])
        self.X = np.transpose(np.array([xV1, xV2]))

        # [Step 6] Determine the number of clusters
        numberOfRows, numberOfColumns = self.X.shape
        k = int(input(f"Enter the number of clusters for K-means (from 2 to {numberOfRows}): "))

        # [Step 7] Apply K-Means clustering
        kmeans = KMeans(n_clusters=k, n_init=10, random_state=42).fit(self.X)
        IDX = kmeans.labels_         # Get the labels of each cluster
        C = kmeans.cluster_centers_  # Get the cluster centers

        # [Step 8] Plotting the data points and clusters
        plt.figure(1)
        plt.scatter(self.X[:, 0], self.X[:, 1])  # Plot all data without clustering
        plt.title("Clustering Data")
        plt.show()

        # [Step 9] Plot each cluster with different colors
        colors = ['limegreen', 'yellow', 'c', 'purple']
        for i in range(k):
            plt.scatter(self.X[IDX == i, 0], self.X[IDX == i, 1], label=f'C{i+1}', alpha=0.6)

        # [Step 10] Plot the centroids
        plt.scatter(C[:, 0], C[:, 1], marker='x', color='black', s=150, linewidth=3, label="Centroids", zorder=10)
        plt.legend()
        plt.show()

        # [Step 11] Print clustering metrics
        print("\n\nSSE (Sum of Squared Errors) = %.3f" % kmeans.inertia_)
        print("Silhouette Coefficient: %0.3f" % metrics.silhouette_score(self.X, IDX))

    """
        Draw the SSE Plot
    """
    def plot_sse(self, max_clusters=10):
        # [Step 12.1] Calculate the SSE for different numbers of clusters
        sse = []
        for k in range(1, max_clusters + 1):
            kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
            kmeans.fit(self.X)
            sse.append(kmeans.inertia_)

        # [Step 12.2] Plot SSE vs. number of clusters to determine the optimal number of clusters (elbow method)
        plt.figure(figsize=(8, 6))
        plt.plot(range(1, max_clusters + 1), sse, marker='o')
        plt.xlabel('Number of Clusters')
        plt.ylabel('Sum of Squared Errors (SSE)')
        plt.title('Elbow Method For Optimal k')
        plt.show()

if __name__ == "__main__":
    clustering_instance = Clustering()

    # [Step 12] Draw the SSE Plot
    clustering_instance.plot_sse(max_clusters=10)
