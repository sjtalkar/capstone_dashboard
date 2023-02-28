import os
from collections import Counter

import pandas as pd
from dbfread import DBF


class RetrieveHimdata():
    """
    This  class retrieves data from the Himalayan dataset and has functions to process the DBF files to convert them into dataframes
    """

    def __init__(self, dbf_file_path: str = "../data/HIMDATA-2.5-Spring2022", raw_data_path: str = "../data/raw_data/",
                 read_dbf: bool = True):
        """

        :param file_path: relative path of the folder containing DBF file data
        :param file_path: relative path of the folder containing csv file data
        :param read_dbf:  Falg indicating whether to read from DBF file or csv files
        Initialization of the dataframes with the four basic datasets in the database

        """
        data_df_dict = dict()
        self.raw_data_path = raw_data_path
        self.dbf_file_path = dbf_file_path

        if read_dbf:
            for file_name in os.listdir(dbf_file_path):
                if file_name.endswith("DBF"):
                    full_filename = os.path.join(dbf_file_path, file_name)
                    dbf = DBF(full_filename)
                    data_df_dict[f"{file_name.split('.')[0]}_df"] = pd.DataFrame(iter(dbf))

            try:
                self.peaks_df = data_df_dict['peaks_df']
                self.exped_df = data_df_dict['exped_df']
                self.refer_df = data_df_dict['refer_df']
                self.members_df = data_df_dict['members_df']

            except:
                pass
        else:
            self.peaks_df = pd.read_csv(os.path.join(raw_data_path, "peaks.csv"))
            self.exped_df = pd.read_csv('../data/raw_data/exped.csv', dtype={'ROUTE4': object,
                                                                             'ASCENT3': object,
                                                                             'ASCENT4': object,
                                                                             'COMRTE': object,
                                                                             'STDRTE': object})
            self.refer_df = pd.read_csv(os.path.join(raw_data_path, "refer.csv"))

            self.members_df = pd.read_csv('../data/members.csv', dtype={'MSPEED': object,
                                                                                 'MSMTDATE2': object,
                                                                                 'MSMTDATE3': object,
                                                                                 'MO2NOTE': object,
                                                                                 'DEATHDATE': object,
                                                                                 'INJURYDATE': object,
                                                                                 'DEATHNOTE': object,
                                                                                 'MEMBERMEMO': object,
                                                                                 'NECROLOGY': object
                                                                        })

    def save_data_csv(self, df: pd.DataFrame, file_name: str, raw_data_path: str = "../data/raw_data/"):
        """
        :param df: Dataframe to save
        :param file_path: file path with file name to save dataframe to
        :return:
        """
        try:
            df.to_csv(os.path.join(raw_data_path, file_name), index=False)
        except Exception as e:
            print(f"Error saving file with exception thrown : {e}")
        return

    def get_exped_num_first_summiters(self) -> dict:
        """
            This function returns a dictionary with name of members who first summitted a peak as key and the value is the
            number of times they were first summiters

        :return: dict of first summitters and the number of times they were first summitters
        """
        df = self.peaks_df
        first_summiters_dict = Counter()
        first_summiters_df = pd.DataFrame(df['PSUMMITERS'].str.split(", ")).dropna()
        add_item = list()
        for row in first_summiters_df.iteritems():
            add_item.append(list(row[1].values))
        for item in add_item[0]:
            first_summiters_dict.update(item)
        return_dict = {}
        for name in sorted(first_summiters_dict, key=first_summiters_dict.get, reverse=True):
            return_dict[name] = first_summiters_dict[name]

        return return_dict

    def get_num_exped_on_peak(self) -> dict:
        """
        When provided with the expeditions dataframe, this function returns the dictionary of peaks and expeditions on them
        in descending order as a dict

        :param df: The expeditions dataframe
        :return: dictionary of peaks and expeditions on them in descending order as a dict
        """
        df = self.exped_df
        most_expeditions_peaks = df.groupby(['PEAKID'])['EXPID'].count().reset_index().sort_values('EXPID',
                                                                                                   ascending=False)
        return dict(zip(most_expeditions_peaks['PEAKID'], most_expeditions_peaks['EXPID']))

    def get_unique_approach_routes_for_peak(self) -> pd.DataFrame:
        """
        This function returns a dataframe with paek and unique approaches and the counts of unique approaches for the peak
        :param df: expedition dataframe with peak and approaches
        :return:
        """
        df = self.exped_df
        # List of peaks and unique approaches
        approaches_df = df.dropna(subset=['APPROACH'])[['PEAKID', 'APPROACH']].drop_duplicates()
        peak_approach_df = pd.DataFrame()
        peak_approach_df['APPROACH_ROUTES'] = approaches_df.groupby('PEAKID')['APPROACH'].apply('|'.join)
        peak_approach_df['APPROACH_ROUTES_COUNT'] = approaches_df.groupby('PEAKID')['APPROACH'].apply('count')
        peak_approach_df = peak_approach_df.reset_index().sort_values('APPROACH_ROUTES_COUNT', ascending=False)
        return peak_approach_df

    def get_countries_with_most_expeds(self, top_n: int = 40) -> pd.DataFrame:
        df = self.exped_df
        most_exped_countries_df = df.groupby(['YEAR', 'NATION']).agg(
            NUM_EXPEDITIONS=('EXPID', 'count')).sort_values(['NUM_EXPEDITIONS', 'YEAR'], ascending=False).iloc[:top_n]
        return most_exped_countries_df.sort_values('YEAR')
