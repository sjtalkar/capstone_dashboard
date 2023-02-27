import sys

sys.path.append("../..")

import numpy as np
import pandas as pd


## To get unique members, we need to group by FNAME and LNAME but the first and last names data is not very clean
# Emilio Vicente Laqunilla Alonso
# Emilio Vicente (Tente) Lagunilla Alonso
# There is also data twith numbers and unknowns as LNAME
# 10, Unknown
# 11, Unknown
# 12, Unknown

class MemberInfo():
    def __init__(self, data_path: str = '../data/raw_data/members.csv'):
        """
        In this initialization of the member data, the records are retained as per member id held by individual in each expedition.
        What this means is that there are multiple records for each individual in the members dataset.

        When it comes to counts of Leadership roles (instances when an individual assumed a leadership role) , deaths, injuries, oxygen
        used, reached high point, reached bc only, climbed solo, age at which climb was undertaken,
         we do not need the unique members counts since each instance of the injury has to be summed.

        1. For count of Gender, this has to be performed for each member
        2. For the median age per nationality as well, we do not have to extract out age per unique individual since we are interested
        in the median age per cuntry over all the ages an individual might have trekked.


        When we are normalizing the data by unique members, though, then we do need the count of unique members of each nationality


        :param data_path: Path to member data file
        """
        members_df = pd.read_csv(data_path,
                                 usecols=['EXPID', 'MEMBID', 'PEAKID', 'MYEAR', 'MSEASON', 'SEX', 'CALCAGE', 'CITIZEN',
                                          'WEATHER', 'LEADER', 'HIRED', 'DEATH', 'DEATHCLASS', 'WEATHER', 'INJURY',
                                          'MHIGHPT', 'MO2USED', 'BCONLY', 'MSOLO', 'LNAME', 'FNAME'],
                                 dtype={'LEADER': int, 'HIRED': int, 'WEATHER': int, 'INJURY': int, 'DEATH': int,
                                        'M02USED': int, 'BCONLY': int, 'MSOLO': int}).dropna(subset=['CITIZEN'])

        # We lose 67 records due to insufficent data about member names
        members_df = members_df[members_df['LNAME'] != 'Unknown'].copy()
        # If nationality is not certain, we should remove those as well. These are indicated by ?
        members_df = members_df[~(members_df['CITIZEN'].str.contains("?", regex=False))].copy()
        # In instances where there are two nationalities, use the first one
        members_df['CITIZEN'] = np.where(members_df['CITIZEN'].str.contains("/"),
                                         members_df['CITIZEN'].str.rpartition('/')[0].str.strip(),
                                         members_df['CITIZEN'].str.strip())
        # Remove misspellings
        members_df['CITIZEN'] = members_df['CITIZEN'].str.replace("Malaysi", "Malaysia").replace("?", "")

        # Remove records where age is 0, and nationality is a string of numbers and where gender is unknown
        members_df = members_df[
            (members_df['CALCAGE'] != 0) &
            (~members_df['CITIZEN'].str.contains(r"\d")) &
            (~(members_df['SEX'] == 'X'))]
        members_df['SEX'] = np.where(members_df['SEX'].str.contains("M"), 0, 1)
        members_df.rename(columns={'SEX': 'FEMALE'}, inplace=True)
        self.members_df = members_df

    def get_members_parallel_coord_data(self):
        """
        This function return a members database with member characteristics by Nationality/CITIZEN value as provided in the
        members.csv file. Not in case of ambiguity, the value provided is taken as ground truth. If multiple values are provided then the
        first option is coonsiered as ground truth.


        :return:Two dataframes, with members grouped according to countries. One dataframe has normalized values for each column
        (per member) and the other has row counts for each column
        """

        members_df = self.members_df

        unique_member_df = members_df[['CITIZEN', 'FNAME', 'LNAME', 'FEMALE']].drop_duplicates()
        # This will give count of women when grouped by CITIZEN
        # This will also give count of members when grouped by CITIZEN

        # get unique women
        gender_count_df = unique_member_df.groupby(['CITIZEN'])['FEMALE'].agg('sum').reset_index()
        # get unique members
        members_per_country_df = unique_member_df.groupby(
            ['CITIZEN'])['FEMALE'].agg('count').reset_index().rename(
            columns={'FEMALE': 'MEMBER_COUNT'})

        members_counts_df = members_df.groupby('CITIZEN').agg(
            {'CALCAGE': ('median', 'min', 'max'), 'LEADER': "sum", 'HIRED': "sum", 'WEATHER': "sum",
             'INJURY': "sum", 'DEATH': "sum", 'MO2USED': "sum", 'MHIGHPT': 'sum', 'BCONLY': 'sum',
             'MSOLO': 'sum'}).reset_index()

        # create single level column headers
        cols = []
        for lev_1, lev_2 in members_counts_df.columns:
            col_name = f"{lev_1}_{lev_2}".replace("_sum", "").rstrip("_").replace("_count", "").replace("_mean", "")
            cols.append(col_name)
        members_counts_df.columns = cols

        members_counts_df = members_counts_df.merge(
            members_per_country_df, how="inner", left_on=['CITIZEN'], right_on=['CITIZEN']
        )
        members_counts_df = members_counts_df.merge(gender_count_df, how="inner", left_on=['CITIZEN'],
                                                    right_on=['CITIZEN'])

        # Create the normalized values by dividing each of the other columns (except calculated age) by the number of unique members
        members_norm_df = members_counts_df.copy()
        col_to_normalize = [col_name for col_name in members_counts_df if
                            not col_name.startswith('CALCAGE') and col_name != 'MEMBER_COUNT' and col_name != 'CITIZEN']
        for col_name in col_to_normalize:
            members_norm_df[col_name] = np.round(members_norm_df[col_name] / members_norm_df['MEMBER_COUNT'], 2)

        return members_counts_df, members_norm_df

    def get_members_nationalities(self) -> list:
        """
        This function returns a list of member nationalities
        :return: list of memeber nationalities
        """
        return list(self.members_df['CITIZEN'].sort_values().unique())
