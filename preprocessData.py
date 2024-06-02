import json
import pandas as pd

class PreprocessData:

    PoliceKillingUS = None
    PovertyUS = None
    FilteredPoliceKillingUS = None
    FilteredPovertyUS = None

    PoliceKillingFinal2015 = None
    PoliceKillingFinal2016 = None
    PoliceKillingFinal = None
    PovertyUSFinal = None
    USStates = None

    def __init__(self):
        self.PoliceKillingUS = pd.read_csv('./datasets/PoliceKillingsUS.csv',encoding='utf-8')
        self.PovertyUS = pd.read_csv('./datasets/PovertyUS.csv',encoding='utf-8')
        
        self.filter_by_date()
        self.naming_states()
        self.save_to_csv()
        self.PoliceKillingFinal2015 = self.reduce_data_of_kills(pd.DataFrame(self.FilteredPoliceKillingUS[(self.FilteredPoliceKillingUS['date'] >= '2015-01-01')& (self.FilteredPoliceKillingUS['date'] <= '2015-12-31')]))
        self.PoliceKillingFinal2016 = self.reduce_data_of_kills(pd.DataFrame(self.FilteredPoliceKillingUS[(self.FilteredPoliceKillingUS['date'] >= '2016-01-01')& (self.FilteredPoliceKillingUS['date'] <= '2016-12-31')]))
        self.PoliceKillingFinal = self.reduce_data_of_kills(pd.DataFrame(self.FilteredPoliceKillingUS[(self.FilteredPoliceKillingUS['date'] >= '2015-01-01')& (self.FilteredPoliceKillingUS['date'] <= '2016-12-31')]))
        self.PoliceKillingFinal.to_csv('./datasets/ProcessedPoliceKillingUS.csv')
        #self.PoliceKillingFinal2015.to_csv('./datasets/ProcessedPoliceKillingUS.csv')
        #self.PoliceKillingFinal2016.to_csv('./datasets/ProcessedPoliceKillingUS.csv')
        print(self.PoliceKillingFinal2015)
        print(self.PoliceKillingFinal2016)


    def filter_by_date(self):

        #Filter PoliceKilling Dataset
        # Convert date to standard format for pandas
        self.PoliceKillingUS['date'] = pd.to_datetime(self.PoliceKillingUS['date'], format='%d/%m/%y') 
        # Select the range of dates that we want (period 2015-2016)
        self.FilteredPoliceKillingUS = self.PoliceKillingUS[(self.PoliceKillingUS['date'] >= '2015-01-01') & (self.PoliceKillingUS['date'] <= '2016-12-31')]
        # print(self.FilteredPoliceKillingUS)

        #Filter Poverty Dataset
        #Select the range of years (period 2015-2016)
        self.FilteredPovertyUS = self.PovertyUS[(self.PovertyUS['Year'] >=  2015 ) & (self.PovertyUS['Year'] <= 2016 ) ]
        # print(self.FilteredPovertyUS)

    def save_to_csv(self):
        self.FilteredPoliceKillingUS.to_csv('./datasets/ProcessedPoliceKillingUS.csv')
        self.FilteredPovertyUS.to_csv('./datasets/ProcessedPovertyUS.csv')
    
    def reduce_data_of_kills(self,df):
        # df = pd.DataFrame(self.FilteredPoliceKillingUS[(self.FilteredPoliceKillingUS['date'] >= '2015-01-01')& (self.FilteredPoliceKillingUS['date'] <= '2015-12-31')])
        #print(df)
        grouped = df.groupby('state') #groups data for every state 
        #print(grouped)
        #finds most frequest row for every state using most_frequest function
        summary = grouped.agg({ 
            'id': 'count', #counts the kills for this state
            'name': PreprocessData.most_frequent,
            'date': PreprocessData.most_frequent,
            'manner_of_death': PreprocessData.most_frequent,
            'armed': PreprocessData.most_frequent,
            'age': PreprocessData.most_frequent,
            'gender': PreprocessData.most_frequent,
            'race': PreprocessData.most_frequent,
            'city': PreprocessData.most_frequent,
            'signs_of_mental_illness': PreprocessData.most_frequent,
            'threat_level': PreprocessData.most_frequent,
            'flee': PreprocessData.most_frequent,
            'body_camera': PreprocessData.most_frequent
        })

        # Rename the 'id' column to 'count'
        summary = summary.rename(columns={'id': 'count'}) 
        
        
        total_kills = df.shape[0] #get x dimension
        summary['percentage'] = (summary['count'] / total_kills) * 100

        # Reset index to make 'state' a column
        summary = summary.reset_index()

        #print(summary)
        return summary
    
    # finds the most frequent value
    @staticmethod
    def most_frequent(series):
        #print(series)
        return series.mode().iloc[0] 

    def naming_states(self):

        with open('us_states.json', 'r') as f:
            self.USStates = json.load(f)

        for name in self.PovertyUS['Name']:
            if name in self.USStates:
                self.FilteredPovertyUS['Name'] = self.FilteredPovertyUS['Name'].replace(name, self.USStates[name])


                    

                    
        



if __name__ == "__main__":
    datasets = PreprocessData()
