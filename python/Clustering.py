import pandas as pd
from sklearn.cluster import KMeans
from sklearn import metrics
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import zscore

class Clustering:

    def __init__(self):
        self.PoliceKillingUS = pd.read_csv('../processed_datasets/ProcessedPoliceKillingUS.csv', encoding='utf-8')
        #self.PoliceKillingUS = pd.read_csv('../processed_datasets/PolliceKillingUs_Average_2015_2016.csv', encoding='utf-8')
        #self.PoliceKillingUS = self.PoliceKillingUS[self.PoliceKillingUS['date'] == 2015]
        self.PoliceKillingUS = self.PoliceKillingUS[self.PoliceKillingUS['date'] == 2016]
        
        self.PovertyUS = pd.read_csv('../processed_datasets/ProcessedPovertyUS.csv', encoding='utf-8')
        #self.PovertyUS = pd.read_csv('../processed_datasets/PovertyUS_Average_2015_2016.csv', encoding='utf-8')
        #self.PovertyUS = self.PovertyUS[self.PovertyUS['Year'] == 2015]
        self.PovertyUS = self.PovertyUS[(self.PovertyUS['Year'] == 2016)]

        self.Joined = pd.merge(self.PoliceKillingUS, self.PovertyUS, left_on='state', right_on='Name', how='outer')
        self.Joined.fillna(0,inplace=True)
        self.Joined.loc[self.Joined['state'] == 0, 'state'] = self.Joined.loc[self.Joined['state'] == 0, 'Name']
        self.Joined.to_csv('./Joined.csv', index=False)

        #print(self.Joined)
        self.Joined['Log Poverty'] = np.log1p(self.Joined['Number in Poverty'])
        self.Joined['Log Killings'] = np.log1p(self.Joined['count'])
        self.X = self.Joined[['Log Poverty', 'Log Killings']]
        #self.X = self.Joined[['Percent in Poverty', 'percentage']]  # get the collumns that we want to correlate
        #self.X = self.Joined[['Percent in Poverty Avg', 'Avg Deaths in percentage']]  # get the collumns that we want to correlate
        # Normalization data
        xV1 = zscore(self.X.iloc[:,0])
        xV2 = zscore(self.X.iloc[:,1]) 
        self.X = np.transpose(np.array([xV1,xV2])) 

        # Ask for the number of clusters
        numberOfRows, numberOfColumns = self.X.shape
        k = int(input(f"Δώσε τον αριθμό των συστάδων για τον K-means (από 2 έως {numberOfRows}): "))

        # Apply K-Means clustering
        kmeans = KMeans(n_clusters=k, n_init=10, random_state=42).fit(self.X)
        IDX = kmeans.labels_  # Get the labels of every cluster
        C = kmeans.cluster_centers_  # Get the centers

        # Plotting the data and clusters
        plt.figure(1)
        plt.scatter(self.X[:, 0], self.X[:, 1])  # Plot all data without clustering
        plt.title("Clustering Data")
        plt.show()

        # Plot each cluster with different color
        colors = ['limegreen', 'yellow', 'c', 'purple']
        for i in range(k):
            plt.scatter(self.X[IDX == i, 0], self.X[IDX == i, 1], label=f'C{i+1}', alpha=0.6)

        # Plot the centroids
        plt.scatter(C[:, 0], C[:, 1], marker='x', color='black', s=150, linewidth=3, label="Centroids", zorder=10)
        plt.legend()
        plt.show()

        # Print metrics
        print("\n\nsse = %.3f" % kmeans.inertia_)
        print("Silhouette Coefficient: %0.3f" % metrics.silhouette_score(self.X, IDX))

    def plot_sse(self, max_clusters=10):
        sse = []

        for k in range(1, max_clusters + 1):
            kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
            kmeans.fit(self.X)
            sse.append(kmeans.inertia_)

        # Plot SSE vs. number of clusters
        plt.figure(figsize=(8, 6))
        plt.plot(range(1, max_clusters + 1), sse, marker='o')
        plt.xlabel('Number of Clusters')
        plt.ylabel('Sum of Squared Errors (SSE)')
        plt.title('Elbow Method For Optimal k')
        plt.show()

if __name__ == "__main__":
    clustering_instance = Clustering()
    clustering_instance.plot_sse(max_clusters=10)
    # k = int(input("Enter the number of clusters for K-Means: "))
    # clustering_instance.do_clustering(k)
