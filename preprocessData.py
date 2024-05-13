import pandas as pd

class PreprocessData:

    PoliceKillingUS = None
    PovertyUS = None
    FilteredPoliceKillingUS = None
    FilteredPovertyUS = None

    PoliceKillingFinal = None
    PovertyUSFinal = None

    def __init__(self):
        self.PoliceKillingUS = pd.read_csv('./datasets/PoliceKillingsUS.csv',encoding='utf-8')
        self.PovertyUS = pd.read_csv('./datasets/PovertyUS.csv',encoding='utf-8')
        self.filter_by_date() 
        self.save_to_csv()
        self.deaths_to_percentage()
  
        
    def filter_by_date(self):

        #Filter PoliceKilling Dataset
        # Convert date to standard format for pandas
        self.PoliceKillingUS['date'] = pd.to_datetime(self.PoliceKillingUS['date'], format='%d/%m/%y') 
        # Select the range of dates that we want (period 2015-2016)
        self.FilteredPoliceKillingUS = self.PoliceKillingUS[(self.PoliceKillingUS['date'] >= '2015-01-01') & (self.PoliceKillingUS['date'] <= '2016-12-31')]
        print(self.FilteredPoliceKillingUS)

        #Filter Poverty Dataset
        #Select the range of years (period 2015-2016)
        self.FilteredPovertyUS = self.PovertyUS[(self.PovertyUS['Year'] >=  2015 ) & (self.PovertyUS['Year'] <= 2016 ) ]
        print(self.FilteredPovertyUS)

    def save_to_csv(self):
        self.FilteredPoliceKillingUS.to_csv('./datasets/ProcessedPoliceKillingUS.csv')
        self.FilteredPovertyUS.to_csv('./datasets/ProcessedPovertyUS.csv')
    
    def deaths_to_percentage(self):
        df = pd.DataFrame(self.FilteredPoliceKillingUS[(self.FilteredPoliceKillingUS['date'] >= '2015-01-01')& (self.FilteredPoliceKillingUS['date'] <= '2015-12-31')])
        self.deaths_2015 = len(df['id'])
        self.state_counts_2015 = df.groupby('state').size()
        #print(self.deaths_2015)
        print(self.state_counts_2015)
        df = pd.DataFrame(self.FilteredPoliceKillingUS[(self.FilteredPoliceKillingUS['date'] >= '2016-01-01')& (self.FilteredPoliceKillingUS['date'] <= '2016-12-31')])
        self.deaths_2016 = len(df['id'])
        self.state_counts_2016 = df.groupby('state').size()
        #print(self.deaths_2016)
        print(self.state_counts_2016)

        # df = self.FilteredPoliceKillingUS
        # columns = ["ID", "Name", "Date", "Method", "Weapon", "Age", "Gender", "Race", "City", "State", "Fleeing", "Fatal"]
        # df.columns = columns
        
        #print(state_counts_2015)



if __name__ == "__main__":
    datasets = PreprocessData()
    # print(datasets.PoliceKillingUsDataset)
    # print(datasets.PovertyUs)