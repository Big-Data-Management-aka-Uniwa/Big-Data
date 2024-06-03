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
        self.FilteredPovertyUS = self.FilteredPovertyUS[self.FilteredPovertyUS['Name'] != 'US']
        self.save_to_csv()
        self.PoliceKillingFinal2015 = self.reduce_data_of_kills(pd.DataFrame(self.FilteredPoliceKillingUS[(self.FilteredPoliceKillingUS['date'] >= '2015-01-01')& (self.FilteredPoliceKillingUS['date'] <= '2015-12-31')]))
        self.PoliceKillingFinal2016 = self.reduce_data_of_kills(pd.DataFrame(self.FilteredPoliceKillingUS[(self.FilteredPoliceKillingUS['date'] >= '2016-01-01')& (self.FilteredPoliceKillingUS['date'] <= '2016-12-31')]))
        self.PoliceKillingFinal = pd.concat([self.PoliceKillingFinal2015,self.PoliceKillingFinal2016], ignore_index=True)
        self.poverty_averages()
        self.killing_averages()
        print(self.PoliceKillingFinal)
        self.PoliceKillingFinal.to_csv('./datasets/ProcessedPoliceKillingUS.csv',index=False)
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
            # 'name': PreprocessData.most_frequent,
            'date': lambda x: PreprocessData.most_frequent(x.dt.year),
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
        
        
       
        # Reset index to make 'state' a column
        summary = summary.reset_index()

        total_kills = df.shape[0] #get x dimension
        summary['percentage'] = (summary['count'] / total_kills) * 100


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

    def poverty_averages(self):
        poverty_2015 = self.FilteredPovertyUS[self.FilteredPovertyUS['Year'] == 2015]
        poverty_2016 = self.FilteredPovertyUS[self.FilteredPovertyUS['Year'] == 2016]
        merged_data = pd.merge(poverty_2015, poverty_2016, on='ID', suffixes=('_2015', '_2016'))
        #print(merged_data)
       
        merged_data['Poverty Universe Avg'] = (merged_data['Poverty Universe_2015'] + merged_data['Poverty Universe_2016']) / 2
        merged_data['Number in Poverty Avg'] = (merged_data['Number in Poverty_2015'] + merged_data['Number in Poverty_2016']) / 2
        merged_data['Percent in Poverty Avg'] = (merged_data['Percent in Poverty_2015'] + merged_data['Percent in Poverty_2016']) / 2

        
        self.PovertyUSFinal = merged_data[['ID', 'Name_2015', 'Poverty Universe Avg', 'Number in Poverty Avg', 'Percent in Poverty Avg']]
        self.PovertyUSFinal.rename(columns={'Name_2015': 'Name'}, inplace=True)

        
        self.PovertyUSFinal.to_csv('./datasets/PovertyUS_Average_2015_2016.csv', index=False)
    def killing_averages(self):
        
        #print(kills_2015)
        merged_data = pd.merge(self.PoliceKillingFinal2015, self.PoliceKillingFinal2016, on='state', suffixes=('_2015', '_2016'), how='outer')
        print(merged_data)
        merged_data['Avg Deaths'] = (merged_data['count_2015'].fillna(0) + merged_data['count_2016'].fillna(0)) / 2
        merged_data['Avg Deaths in percentage'] = (merged_data['percentage_2015'].fillna(0) + merged_data['percentage_2016'].fillna(0)) / 2         
        #print(merged_data)
        self.PoliceKillingFinalAvg = merged_data[['state','Avg Deaths','Avg Deaths in percentage']]
        #print(self.PoliceKillingFinal)
        self.PoliceKillingFinalAvg = self.PoliceKillingFinalAvg[self.PoliceKillingFinalAvg['state'] != 'US']
        self.PoliceKillingFinalAvg.to_csv('./datasets/PolliceKillingUs_Average_2015_2016.csv', index=False)



if __name__ == "__main__":
    datasets = PreprocessData()
