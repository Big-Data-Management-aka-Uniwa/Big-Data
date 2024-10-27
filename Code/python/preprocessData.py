import json
import pandas as pd

class PreprocessData:

    PoliceKillingUS = None
    PovertyUS = None
    PopulationUS = None
    USStates = None
    FilteredPopulationUS = None
    FilteredPoliceKillingUS = None
    FilteredPovertyUS = None

    PoliceKillingFinal2015 = None
    PoliceKillingFinal2016 = None
    PoliceKillingFinal = None
    PovertyUSFinal = None

    """
        Data Preprocessing 
    """
    def __init__(self):
        # [Step 1] Store the 3 datasets as DataFrame Objects 
        self.PoliceKillingUS = pd.read_csv('../datasets/PoliceKillingsUS.csv', encoding='utf-8')
        self.PovertyUS = pd.read_csv('../datasets/PovertyUS.csv', encoding='utf-8')
        self.PopulationUS = pd.read_csv('../datasets/PopulationUS_2015.csv', encoding='latin1', delimiter=';')
        
        # [Step 2] Filter the dates of PoliceKilling & PovertyUS datasets (Keep only 2015-2016 data) 
        self.filter_by_date()

        # [Step 3] Change the name of US States from full name to 2-letter name (eg. California --> CA)
        self.rename_states()
        self.FilteredPovertyUS = self.FilteredPovertyUS[self.FilteredPovertyUS['Name'] != 'US']

        # [Step 4] Calculate each US state's population in 2015
        self.calculate_population()
        
        # [Step 5] Save the Processed datasets to different .csv files
        self.save_to_csv()
        
        # [Step 6] Keep only the data of Police killing in 2015 and in 2016 
        self.PoliceKillingFinal2015 = self.reduce_data_of_kills(pd.DataFrame(self.FilteredPoliceKillingUS[(self.FilteredPoliceKillingUS['date'] >= '2015-01-01') & (self.FilteredPoliceKillingUS['date'] <= '2015-12-31')]))
        self.PoliceKillingFinal2016 = self.reduce_data_of_kills(pd.DataFrame(self.FilteredPoliceKillingUS[(self.FilteredPoliceKillingUS['date'] >= '2016-01-01') & (self.FilteredPoliceKillingUS['date'] <= '2016-12-31')]))
        
        # [Step 7] Merge the 2 Police Killing datasets 
        self.PoliceKillingFinal = pd.concat([self.PoliceKillingFinal2015, self.PoliceKillingFinal2016], ignore_index=True)
        
        # [Step 8] Calculate the Poverty Average by state (PovertyUS_Avg_2015_2016.csv) 
        self.poverty_averages()

        # [Step 9] Calculate the Killings Average by state (PoliceKillingUs_Avg_2015_2016.csv)  
        self.killing_averages()
        
        # [Step 10] Print in the console the Processed Police Killing dataset
        print(self.PoliceKillingFinal)

        # [Step 11] Store the Processed Police Killing dataset in a .csv file
        self.PoliceKillingFinal.to_csv('../processed_datasets/ProcessedPoliceKillingUS.csv', index=False)
    
    """
        Filter Dataset's Dates 
    """
    def filter_by_date(self):
        # [Step 2.1] Convert date to standard format for pandas
        self.PoliceKillingUS['date'] = pd.to_datetime(self.PoliceKillingUS['date'], format='%d/%m/%y') 
        
        # [Step 2.2] Select the range of dates that we want (period 2015-2016)
        self.FilteredPoliceKillingUS = self.PoliceKillingUS[(self.PoliceKillingUS['date'] >= '2015-01-01') & (self.PoliceKillingUS['date'] <= '2016-12-31')]

        # [Step 2.3] Select the range of years (period 2015-2016)
        self.FilteredPovertyUS = self.PovertyUS[(self.PovertyUS['Year'] >=  2015) & (self.PovertyUS['Year'] <= 2016)]
    
    """
        Change US states from full names to 2-letter names 
    """
    def rename_states(self):
        # [Step 3.1] Open US states dataset and store it to a dict
        with open('../datasets/us_states.json', 'r') as f:
            self.USStates = json.load(f)

        # [Step 3.2] Replace the full name to 2-letter name for every US state
        for name in self.PovertyUS['Name']:
            if name in self.USStates:
                self.FilteredPovertyUS['Name'] = self.FilteredPovertyUS['Name'].replace(name, self.USStates[name])
    
    """
        Calculate each US state's population 
    """
    def calculate_population(self):
        # [Step 4.1] Group by 'State' and sum 'Total_Population'
        self.FilteredPopulationUS = self.PopulationUS.groupby('State')['Total_Population'].sum()

        # [Step 4.2] Convert the Series to a DataFrame
        self.FilteredPopulationUS = self.FilteredPopulationUS.reset_index()

    """
        Save Processed Datasets to .csv  
    """
    def save_to_csv(self):
        # [Step 5.1] Save the processed datasets to .csv files
        self.FilteredPoliceKillingUS.to_csv('../processed_datasets/ProcessedPoliceKillingUS.csv')
        self.FilteredPovertyUS.to_csv('../processed_datasets/ProcessedPovertyUS.csv')
        self.FilteredPopulationUS.to_csv('../processed_datasets/ProcessedPopulationUS_2015.csv')
    
    """
        Reduce the data of kills 
    """
    def reduce_data_of_kills(self, df):
        # [Step 6.1] Groups data for every state
        grouped = df.groupby('state')  

        # [Step 6.2] Finds most frequent row for every state using most_frequent function
        summary = grouped.agg({ 
            'id': 'count', #counts the kills for this state
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

        # [Step 6.3] Rename the 'id' column to 'count'
        summary = summary.rename(columns={'id': 'count'}) 
        
        # [Step 6.4] Reset index to make 'state' a column
        summary = summary.reset_index()

        # [Step 6.5] Calculate total kills
        total_kills = df.shape[0] # get x dimension
        summary['percentage'] = (summary['count'] / total_kills) * 100
        
        return summary
    
    # [Step 6.2.1] Finds the most frequent value
    @staticmethod
    def most_frequent(series):
        return series.mode().iloc[0]


    """
        Calculate the Poverty Average by state
    """
    def poverty_averages(self):
        # [Step 8.1] Filter data for the years 2015 and 2016
        poverty_2015 = self.FilteredPovertyUS[self.FilteredPovertyUS['Year'] == 2015]
        poverty_2016 = self.FilteredPovertyUS[self.FilteredPovertyUS['Year'] == 2016]
        
        # [Step 8.2] Merge the two datasets on 'ID'
        merged_data = pd.merge(poverty_2015, poverty_2016, on='ID', suffixes=('_2015', '_2016'))
       
        # [Step 8.3] Calculate average values for the required columns
        merged_data['Poverty Universe Avg'] = (merged_data['Poverty Universe_2015'] + merged_data['Poverty Universe_2016']) / 2
        merged_data['Number in Poverty Avg'] = (merged_data['Number in Poverty_2015'] + merged_data['Number in Poverty_2016']) / 2
        merged_data['Percent in Poverty Avg'] = (merged_data['Percent in Poverty_2015'] + merged_data['Percent in Poverty_2016']) / 2

        # [Step 8.4] Select and rename the columns
        self.PovertyUSFinal = merged_data[['ID', 'Name_2015', 'Poverty Universe Avg', 'Number in Poverty Avg', 'Percent in Poverty Avg']]
        self.PovertyUSFinal.rename(columns={'Name_2015': 'Name'}, inplace=True)

        # [Step 8.5] Save the final poverty dataset to a CSV file
        self.PovertyUSFinal.to_csv('../datasets/PovertyUS_Avg_2015_2016.csv', index=False)

    """
        Calculate the Killings Average by state
    """
    def killing_averages(self):
        # [Step 9.1] Merge the datasets for 2015 and 2016 police killings
        merged_data = pd.merge(self.PoliceKillingFinal2015, self.PoliceKillingFinal2016, on='state', suffixes=('_2015', '_2016'), how='outer')
        print(merged_data)

        # [Step 9.2] Calculate average values for the required columns
        merged_data['Avg Deaths'] = (merged_data['count_2015'].fillna(0) + merged_data['count_2016'].fillna(0)) / 2
        merged_data['Avg Deaths in percentage'] = (merged_data['percentage_2015'].fillna(0) + merged_data['percentage_2016'].fillna(0)) / 2

        # [Step 9.3] Select the final columns
        self.PoliceKillingFinalAvg = merged_data[['state', 'Avg Deaths', 'Avg Deaths in percentage']]

        # [Step 9.4] Exclude data for the entire US
        self.PoliceKillingFinalAvg = self.PoliceKillingFinalAvg[self.PoliceKillingFinalAvg['state'] != 'US']

        # [Step 9.5] Save the final killings dataset to a CSV file
        self.PoliceKillingFinalAvg.to_csv('../datasets/PolliceKillingUS_Avg_2015_2016.csv', index=False)

if __name__ == "__main__":
    datasets = PreprocessData()
