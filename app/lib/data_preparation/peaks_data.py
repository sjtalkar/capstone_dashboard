import os
import re
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

SEASONS_DICT = {1: 'Spring', 2: 'Summer', 3: 'Autumn', 4: 'Winter'}
SEASONS_SYMBOL_DICT = {
    'Spring': 'asterisk',
    'Summer': 'circle',
    'Autumn': 'hexagon-dot',
    'Winter': 'star'

}

REGIONS_DICT = {0: 'Unclassified',
                1: 'Kangchenjunga - Janak',
                5: 'Annapurna - Damodar - Peri',
                2: 'Khumbu : Rolwaling - Makalu',
                6: 'Dhaulagiri : Mukut',
                3: 'Langtang : Jugal',
                7: 'Kanjiroba - Far West',
                4: 'Manaslu : Ganesh'}

HIMALS_DICT = {
    0: 'Unclassified',
    1: 'Annapurna',
    11: 'Kanti / Palchung',
    2: 'Api / Byas/ Risi / Guras',
    12: 'Khumbu',
    3: 'Damodar',
    13: 'Langtang',
    4: 'Dhaulagiri',
    14: 'Makalu',
    5: 'Ganesh / Shringi',
    15: 'Manaslu / Mansiri',
    6: 'Janak / Ohmi / Kangri',
    16: 'Mukut / Mustang',
    7: 'Jongsang',
    17: 'Nalakankar / Chandi / Changla',
    8: 'Jugal',
    18: 'Peri',
    9: 'Kangchenjunga / Simhalila',
    19: 'Rolwaling',
    10: 'Kanjiroba',
    20: 'Saipal'}

PEAK_STATUS_DICT = {0: 'Unknown',
                    1: 'Unclimbed',
                    2: 'Climbed'}

PEAK_HOST_DICT = {0: 'Unclassified',
                  1: 'Nepal only',
                  4: 'Nepal & China',
                  2: 'China only',
                  5: 'Nepal & India',
                  3: 'India only',
                  6: 'Nepal, China & India'}

TERM_REASON_DICT = {
    0: 'Unknown',
    1: 'Success (main peak)',
    2: 'Success (subpeak, foresummit)',
    3: 'Success (claimed)',
    4: 'Bad weather (storms, high winds)',
    5: 'Bad conditions (deep snow, avalanching, falling ice, or rock)',
    6: 'Accident (death or serious injury)',
    7: 'Illness, AMS, exhaustion, or frostbite',
    8: 'Lack (or loss) of supplies, support or equipment',
    9: 'Lack of time',
    10: 'Route technically too difficult, lack of experience, strength, or motivation',
    11: 'Did not reach base camp',
    12: 'Did not attempt climb',
    13: 'Attempt rumored',
    14: 'Other'
}


