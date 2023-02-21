import os
import re
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

HOST_DICT = {0: "Unknown",
             1: "Nepal",
             2: "China",
             3: "India"}

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
    def __init__(self, data_dir: str = '../data/raw_data/', nhpp_data_dir: str = '../data/nhpp/'):
        peak_df = pd.read_csv(os.path.join(data_dir, 'peaks.csv'),
                              usecols=['PEAKID', 'PKNAME', 'PKNAME2', 'LOCATION', 'HEIGHTM', 'REGION', 'OPEN',
                                       'PSTATUS', ])
        # Nbr of hired personnel(above BC) TOTHIRED
        exped_df = pd.read_csv(os.path.join(data_dir, 'exped.csv'),
                               usecols=['EXPID', 'PEAKID', 'YEAR', 'SEASON', 'HOST', 'SMTDAYS', 'TOTDAYS',
                                        'TERMDATE', 'TERMREASON', 'CAMPSITES', 'TOTMEMBERS', 'SMTMEMBERS', 'TOTHIRED',
                                        'SMTHIRED', 'O2USED', 'NATION', 'MDEATHS', 'HDEATHS', 'COMRTE',
                                        'ROUTE1', 'ROUTE2', 'ROUTE3', 'ROUTE4',
                                        'SUCCESS1', 'SUCCESS2', 'SUCCESS3', 'SUCCESS4',
                                        'SKI', 'PARAPENTE', 'STDRTE', 'PRIMRTE'
                                        ],
                               dtype={'O2USED': int, 'COMRTE': object, 'STDRTE': object, 'ROUTE1': object,
                                      'ROUTE2': object, 'ROUTE3': object, 'ROUTE4': object, 'SKI': int,
                                      'PARAPENTE': int,
                                      'SUCCESS1': int, 'SUCCESS2': int, 'SUCCESS3': int, 'SUCCESS4': int,
                                      }
                               )

        self.camp_height_pattern = re.compile(r"\d{2}/\d{2},(\d{4})m")
        self.camp_summit_pattern = re.compile("^.*(?=xxx|Smt)")
        self.camp_pattern = re.compile("([a-zA-Z0-9\.]+[\(][a-z0-9,\/\s]*[)],)|([A-Za-z]+[0-9]?[,]?)[\(]?")

        exped_df['CAMP_HEIGHTS'] = exped_df['CAMPSITES'].apply(self.extract_value)
        exped_df['CAMP_SITES_LIST'] = exped_df['CAMPSITES'].apply(self.extract_camps)
        exped_df['NUM_CAMPS'] = exped_df['CAMP_SITES_LIST'].apply(lambda this_list: len(this_list))

        # Expand the year and season timeframe
        exped_df['TERMREASON_STRING'] = exped_df['TERMREASON'].map(TERM_REASON_DICT)
        exped_df['YEAR_SEASON_DATE'] = exped_df.apply(lambda row: self.set_season_date(row['YEAR'], row['SEASON']),
                                                      axis=1)

        exped_df.drop(columns=['CAMPSITES'], inplace=True)
        self.peak_exped_df = pd.merge(exped_df, peak_df, how='inner', left_on='PEAKID', right_on='PEAKID')
        # Set latitude and longitude in self.peak_exped_df
        self.set_latitude_longitude_with_peak_mapppings(nhpp_data_dir)

        # Commercial peaks are far fewer, isolate all peaks with an indication of commercial versus non commercial
        self.exped_commercial_type_df = self.peak_exped_df[~self.peak_exped_df['COMRTE'].isna()].copy()
        self.exped_commercial_type_df.replace({'True': True, "False": False}, regex=False, inplace=True)
        self.exped_commercial_type_df['COMRTE'] = self.exped_commercial_type_df['COMRTE'].astype('int')

        self.get_routes_data()

    def get_routes_data(self):
        """
            This function creates a routes dataframe
        :return:
        """

        ##There are 6 expeditions where the termination is successful but none of the routes are successful
        # MARD67001        POKA73301        CHOY06315        AMAD06307        DHA112108        EVER21110

        route_df = self.peak_exped_df[[
            'EXPID', 'PEAKID', 'PKNAME', 'YEAR', 'YEAR_SEASON_DATE', 'HOST', 'LAT', 'LON', 'HEIGHTM', 'ROUTE1',
            'ROUTE2', 'ROUTE3', 'ROUTE4',
            'SUCCESS1', 'SUCCESS2', 'SUCCESS3', 'SUCCESS4', 'TERMREASON_STRING', 'SKI', 'PARAPENTE', 'COMRTE', 'STDRTE',
            'PRIMRTE', 'NUM_CAMPS']].copy()

        for col in [column for column in route_df.columns if column.startswith('ROUTE')]:
            route_df[col] = route_df[col].fillna("")
            route_df[col] = route_df[col].str.strip()

        for col in [column for column in route_df.columns if column.startswith('ROUTE')]:
            route_df[f'{col}_HIGHPOINT'] = route_df[col].apply(self.extract_values)
            route_df[col] = route_df[col].apply(self.replace_values)
        route_df['COMRTE'] = route_df['COMRTE'].fillna("Not Known")
        route_df['STDRTE'] = route_df['STDRTE'].fillna("Not Known")

        self.peak_routes_df = pd.concat([
            route_df[['PEAKID', 'PKNAME', 'YEAR', 'HOST', 'LAT', 'LON', 'HEIGHTM', 'COMRTE', 'ROUTE1', 'SUCCESS1',
                      'ROUTE1_HIGHPOINT']].rename(
                columns={'ROUTE1': 'ROUTE', 'SUCCESS1': 'ROUTE_SUCCESS', 'ROUTE1_HIGHPOINT': 'ROUTE_HIGHPOINT'}),
            route_df[['PEAKID', 'PKNAME', 'YEAR', 'HOST', 'LAT', 'LON', 'HEIGHTM', 'COMRTE', 'ROUTE2', 'SUCCESS2',
                      'ROUTE2_HIGHPOINT']].rename(
                columns={'ROUTE2': 'ROUTE', 'SUCCESS2': 'ROUTE_SUCCESS', 'ROUTE2_HIGHPOINT': 'ROUTE_HIGHPOINT'}),
            route_df[['PEAKID', 'PKNAME', 'YEAR', 'HOST', 'LAT', 'LON', 'HEIGHTM', 'COMRTE', 'ROUTE3', 'SUCCESS3',
                      'ROUTE3_HIGHPOINT']].rename(
                columns={'ROUTE3': 'ROUTE', 'SUCCESS3': 'ROUTE_SUCCESS', 'ROUTE3_HIGHPOINT': 'ROUTE_HIGHPOINT'}),
            route_df[['PEAKID', 'PKNAME', 'YEAR', 'HOST', 'LAT', 'LON', 'HEIGHTM', 'COMRTE', 'ROUTE4', 'SUCCESS4',
                      'ROUTE4_HIGHPOINT']].rename(
                columns={'ROUTE4': 'ROUTE', 'SUCCESS4': 'ROUTE_SUCCESS', 'ROUTE4_HIGHPOINT': 'ROUTE_HIGHPOINT'}),

        ], axis='rows')

        # Some cleaning
        self.peak_routes_df['ROUTE'] = self.peak_routes_df['ROUTE'].str.replace('Rigde', 'Ridge').str.replace('Genava',
                                                                                                              'Geneva').str.replace(
            " -", "-").str.replace("- ", "-").str.replace("COl", "Col")
        # Some routes are combinations of two (ascending and descending)
        self.peak_routes_df = self.peak_routes_df.assign(
            NEW_ROUTE=self.peak_routes_df['ROUTE'].str.split(',|;')).explode('NEW_ROUTE').drop(
            columns=["ROUTE"]).rename(columns={'NEW_ROUTE': 'ROUTE'})
        self.peak_routes_df['ROUTE'] = self.peak_routes_df['ROUTE'].str.strip()
        self.peak_routes_df = self.peak_routes_df[self.peak_routes_df['ROUTE'] != ""]

    def extract_values(self, text):
        """
        This function extracts values in parenthesis (to 6000m) for instance
        :param text: text string
        :return: (to 6000m) as an example if present
        """
        if pd.isna(text):
            return ""

        match = re.search(r'\(to \d+m\)', text)
        text = re.sub(r'\([^)]*\)', '', text)
        if match:
            return match.group()

        return ''

    def replace_values(self, text):
        """
             This function deletes values in parenthesis (to 6000m) for instance
             :param text: text string
             :return: deletes (to 6000m) or (as ascension)  as  examples if present
             """
        if pd.isna(text):
            return ""

        # print(text)
        return re.sub(r'\([^)]*\)', '', text.strip())

    def extract_camps(self, text):
        """
        This function extracts camps out of the camp route field. This field contains base camp to summit campsites.
        At times this is detailed with height of the camps and at other times only the type of camp such as BC, C1 or ABC is mentioned.
        :param text: camp sites text such as "BC(07/04, 5000m), Dep(13/04, 5200m), C1(19/04, 5700m), C2.ABC(21/04, 6000m),
                                                C3(23/04, 6600m), C4(25/04, 7100m), xxx(29-30/04 7600m)"
                                        string2 = "BC,C1,C2,C3,C4,Smt(23,31/05)"
                                        string3  =  "BC,C1,C2,C3,C4,Smt(11-12,21,23,31/05,01/06)"
        :return: pattern_matches : camp site strings in a list
        """

        try:
            if text is None:
                return []
            else:
                # Remove  the summit  info

                summit = re.sub(self.camp_summit_pattern, "", text)
                # print(summit)
                text = text.replace(summit, "")
                pattern_matches = re.findall(self.camp_pattern, text)
                # print(pattern_matches)
        except:
            return []
        return pattern_matches

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
         found in preprocessed_nhpp_peaks.csv
        :return:
        """

        def get_first_name(peak_name):
            return peak_name.split(" ")[0]

        nhpp_peaks = pd.read_csv(os.path.join(nhpp_data_dir, "preprocessed_nhpp_peaks.csv"),
                                 usecols=['ID', 'PEAKID', 'NAME', 'ALTERNATE_NAMES', 'LAT', 'LON',
                                          'ELEVATION_M']).rename(
            columns={'ID': 'NHPP_PEAKID', 'PEAKID': 'HIMDATA_PEAKID'})

        # now merge based on PEAKID_nhpp
        peak_expedition_nhpp = self.peak_exped_df.merge(nhpp_peaks, how='left', left_on='PEAKID',
                                                        right_on='HIMDATA_PEAKID',
                                                        suffixes=['_left', '_right']).drop(
            columns=['NHPP_PEAKID', 'HIMDATA_PEAKID'])

        self.peak_exped_df = peak_expedition_nhpp.dropna(subset=['LAT'])
        return

    def expand_timeframe_year_season(self, df):
        """
        This function expands the provided dataset with all years and seasons for every peak, between the maximum
        and minimum year range.
        :param df: The dataframe with expeditions, years and peaks for which the time series is to be created.
        :return: Dataframe with all  years and seasons filled in between minimum  and maximum
        """
        # Create dataset based quarters for all years from start to current year
        q_df = pd.DataFrame({"YEAR": list(range(df['YEAR'].min(), df['YEAR'].max()))})
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
        primary_df = df[['PEAKID', 'PKNAME', 'LAT', 'LON', 'HEIGHTM']].drop_duplicates().copy()
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
        primary_df = primary_df.merge(df,
                                      left_on=['YEAR', 'PEAKID', 'LAT', 'LON', 'HEIGHTM', 'YEAR_SEASON_DATE'],
                                      right_on=['YEAR', 'PEAKID', 'LAT', 'LON', 'HEIGHTM', 'YEAR_SEASON_DATE'],
                                      how='left')

        primary_df['SEASON_STRING'] = np.where(primary_df['YEAR_SEASON_DATE'].dt.month == 3, 'Spring',
                                               np.where(primary_df['YEAR_SEASON_DATE'].dt.month == 8, 'Autumn',
                                                        np.where(primary_df['YEAR_SEASON_DATE'].dt.month == 6, 'Summer',
                                                                 'Winter')))

        primary_df.drop(columns=['PKNAME_y'], inplace=True)
        primary_df.rename(columns={'PKNAME_x': 'PKNAME'}, inplace=True)
        return primary_df

    def expand_timeframe_year(self, df):
        """
        This function expands the provided dataset with all years for every peak, between the maximum and minimum year range.
        :param df: The dataframe with expeditions, years and peaks for which the time series is to be created.
        :return: Dataframe with all  years filled in between minimum  and maximum
        """
        # Create dataset based quarters for all years from start to current year
        y_df = pd.DataFrame({"YEAR": list(range(df['YEAR'].min(), df['YEAR'].max()))})
        y_df['key'] = 0

        # Create a row for every peak for every year and every year
        primary_df = df[['PEAKID', 'PKNAME', 'LAT', 'LON', 'HEIGHTM']].drop_duplicates().copy()
        primary_df['key'] = 0
        primary_df = primary_df[['PEAKID', 'PKNAME', 'LAT', 'LON', 'HEIGHTM', 'key']].merge(y_df, how='inner',
                                                                                            left_on=['key'],
                                                                                            right_on=['key'],
                                                                                            suffixes=(
                                                                                                '_left',
                                                                                                '_right')
                                                                                            ).sort_values(
            ['PEAKID', 'YEAR'])
        primary_df.drop(columns=['key'], inplace=True)

        # Join to aggregate data
        primary_df = primary_df.merge(df,
                                      left_on=['YEAR', 'PEAKID', 'LAT', 'LON', 'HEIGHTM'],
                                      right_on=['YEAR', 'PEAKID', 'LAT', 'LON', 'HEIGHTM'],
                                      how='left')

        primary_df.drop(columns=['PKNAME_y'], inplace=True)
        primary_df.rename(columns={'PKNAME_x': 'PKNAME'}, inplace=True)
        return primary_df

    def create_peak_aggregation(self):
        """
        To visualize the peak expedition count by year and season in a continuous fashion, we need to create a timeseries
        for each peak for every year and every season
        :return: It returns and stores(self.peak_expedition_by_year_season_df) the expeditions dataframe by year and season
        """

        df = self.peak_exped_df
        # Aggregate expedition counts for peaks per year and season, limited to expeditions that are successful
        # This should be performed before expand the dataframe to create rows for every season and year
        exped_count_df = df[df['TERMREASON_STRING'] == 'Success (main peak)'].groupby(
            ['YEAR', 'YEAR_SEASON_DATE', 'PEAKID', 'PKNAME', 'LAT', 'LON', 'HEIGHTM']
        ).agg(
            EXPEDITIONS_COUNT=('PEAKID', 'count'), MEMBER_DEATHS_COUNT=('MDEATHS', 'sum'),
            HIRED_DEATHS_COUNT=('HDEATHS', 'sum'), OXYGEN_USED_COUNT=('O2USED', 'sum'),
            TOTMEMBERS_COUNT=('TOTMEMBERS', 'sum'), TOTHIRED_COUNT=('TOTHIRED', 'sum'),
        ).reset_index()

        # Expand timeseries to all years and seasons for all peaks
        primary_df = self.expand_timeframe_year_season(exped_count_df)
        # Capture percentage aggregations

        for col_name in ['EXPEDITIONS_COUNT', 'MEMBER_DEATHS_COUNT', 'OXYGEN_USED_COUNT', 'TOTMEMBERS_COUNT',
                         'TOTHIRED_COUNT', 'HIRED_DEATHS_COUNT']:
            primary_df[col_name].fillna(0, inplace=True)

        primary_df['MEMBER_DEATHS_PERC'] = np.round(
            primary_df['MEMBER_DEATHS_COUNT'] / primary_df['TOTMEMBERS_COUNT'] * 100, 2)
        primary_df['HIRED_DEATHS_PERC'] = np.round(
            primary_df['HIRED_DEATHS_COUNT'] / primary_df['TOTHIRED_COUNT'] * 100, 2)
        primary_df['OXYGEN_USED_PERC'] = np.round(
            primary_df['OXYGEN_USED_COUNT'] / primary_df['EXPEDITIONS_COUNT'] * 100, 2)

        primary_df['MEMBER_DEATHS_PERC'].fillna(0, inplace=True)
        primary_df['HIRED_DEATHS_PERC'].fillna(0, inplace=True)
        primary_df['OXYGEN_USED_PERC'].fillna(0, inplace=True)

        self.peak_expedition_by_year_season_df = primary_df
        return primary_df

    def create_commerce_noncommerce_peak_aggregation(self, by_season: bool = True, commercial: bool = True):
        """
        To visualize the peak expedition count by year and season in a continuous fashion, we need to create a timeseries
        for each peak for every year and every season. This function is restricted to dataframe containing expeditions that have
        clear indication of whether they are commercial or non-commercial
        :param by_season: Flag for choice of aggregation by season (True) or year (False)
        :return: It returns the expeditions dataframe by year or season and a list of peaks with commercial expeditions
                 For the grouping of peak and year, get the total across all expeditions as _COUNT and the mean across
                 expeditions as _MEAN
        """

        df = self.exped_commercial_type_df
        # Expand timeseries to all years and seasons for all peaks
        # Aggregate expedition counts for peaks per year and season, limited to expeditions that are successful

        # Aggregate by year and season first
        if by_season:
            group_cols = ['YEAR', 'YEAR_SEASON_DATE', 'PEAKID', 'PKNAME', 'LAT', 'LON', 'HEIGHTM']
        else:
            group_cols = ['YEAR', 'PEAKID', 'PKNAME', 'LAT', 'LON', 'HEIGHTM']

        # For the grouping of peak and year, get the total across all expeditions as _COUNT and the mean across
        # all expeditions as _MEAN
        # This should be performed before expand the dataframe to create rows for every season and year
        exped_count_df = df.groupby(group_cols
                                    ).agg(
            EXPEDITIONS_COUNT=('PEAKID', 'count'), OXYGEN_USED_COUNT=('O2USED', 'sum'),
            COMMERCIAL_ROUTES_COUNT=('COMRTE', 'sum'),
            MEMBER_DEATHS_COUNT=('MDEATHS', 'sum'), HIRED_DEATHS_COUNT=('HDEATHS', 'sum'),
            TOTMEMBERS_COUNT=('TOTMEMBERS', 'sum'), TOTHIRED_COUNT=('TOTHIRED', 'sum'),
            TOTMEMBERS_MEAN=('TOTMEMBERS', 'mean'), TOTHIRED_MEAN=('TOTHIRED', 'mean'),
            SMTMEMBERS_COUNT=('SMTMEMBERS', 'sum'), SMTHIRED_COUNT=('SMTHIRED', 'sum'),
            SMTMEMBERS_MEAN=('SMTMEMBERS', 'mean'), SMTHIRED_MEAN=('SMTHIRED', 'mean'),
            SUMMIT_DAYS_COUNT=('SMTDAYS', 'sum'), TOTAL_DAYS_COUNT=('TOTDAYS', 'sum'),
            SUMMIT_DAYS_MEAN=('SMTDAYS', 'mean'), TOTAL_DAYS_MEAN=('TOTDAYS', 'mean'),
            NUM_CAMPS_COUNT=('NUM_CAMPS', 'sum'), NUM_CAMPS_MEAN=('NUM_CAMPS', 'mean'),
        ).reset_index()

        if by_season:
            exped_count_df = self.expand_timeframe_year_season(exped_count_df)
        else:
            exped_count_df = self.expand_timeframe_year(exped_count_df)

        for col_name in ['EXPEDITIONS_COUNT', 'MEMBER_DEATHS_COUNT', 'OXYGEN_USED_COUNT', 'TOTMEMBERS_COUNT',
                         'TOTHIRED_COUNT', 'HIRED_DEATHS_COUNT', 'COMMERCIAL_ROUTES_COUNT']:
            exped_count_df[col_name].fillna(0, inplace=True)
        # Capture percentage aggregations
        exped_count_df['MEMBER_DEATHS_PERC'] = np.round(
            exped_count_df['MEMBER_DEATHS_COUNT'] / exped_count_df['TOTMEMBERS_COUNT'] * 100, 2)
        exped_count_df['HIRED_DEATHS_PERC'] = np.round(
            exped_count_df['HIRED_DEATHS_COUNT'] / exped_count_df['TOTHIRED_COUNT'] * 100, 2)
        exped_count_df['OXYGEN_USED_PERC'] = np.round(
            exped_count_df['OXYGEN_USED_COUNT'] / exped_count_df['EXPEDITIONS_COUNT'] * 100, 2)
        exped_count_df['COMMERCIAL_ROUTES_PERC'] = np.round(
            exped_count_df['COMMERCIAL_ROUTES_COUNT'] / exped_count_df['EXPEDITIONS_COUNT'] * 100, 2)

        exped_count_df.fillna(0, inplace=True)
        for col_name in ['NUM_CAMPS_MEAN', 'SUMMIT_DAYS_MEAN']:
            exped_count_df[col_name] = np.round(exped_count_df[col_name], 2)
        # If saving in class we need two : one for season and one for year
        # Find distinct peaks with any commercial expedition
        peak_commerce_df = exped_count_df.groupby(['PEAKID', 'PKNAME']).agg(
            COMMERCIAL_EXPED_COUNT=('COMMERCIAL_ROUTES_COUNT', 'sum')).reset_index()
        peak_commerce_df = peak_commerce_df[peak_commerce_df['COMMERCIAL_EXPED_COUNT'] > 0].copy()

        return exped_count_df, list(peak_commerce_df['PKNAME'].unique())

    def create_yoy_oxygen_usage_data(self):
        """
        This function returns a dataframe of year over year values for oxygen usage.
        :return:
        """

        yearly_oxygen_usage = self.peak_expedition_by_year_season_df.groupby(
            ['PEAKID', 'PKNAME', 'LAT', 'LON', 'HEIGHTM', 'YEAR']).agg(
            YEARLY_OXYGEN_USED_PERC=('OXYGEN_USED_PERC', 'sum'),
            EXPEDITIONS_COUNT=('EXPEDITIONS_COUNT', 'sum')).reset_index()
        yearly_oxygen_usage = yearly_oxygen_usage.set_index(['YEAR'])
        yearly_oxygen_usage["YOY_YEARLY_OXYGEN_USED_PERC"] = yearly_oxygen_usage['YEARLY_OXYGEN_USED_PERC'].pct_change(
            periods=1)
        yearly_oxygen_usage.fillna(0, inplace=True)

        # Where the previous year is 0
        yearly_oxygen_usage['YOY_YEARLY_OXYGEN_USED_PERC'] = np.where(
            yearly_oxygen_usage['YOY_YEARLY_OXYGEN_USED_PERC'] == np.inf,
            yearly_oxygen_usage['YEARLY_OXYGEN_USED_PERC'],
            yearly_oxygen_usage['YOY_YEARLY_OXYGEN_USED_PERC'])

        return yearly_oxygen_usage.reset_index()