class PeakExpedition():
    def __init__(self, data_dir: str = '../data/raw_data/'):
        peak_df = pd.read_csv(os.path.join(data_dir, 'peaks.csv'),
                              usecols=['PEAKID', 'PKNAME', 'PKNAME2', 'LOCATION', 'HEIGHTM', 'REGION', 'OPEN',
                                       'PSTATUS', ])
        # Nbr of hired personnel(above BC) TOTHIRED
        exped_df = pd.read_csv(os.path.join(data_dir, 'exped.csv'),
                               usecols=['EXPID', 'PEAKID', 'YEAR', 'SEASON', 'HOST', 'SMTDAYS', 'TOTDAYS',
                                        'TERMDATE', 'TERMREASON', 'CAMPSITES', 'TOTMEMBERS', 'SMTMEMBERS', 'TOTHIRED',
                                        'SMTHIRED', 'O2USED', 'NATION', 'MDEATHS', 'HDEATHS'],
                               dtype={'O2USED': int}
                               )

        self.camp_height_pattern = re.compile(r"\d{2}/\d{2},(\d{4})m")

        exped_df['CAMP_HEIGHTS'] = exped_df['CAMPSITES'].apply(self.extract_value)
        exped_df['NUM_CAMPS'] = exped_df['CAMP_HEIGHTS'].apply(lambda this_list: len(this_list))
        exped_df['YEAR_SEASON_DATE'] = exped_df.apply(lambda row: self.set_season_date(row['YEAR'], row['SEASON']),
                                                      axis=1)

        exped_df.drop(columns=['CAMPSITES'], inplace=True)
        self.peak_exped_df = pd.merge(exped_df, peak_df, how='inner', left_on='PEAKID', right_on='PEAKID')

    def extract_value(self, text):
        """
        Define a function that takes a string and returns the value after the comma

        :param text: string in which find a certain pattern
        :return: Find all matches for the pattern defined
        """
        # Find all matches using the regular expression
        try:
            if text is None:
                return []
            else:
                matches = re.findall(self.camp_height_pattern, text)
        except:
            return []
        return matches

    def set_season_date(self, year, season):
        """
        This math is provided in Himalayan database guide
        :param year: Year of expedition
        :param season: Season of expedition
        :return: Returns the season start date
        """
        dt = datetime(year, 1, 1)
        if season == 1:
            return dt + timedelta(60)
        elif season == 2:
            summer_date = dt + timedelta(151)
            if summer_date.month == 5:
                summer_date = summer_date + timedelta(1)
            return summer_date
        elif season == 3:
            return dt + timedelta(242)
        else:
            return dt + timedelta(333)

    def set_latitude_longitude_with_peak_mapppings(self, nhpp_data_dir: str = '../data/nhpp/'):
        """
        This function combines peaks data from the himalayan dataset with the Nepal Himalaya Peak Profile organization dataset. The cleaned version of this dataset can be
         found in merged_nepal_peaks.csv
        :return:
        """

        def get_first_name(peak_name):
            return peak_name.split(" ")[0]

        nhpp_peaks = pd.read_csv(os.path.join(nhpp_data_dir, "merged_nepal_peaks.csv"),
                                 usecols=['ID', 'PEAKID', 'NAME', 'ALTERNATE_NAMES', 'LAT', 'LON', 'ELEVATION_M']).rename(
            columns={'ID': 'NHPP_PEAKID', 'PEAKID':'HIMDATA_PEAKID'})


        # now merge based on PEAKID_nhpp
        peak_expedition_nhpp = self.peak_exped_df.merge(nhpp_peaks, how='left', left_on='PEAKID',
                                                        right_on='HIMDATA_PEAKID',
                                                        suffixes=['_left', '_right']).drop(columns=['NHPP_PEAKID', 'HIMDATA_PEAKID'])

        self.peak_exped_df = peak_expedition_nhpp.dropna(subset=['LAT'])
        return

    def create_peak_aggregation(self):
        """
        To visualize the peak expedition count by year and season in a continuous fashion, we need to create a timeseries
        for each peak for every year and every season
        :return: It returns and stores(self.peak_expedition_by_year_season_df) the expeditions dataframe by year and season
        """

        df = self.peak_exped_df
        df['TERMREASON_STRING'] = df['TERMREASON'].map(TERM_REASON_DICT)

        # Aggregate expedition counts for peaks per year and season
        exped_count_df = df[df['TERMREASON_STRING'] == 'Success (main peak)'].groupby(
            ['YEAR', 'SEASON', 'YEAR_SEASON_DATE', 'PEAKID', 'PKNAME', 'LAT', 'LON', 'HEIGHTM']).agg(
            EXPEDITIONS_COUNT=('PEAKID', 'count'), MEMBER_DEATHS_COUNT=('MDEATHS', 'sum'),
            HIRED_DEATHS_COUNT=('HDEATHS', 'sum'), OXYGEN_USED_COUNT=(
                'O2USED', 'sum'), TOTMEMBERS_COUNT=('TOTMEMBERS', 'sum'),
            TOTHIRED_COUNT=('TOTHIRED', 'sum'), ).reset_index()
        exped_count_df['SEASON_STRING'] = exped_count_df['SEASON'].map(SEASONS_DICT)
        exped_count_df.drop(columns=['SEASON'], inplace=True)

        # Create dataset based quarters for all years from start to current year
        q_df = pd.DataFrame({"YEAR": list(range(exped_count_df['YEAR'].min(), exped_count_df['YEAR'].max()))})
        q_df['YEAR'] = pd.to_datetime(q_df['YEAR'].astype(str) + '-01-01')

        q_df = q_df.set_index(pd.to_datetime(q_df['YEAR']))
        q_df = q_df.resample('Q').ffill().drop(columns=(['YEAR'])).reset_index().rename(
            columns={'YEAR': 'YEAR_SEASON_DATE'})
        q_df['YEAR'] = q_df['YEAR_SEASON_DATE'].dt.year
        q_df['MONTH'] = q_df['YEAR_SEASON_DATE'].dt.month
        q_df['DAY'] = q_df['YEAR_SEASON_DATE'].dt.day

        # Align the resampled dates as per himalayan dataset season months
        # where month is 12 set date to year, 11, 30
        # where month is 09 set date to 08, 31
        # where month is 03 set date to 03, 02

        q_df['MONTH'] = np.where(q_df['MONTH'] == 9, 8, np.where(q_df['MONTH'] == 12, 11, q_df['MONTH']))
        q_df['DAY'] = np.where(q_df['MONTH'] == 3, 2,
                               np.where(q_df['MONTH'] == 11, 30,
                                        np.where(q_df['MONTH'] == 6, 1,
                                                 np.where(q_df['MONTH'] == 8, 31, q_df['DAY']))))

        q_df['YEAR_SEASON_DATE'] = pd.to_datetime(q_df[['YEAR', 'MONTH', 'DAY']])
        q_df['key'] = 0

        # Create a row for every peak for every year and every season
        primary_df = exped_count_df[['PEAKID', 'PKNAME', 'LAT', 'LON', 'HEIGHTM']].drop_duplicates().copy()
        primary_df['key'] = 0
        primary_df = primary_df[['PEAKID', 'PKNAME', 'LAT', 'LON', 'HEIGHTM', 'key']].merge(q_df, how='inner',
                                                                                            left_on=['key'],
                                                                                            right_on=['key'],
                                                                                            suffixes=(
                                                                                                '_left',
                                                                                                '_right')
                                                                                            ).sort_values(
            ['PEAKID', 'YEAR_SEASON_DATE']).drop(columns=['MONTH', 'DAY'])
        primary_df.drop(columns=['key'], inplace=True)

        # Join to aggregate data
        primary_df = primary_df.merge(exped_count_df,
                                      left_on=['YEAR', 'PEAKID', 'LAT', 'LON', 'HEIGHTM', 'YEAR_SEASON_DATE'],
                                      right_on=['YEAR', 'PEAKID', 'LAT', 'LON', 'HEIGHTM', 'YEAR_SEASON_DATE'],
                                      how='left')
        primary_df['EXPEDITIONS_COUNT'].fillna(0, inplace=True)
        primary_df['MEMBER_DEATHS_COUNT'].fillna(0, inplace=True)
        primary_df['OXYGEN_USED_COUNT'].fillna(0, inplace=True)
        primary_df['TOTMEMBERS_COUNT'].fillna(0, inplace=True)
        primary_df['TOTHIRED_COUNT'].fillna(0, inplace=True)
        primary_df['HIRED_DEATHS_COUNT'].fillna(0, inplace=True)
        # Capture percentages

        primary_df['MEMBER_DEATHS_PERC'] = np.round(
            primary_df['MEMBER_DEATHS_COUNT'] / primary_df['TOTMEMBERS_COUNT'] * 100, 2)
        primary_df['HIRED_DEATHS_PERC'] = np.round(
            primary_df['HIRED_DEATHS_COUNT'] / primary_df['TOTHIRED_COUNT'] * 100, 2)
        primary_df['OXYGEN_USED_PERC'] = np.round(
            primary_df['OXYGEN_USED_COUNT'] / primary_df['EXPEDITIONS_COUNT'] * 100, 2)

        primary_df['MEMBER_DEATHS_PERC'].fillna(0, inplace=True)
        primary_df['HIRED_DEATHS_PERC'].fillna(0, inplace=True)
        primary_df['OXYGEN_USED_PERC'].fillna(0, inplace=True)

        primary_df['SEASON_STRING'] = np.where(primary_df['YEAR_SEASON_DATE'].dt.month == 3, 'Spring',
                                               np.where(primary_df['YEAR_SEASON_DATE'].dt.month == 8, 'Autumn',
                                                        np.where(primary_df['YEAR_SEASON_DATE'].dt.month == 6, 'Summer',
                                                                 'Winter')))

        primary_df.drop(columns=['PKNAME_y'], inplace=True)
        primary_df.rename(columns={'PKNAME_x': 'PKNAME'}, inplace=True)
        self.peak_expedition_by_year_season_df = primary_df
        return primary_df

    def create_yoy_oxygen_usage_data(self):
        """
        This function returns a dataframe of year over year values for oxygen usage.
        :return:
        """

        yearly_oxygen_usage = self.peak_expedition_by_year_season_df.groupby(
            ['PEAKID', 'PKNAME', 'LAT', 'LON', 'HEIGHTM', 'YEAR']).agg(
            YEARLY_OXYGEN_USED_PERC=('OXYGEN_USED_PERC', 'sum') , EXPEDITIONS_COUNT=('EXPEDITIONS_COUNT', 'sum')).reset_index()
        yearly_oxygen_usage = yearly_oxygen_usage.set_index(['YEAR'])
        yearly_oxygen_usage["YOY_YEARLY_OXYGEN_USED_PERC"] = yearly_oxygen_usage['YEARLY_OXYGEN_USED_PERC'].pct_change(
            periods=1)
        yearly_oxygen_usage.fillna(0, inplace=True)

        #Where the previous year is 0
        yearly_oxygen_usage['YOY_YEARLY_OXYGEN_USED_PERC'] = np.where(
            yearly_oxygen_usage['YOY_YEARLY_OXYGEN_USED_PERC'] == np.inf,
            yearly_oxygen_usage['YEARLY_OXYGEN_USED_PERC'],
            yearly_oxygen_usage['YOY_YEARLY_OXYGEN_USED_PERC'])

        return yearly_oxygen_usage.reset_index()