import os
import re
import time
import requests
import concurrent.futures
import pandas as pd

from typing import TypedDict, List, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup, Comment
from dms2dec.dms_convert import dms2dec
from tqdm import tqdm

DATA_DIR = '../../data'
NHPP_DATA_DIR = os.path.join(DATA_DIR, 'nhpp')
HD_DATA_DIR = os.path.join(DATA_DIR, 'raw_data')


class PeakUrl (TypedDict):
    """ Peak table data structure """
    ID: str
    NAME: str
    URL: str


class PeakDetails(TypedDict):
    """ Peak details data structure """
    ID: str
    URL: str
    NAME: str
    ALTERNATE_NAMES: str
    LAT: float
    LON: float
    ELEVATION_M: float
    ELEVATION_FT: float
    STATUS: str
    FIRST_ASCENT_ON: str
    FIRST_ASCENT_BY: str
    DESCRIPTION: str
    PROVINCE: str
    DISTRICT: str
    MUNICIPALITY: str
    RANGE: str
    NEPALESE_FEES: str
    FOREIGNER_FEES: str


# There are few peaks from the NHPP dataset that we don't import automatically by scrapping the NHPP website
# These peaks are manually added to the dataset in the manually_collected_peaks.csv file
NHPP_PEAKS_NOT_TO_IMPORT = [
    'GIMI',  # We don't import Gimigela Chuli as it is made of 2 peaks which have separate IDs in the HD dataset
    'CHMM'   # We drop the Chamar peak as it is a duplicate of the Chamar North peak in the same dataset (2 entries for the same peak)
]

PEAKVISOR_NOT_TO_IMPORT = [
    'CHMR'  # We don't try to import this peak as it will match to the wrong one in the HD dataset
]

# There are peaks which have no matching name and id in both datasets but are identical (manually checked)
# We create this list to force the conversion. We will use the HD dataset ID if it exists and otherwise attribute it a
# new one and update the ALTERNAME_NAMES field
NHPP_PEAKS_CORRECTIONS = [
    {
        # This peak has both Latitude and Longitude set to 27º 51' 40
        "NHPP_ID": "AMAD",
        "LAT": "27.861804",
        "LON": "86.860078"
    },
    {
        # This peak has a wrong Latitude of 84º 02' 12"
        "NHPP_ID": "CHUE",
        "LAT": "28.736189",
        "LON": "84.034811"
    },
    {
        # This peak has a wrong Latitude of 86º 39' 48
        "NHPP_ID": "CHOY",
        "LAT": "28.096408",
        "LON": "86.6595"
    },
    {
        # Chaw Peak (CHAP) In the NHPP dataset is placed in a different mountain range than its neighboring peaks
        "NHPP_ID": "CHAP",
        "RANGE": "Janak"
    },
    {
        # Chaw West is reference as CHAW in the NHPP dataset but doesn't exist in the HD dataset and CHAW is used
        # for Chaw Peak in the HD dataset, so we must assign it a new and unused ID to avoid duplicate ID
        # For consistency with CHWE we modify the name the same way
        "NHPP_ID": "CHAW",
        "ID": "CHA3",
        "NAME": "Chaw Peak West",
        "PROVINCE": "Province 1"
    },
    {
        "NHPP_ID": "CHUR",
        "ALTERNATE_NAMES": "Churen Himal West"
    },
    {
        # Chaw East (CHWE) in the NHPP dataset is reference as an alternate name of Chaw Peak (which is incorrect)
        # As we match on names we must change the name of Chaw East to avoid it to be matched to Chaw Peak
        "NHPP_ID": "CHWE",
        "NAME": "Chaw Peak East"
    },
    {
        "NHPP_ID": "DZA1",
        "ALTERNATE_NAMES": "Dzanye"
    },
    {
        # This peak has a wrong Latitude of 28º 20' 44"
        "NHPP_ID": "GAN4",
        "LAT": "28.345024",
        "LON": "85.079139"
    },
    {
        # This peak has a wrong Latitude of 85º 28' 26"
        "NHPP_ID": "GHEN",
        "LAT": "28.247802",
        "LON": "85.470848"
    },
    {
        # This peak is not in the HD dataset but its ID is used by a totally different peak. Here we give it a new ID
        "NHPP_ID": "GHYM",
        "HD_ID": "GHYP"
    },
    {
        # This peak has a wrong Latitude of 82° 47'00"
        "NHPP_ID": "KAIM",
        "ALTERNATE_NAMES": "Kaipuchonam",
        "LAT": "29.726133",
        "LON": "82.780125"
    },
    {
        # This peak has a wrong Latitude of 82° 38'36"
        "NHPP_ID": "KAGM",
        "ALTERNATE_NAMES": "Kagmara I",
        "LAT": "29.137825",
        "LON": "82.758887"
    },
    {
        # This peak has both Latitude and Longitude set to 27º 44' 00"
        "NHPP_ID": "KARY",
        "LAT": "27.733585",
        "LON": "86.611572"
    },
    {
        # This peak has a wrong Latitude of 29° 16'59"
        "NHPP_ID": "KASI",
        "LAT": "29.283037",
        "LON": "82.552581"
    },
    {
        # This peak has its alternate names set has the name list preventing the matching
        # Latitude and Longitude values are also incorrect
        "NHPP_ID": "KESH",
        "ALTERNATE_NAMES": "Kesang Khang,UAAA Peak",
        "LAT": "28.921361",
        "LON": "84.000361"
    },
    {
        # This peak has a wrong Latitude of 82º 45' 41"
        "NHPP_ID": "KJRN",
        "LAT": "29.385033",
        "LON": "82.641918"
    },
    {
        "NHPP_ID": "KMJG",
        "ALTERNATE_NAMES": "Khumjung,Khamjung"
    },
    {
        "NHPP_ID": "KNCH",
        "ALTERNATE_NAMES": "Kangtsune,Kangchunne,Kanchauni Lekh,Kanchauni,Kang Chunne,Kang Chunne Peak"
    },
    {
        # This peak has a wrong Latitude of 27º 53' 21
        "NHPP_ID": "MAK1",
        "LAT": "27.890887",
        "LON": "87.08841"
    },
    {
        # This peak has a wrong Latitude of 29° 18'07"
        "NHPP_ID": "MNSL",
        "ALTERNATE_NAMES": "Manshail",
        "LAT": "29.301833",
        "LON": "83.813229"
    },
    {
        "NHPP_ID": "MUS2",
        "ALTERNATE_NAMES": "Mustang Peak"
    },
    {
        "NHPP_ID": "NALA",
        "ALTERNATE_NAMES": "Nalakankar North"
    },
    {
        "NHPP_ID": "NGOK",
        "ALTERNATE_NAMES": "Ngojumba Kang II,Ngozumpa Kang II"
    },
    {
        # Fix the latitude and longitude values to more precise values as Lunag I and Lunag II
        # are very close to each other
        "NHPP_ID": "RON1",
        "ALTERNATE_NAMES": "Lunag Ri,Lunag I",
        "LAT": "28.051424",
        "LON": "86.549701"
    },
    {
        # Fix the latitude and longitude values to more precise value
        "NHPP_ID": "RON2",
        "ALTERNATE_NAMES": "Lunag West,Little Lunag",
        "LAT": "28.05",
        "LON": "86.534866"
    }
]


def get_all_nhpp_peak_table() -> List[PeakUrl]:
    """
    Use BeautifulSoup to scrape the peak table from the website URL.
    It extracts the peak ID, NAME and URL from the table.
    :returns: a list of dictionaries containing the peak ID, NAME and URL as defined in the PeakUrl class
    """
    url = 'https://nepalhimalpeakprofile.org/peak-profile/all-peaks'
    # Make selenium headless to prevent the display of the web browser
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    # Use Selenium with the Chrome webdriver to render the page before scraping it due to the main table AJAX code
    # not rendered with a simple requests.get() call
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(3)
    # Get the page source
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "lxml")
    # Get the peak table
    peak_table = soup.find('table', attrs={"id": "mountaintable"})
    # Get the peak table rows in the table body
    peak_table_rows = peak_table.find('tbody').find_all('tr')
    all_peaks_data = []
    for row in peak_table_rows:
        # Get the table row fields in the TD tags
        row_fields = row.find_all('td')
        # Skip the Gimmigela Chuli peak as it is 2 peaks
        peak_id = row_fields[0].text.strip()
        if peak_id not in NHPP_PEAKS_NOT_TO_IMPORT:
            a_peak = {
                "ID": peak_id,
                "NAME": row_fields[1].text.replace('*', '').strip(),
                "URL": f"https://nepalhimalpeakprofile.org{row_fields[1].find('a')['href']}"
            }
            all_peaks_data.append(a_peak)
    return all_peaks_data


def get_nhpp_peak_profile(a_peak: PeakUrl) -> PeakDetails:
    """
    Use BeautifulSoup to scrape the peak profile data from the website URL. The function scraps from the peak page,
    overview data, first ascent data, description, location, fees and other information.
    :param a_peak: a dictionary containing the peak ID, NAME and URL as defined in the PeakUrl class
    :returns: a dictionary containing the peak details as defined in the PeakDetails class
    """
    # Initialise the peak details with empty values
    peak_details = {
        "ID": a_peak['ID'],
        "URL": a_peak['URL'],
        "NAME": a_peak['NAME'],
        "ALTERNATE_NAMES": None,
        "LAT": None,
        "LON": None,
        "ELEVATION_M": None,
        "ELEVATION_FT": None,
        "STATUS": None,
        "FIRST_ASCENT_ON": None,
        "FIRST_ASCENT_BY": None,
        "DESCRIPTION": None,
        "PROVINCE": None,
        "DISTRICT": None,
        "MUNICIPALITY": None,
        "RANGE": None,
        "NEPALESE_FEES": None,
        "FOREIGNER_FEES": None
    }
    # use BeautifulSoup to scrape the peak profile
    soup = BeautifulSoup(requests.get(a_peak['URL']).text, "lxml")
    # Extract all comments in the HTML page, they are used to separate the different sections of the page
    # We reuse them here to find the data in the appropriate sections
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        # If the comment contains "OVERVIEW START" we extract the overview data from the first DIV tag
        if 'OVERVIEW START' in comment:
            overview_section = comment.find_next_sibling('div')
            # Peak overview
            # get the peak overview from the overview section
            peak_overview = overview_section.find(
                'div',
                attrs={"class": "uk-child-width-1-2 uk-child-width-1-2@s uk-child-width-1-2@m uk-child-width-1-3@l "
                                "uk-child-width-1-3@xl uk-grid-medium uk-grid-match uk-grid"}
            )
            peak_overview_details = peak_overview.find_all('div', recursive=False)
            # Define the regex used to extract the various overview fields
            alternate_names_regex = r'\s*Other Name\s+(?P<alternate_names>[A-Z][\w\s,]+)'
            status_regex = r'\s*Status\s+(?P<status>[A-Z]\w+(?:\s\w+)*)\s*'
            elevation_regex = r'\s*Elevation\s+(?P<elevation_m>\d{4}(\.\d{2})?)\sM\s+/\s+(?P<elevation_ft>\d{5}(\.\d{2})?)\sFT'
            lat_regex = r'\s*Latitude\s+((?P<degree>\d{2}\s*[º°]?\s*\d{2}\s*\'?\s*\d{2}\s*[",\']*)|(?P<decimal>\d{2}\.\d{2,10}))\s+'
            lon_regex = r'\s*Longitude\s+((?P<degree>\d{2}\s*[º°]?\s*\d{2}\s*\'?\s*\d{2}\s*[",\']*)|(?P<decimal>\d{2}\.\d{2,10}))\s+'
            # for all DIV tags in the peak overview details search for the regex patterns and extract the data
            for detail in peak_overview_details:
                # Search for the various fields
                alternate_names_match = re.search(alternate_names_regex, detail.text)
                status_match = re.search(status_regex, detail.text)
                elevation_match = re.search(elevation_regex, detail.text)
                lat_match = re.search(lat_regex, detail.text)
                lon_match = re.search(lon_regex, detail.text)
                # Edit the peak details dictionary with the found data
                if alternate_names_match:
                    peak_details['ALTERNATE_NAMES'] = alternate_names_match.group('alternate_names').\
                        strip().replace(" *", '').replace("'", '').replace(", ", ',')
                elif status_match:
                    peak_details['STATUS'] = status_match.group('status')
                elif elevation_match:
                    peak_details['ELEVATION_M'] = float(elevation_match.group('elevation_m'))
                    peak_details['ELEVATION_FT'] = float(elevation_match.group('elevation_ft'))
                elif lat_match:
                    # If the latitude is found in degrees through the group 1, convert it to decimal degrees
                    if lat_match.group('degree'):
                        peak_details['LAT'] = dms2dec(lat_match.group('degree') + ' N')
                    # If the latitude is found in decimal degrees through the group 2, convert it to float
                    elif lat_match.group('decimal'):
                        peak_details['LAT'] = float(lat_match.group('decimal'))
                elif lon_match:
                    # If the longitude is found in degrees through the group 1, convert it to decimal degrees
                    if lon_match.group('degree'):
                        peak_details['LON'] = dms2dec(lon_match.group('degree') + ' E')
                    # If the longitude is found in decimal degrees through the group 2, convert it to float
                    elif lon_match.group('decimal'):
                        peak_details['LON'] = float(lon_match.group('decimal'))
            # Peak history
            # get the peak history section
            peak_history = overview_section.find(
                'div',
                attrs={"class": "uk-child-width-1-2 uk-child-width-1-2@s uk-child-width-1-2@m uk-child-width-1-2@l "
                                "uk-child-width-1-2@xl uk-grid-medium uk-grid-match uk-grid"}
            )
            # If the peak history section is found, extract the first ascent data
            try:
                peak_history_details = peak_history.find_all(
                    'div', attrs={"class": "el-content uk-panel uk-margin-small-top"})
                first_ascent_on_regex = r'(\d{2}/\d{2}/\d{4})\s+AD.*'
                first_ascent_by_regex = r'\s*([\w\s]+(?:\(\s[\w\s]+\))?),?\s'
                # The first DIV tag contains the first ascent date
                first_ascent_on = re.search(first_ascent_on_regex, peak_history_details[0].text).group(1)
                # The second DIV tag contains the list of first ascent climbers
                first_ascentionists = re.findall(first_ascent_by_regex, peak_history_details[1].text)
                first_ascent_by = ','.join([a.replace('( ', '(').replace('   )', ')') for a in first_ascentionists])
            except (AttributeError, IndexError):
                first_ascent_on = ''
                first_ascent_by = ''
            peak_details['FIRST_ASCENT_ON'] = first_ascent_on
            peak_details['FIRST_ASCENT_BY'] = first_ascent_by
        # If the comment contains "OVERVIEW END" we extract the peak description from the second DIV tag
        elif 'OVERVIEW END' in comment:
            description_section = comment.find_next_sibling('div').find_next_sibling('div')
            # get the description
            peak_description = description_section.find('div', attrs={"class": "uk-column-large"})
            # If there is no description, set it to an empty string
            try:
                peak_details['DESCRIPTION'] = peak_description.text.strip()
            except AttributeError:
                pass
        # If the comment contains "FACT START" we extract both the location facts and fees facts
        elif 'FACTS START' in comment:
            # Get the DIV tag containing the different facts
            facts_section = comment.find_next_sibling('div').find(
                'div',
                attrs={"class": "uk-child-width-1-1 uk-child-width-1-2@m uk-grid-small uk-grid uk-flex-top "
                                "uk-flex-wrap-top"}
            )
            # Get the 4 sub-sections of the facts section included in DIV tags just one layer deep
            facts_sub_sections = facts_section.find_all('div', recursive=False)
            # Location details
            # Try to get the location details otherwise continue
            try:
                # The location facts are in the first section and then 2 DIV tags and 1 UL tag deep
                location_facts = facts_sub_sections[0].find('div').find('div').find('ul')
                # Define the different location fields regex patterns
                province_regex = r'\s*Province:\s+(?P<province>[\w\s]+)'
                district_regex = r'\s*District:\s+(?P<district>[\w\s]+/?\w+)\s*'
                municipality_regex = r'\s*Municipality/Rural Municipality:\s+(?P<municipality>[\w\s]+/?\w+)\s*'
                range_regex = r'\s*Mountain Range:\s+(?P<range>[\w\s]+)'
                # For all LI tags in the location facts, extract the data using the regex patterns
                for li in location_facts.find_all('li'):
                    # Search for the various fields
                    province_match = re.search(province_regex, li.text)
                    district_match = re.search(district_regex, li.text)
                    municipality_match = re.search(municipality_regex, li.text)
                    range_match = re.search(range_regex, li.text)
                    # Edit the peak details dictionary with the found data
                    if province_match:
                        peak_details['PROVINCE'] = province_match.group('province').strip()
                    elif district_match:
                        peak_details['DISTRICT'] = district_match.group('district').strip()
                    elif municipality_match:
                        peak_details['MUNICIPALITY'] = municipality_match.group('municipality').strip()
                    elif range_match:
                        peak_details['RANGE'] = range_match.group('range').strip()
            except (AttributeError, IndexError):
                pass
            # Fees details
            # Try to get the fees facts, otherwise continue
            try:
                # The fees facts are in the third section and then 2 DIV tags and 1 UL tag deep
                fees_facts = facts_sub_sections[2].find('div').find('div').find('ul')
                # Get the Nepalese fees from the first LI tag
                nepalese_fees_regex = r'\s*Nepalese \(NRs\):\s+([\w\s]+)'
                peak_details['NEPALESE_FEES'] = re.search(
                    nepalese_fees_regex,
                    fees_facts.find_all('li')[0].text
                ).group(1).strip() + ' (NRs)'
                # Get the foreigner fees from the second LI tag
                foreigner_fees_regex = r'\s*Foreigners \(USD\):\s+([\w\s]+)'
                peak_details['FOREIGNER_FEES'] = re.search(
                    foreigner_fees_regex,
                    fees_facts.find_all('li')[1].text
                ).group(1).strip() + ' (USD)'
            except (AttributeError, IndexError):
                pass
        # Passed the FACT END comment, we can break the loop, we don't need anymore data
        elif 'FACTS END' in comment:
            break
    # Search in the NHPP_PEAKS_CORRECTIONS list of dictionaries for an entry with maching NHPP_ID
    # If there is a match, we need to convert the peak ID and overwrite any correction
    peak_corrections = next((item for item in NHPP_PEAKS_CORRECTIONS if item['NHPP_ID'] == a_peak['ID']), None)
    if peak_corrections:
        # If the HD_ID key is present in the corrections dictionary keys, we need to overwrite the peak ID
        if 'HD_ID' in peak_corrections.keys():
            peak_details['ID'] = peak_corrections['HD_ID']
        # Correct any non ID values in peak_corrections
        for key, value in peak_corrections.items():
            if key != 'NHPP_ID' and key != 'HD_ID':
                peak_details[key] = value
    return peak_details


def get_data_from_peakvisor(peak_names: List[str]) -> Tuple[str, str, str, str]:
    """
    Get the latitude, longitude, district and about text of a peak from the PeakVisor website
    :param peak_names: The list of possible names for the peak
    :return: The latitude, longitude, district and about of the peak
    """
    lat, lon, district, about = None, None, None, None
    # If there is a name which includes "peak" in the peak_names add a possible name without peak
    # Also add for all peaks without "peak" the name with "peak"
    # Also add for all peaks without "peak" the name with prefix "mount"
    peak_names = peak_names + [p.replace('peak', '').strip() for p in peak_names if 'peak' in p.lower()]
    peak_names = peak_names + [p + ' peak' for p in peak_names if 'peak' not in p.lower()]
    peak_names = peak_names + ['mount ' + p for p in peak_names if 'peak' not in p.lower()]
    # For all the possible names of the peak, try to access the peak page
    page_found = False
    for peak_name in peak_names:
        # Get the peak_page
        peak_url = f'https://peakvisor.com/peak/{peak_name.lower().replace(" ", "-")}.html'
        peak_page = requests.get(peak_url)
        # If the peak_page is not found, continue
        if peak_page.status_code == 404:
            continue
        # If the peak_page is found, break the loop
        else:
            # Make sure the peak_page we found is for a peak in Nepal
            # use BeautifulSoup to scrape the peak profile
            soup = BeautifulSoup(peak_page.text, "lxml")
            # Check that we are looking at a peak in Nepal
            nepal_peak = False
            try:
                # Get all countries in the location section
                countries_section = soup.find_all('div', attrs={"class": "sidebar__hs-country"})
                # For all countries, check if the first element is Nepal and if it is get the disctrict from
                # the last element
                for country in countries_section:
                    country_detail_section = country.find('div', attrs={"class": "sidebar__hs-chip-content"})
                    country_details = country_detail_section.find_all('li')
                    if country_details[0].text == 'Nepal':
                        district = country_details[-1].text
                        nepal_peak = True
                        break
                # If the peak is not in Nepal, continue
                if not nepal_peak:
                    continue
                # Get the latitude and longitude section
                location_section = soup.find('div', attrs={"class": "sidebar__hs-chip location-coordinates js-location-coordinates js-copy-to-clipboard"})
                lat = location_section.find('span', attrs={"id": "lat"}).text
                lon = location_section.find('span', attrs={"id": "lng"}).text
                # Get the text from the about section
                about = soup.find('div', attrs={"class": "sidebar__hs-desc-text"}).text.strip()
                # We found the peak and the data. We can stop here
                page_found = True
                break
            except AttributeError:
                # If there was an error reset the lat, lon, district and about and continue
                lat, lon, district, about = None, None, None, None
                continue
    # If the peak_page is not found, return None for all the values
    if not page_found:
        return None, None, None, None
    return lat, lon, district, about


def get_nhpp_and_hd_non_matching_peaks(nhpp_peaks_df: pd.DataFrame) -> pd.DataFrame:
    """
    This function gets all the peaks in both the NHPP and HD datasets which are not found in the other.
    The functions creates a non_matching_peaks_df.csv file in the /data/all_nhpp_alt_names folder containing the
    list of non-matching peaks.
    :param nhpp_peaks_df: The NHPP peaks dataframe
    :return: The non-matching peaks dataframe
    """
    # Get the Himalayan Database peaks data into a Pandas DataFrame
    hd_peaks_df = pd.read_csv(os.path.join(HD_DATA_DIR, 'peaks.csv'))
    # Get the non matching peaks
    non_matching_peaks_df = hd_peaks_df.merge(nhpp_peaks_df, how='outer', left_on='PEAKID', right_on='ID')
    non_matching_peaks_df = non_matching_peaks_df[['PEAKID', 'PKNAME', 'PKNAME2', 'ID', 'NAME', 'ALTERNATE_NAMES']]
    non_matching_peaks_df.rename(columns={"PEAKID": "HD_ID", "PKNAME": "HD_NAME", "PKNAME2": "HD_ALT_NAMES",
                                          "ID": "NHPP_ID", "NAME": "NHPP_NAME", "ALTERNATE_NAMES": "NHPP_ALT_NAMES"},
                                 inplace=True)
    # Get all the possible peak names and alternate names from the HD dataset in a single flat list
    all_hd_names = non_matching_peaks_df[non_matching_peaks_df['HD_NAME'].notnull()]['HD_NAME'].tolist()
    all_hd_alt_names = non_matching_peaks_df[
        non_matching_peaks_df['HD_ALT_NAMES'].notnull()]['HD_ALT_NAMES'].tolist()
    all_hd_alt_names = [name.replace('?', '').strip() for names in all_hd_alt_names for name in names.split(',')]
    all_hd_possible_names = all_hd_names + all_hd_alt_names
    # Get all the possible peak names and alternate names from the NHPP dataset in a single flat list
    all_nhpp_names = non_matching_peaks_df[non_matching_peaks_df['NHPP_NAME'].notnull()]['NHPP_NAME'].tolist()
    all_nhpp_alt_names = non_matching_peaks_df[
        non_matching_peaks_df['NHPP_ALT_NAMES'].notnull()]['NHPP_ALT_NAMES'].tolist()
    all_nhpp_alt_names = [name.strip() for names in all_nhpp_alt_names for name in names.split(',')]
    all_nhpp_possible_names = all_nhpp_names + all_nhpp_alt_names
    # Keep only rows with PeakID or ID null
    non_matching_peaks_df = non_matching_peaks_df[
        non_matching_peaks_df['HD_ID'].isnull() | non_matching_peaks_df['NHPP_ID'].isnull()]
    # For all the rows in the DataFrame where one of the possible name of the peak in the HD dataset
    # is in the name or alternate column of the NHPP dataset, then drop the hd_peak
    for index, hd_peak in non_matching_peaks_df[non_matching_peaks_df['HD_NAME'].notnull()].iterrows():
        # Get all the possible names of the peak
        hd_names = [hd_peak['HD_NAME']]
        if pd.notnull(hd_peak['HD_ALT_NAMES']):
            hd_names += [name.strip() for name in hd_peak['HD_ALT_NAMES'].split(',')]
        # For each alternate name, if it is in the name column, drop the hd_peak
        for name in hd_names:
            if name.strip() in all_nhpp_possible_names:
                non_matching_peaks_df.drop(index, inplace=True)
                break
    # For all the rows in the DataFrame where one of the possible name of the peak in the NHPP dataset
    # is in the name or alternate column of the HD dataset, then drop the hd_peak
    for index, nhpp_peak in non_matching_peaks_df[non_matching_peaks_df['NHPP_NAME'].notnull()].iterrows():
        # Get all the possible names of the peak
        nhpp_names = [nhpp_peak['NHPP_NAME']]
        if pd.notnull(nhpp_peak['NHPP_ALT_NAMES']):
            nhpp_names += nhpp_peak['NHPP_ALT_NAMES'].split(',')
        # For each alternate name, if it is in the name column, drop the hd_peak
        for name in nhpp_names:
            if name.strip() in all_hd_possible_names:
                non_matching_peaks_df.drop(index, inplace=True)
                break
    non_matching_peaks_df.to_csv(os.path.join(NHPP_DATA_DIR, 'non_matching_peaks.csv'), index=False)
    return non_matching_peaks_df


def get_missing_peak_data_from_peakvisor(nhpp_peaks_df: pd.DataFrame,
                                         non_matching_peaks_df: pd.DataFrame) -> pd.DataFrame:
    """
    This function gets the list of peak which are in the NHPP dataset but not in the HD dataset and vice-versa.
    :param nhpp_peaks_df: The NHPP peaks dataframe
    :param non_matching_peaks_df: The dataframe of non-matching peaks from the NHPP and HD datasets
    :return: The dataframe with missing peaks from both the NHPP and HD datasets
    """
    # Get all the unique possible districts
    possible_districts = nhpp_peaks_df['DISTRICT'].dropna().unique()
    # Keep only the peaks from the HD dataset (the ones with the NHPP_ID null)
    non_matching_peaks_df = non_matching_peaks_df[non_matching_peaks_df['NHPP_ID'].isnull()]
    # Get the peaks as a list of dictionary records
    peaks = non_matching_peaks_df.to_dict('records')
    # Remove the peaks for which we have an ID in the PEAKVISOR_NOT_TO_IMPORT list
    peaks = [peak for peak in peaks if peak['HD_ID'] not in PEAKVISOR_NOT_TO_IMPORT]
    # For all peaks convert the HD_ALT_NAMES to a list and add a field of all the peak possible names as the
    # combination of the HD_NAME and the HD_ALT_NAMES list
    for peak in peaks:
        if pd.notnull(peak['HD_ALT_NAMES']):
            peak['HD_ALT_NAMES'] = [p.replace('?', '').strip() for p in peak['HD_ALT_NAMES'].split(',')]
        else:
            peak['HD_ALT_NAMES'] = []
        peak['PEAK_POSSIBLE_NAMES'] = [peak['HD_NAME']] + peak['HD_ALT_NAMES']
    # Use 4 workers in parallel to process the peaks and get their data from peakvisor
    # And use TQDM to show the progress
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        peakvisor_data = list(
            tqdm(executor.map(get_data_from_peakvisor, [peak['PEAK_POSSIBLE_NAMES'] for peak in peaks]),
                 total=len(peaks)))
    # For all the distict values in peakvisor_data[i][2] check if the value is contained in on of the possible_districts
    # If it is repllace the value with the comete one from the possible_districts
    # If it is not contained in any of the possible_districts keep the value
    districts = []
    province = []
    for i in range(len(peakvisor_data)):
        district_found = False
        for possible_district in possible_districts:
            if peakvisor_data[i][2] and peakvisor_data[i][2] in possible_district:
                districts.append(possible_district)
                district_found = True
                break
        # Get the province data for all discticts from district with the same name
        if not district_found:
            districts.append(peakvisor_data[i][2])
        if districts[i]:
            # Find in the NHPP Dataframe a row with the same district name and get the municipality from it
            province.append(nhpp_peaks_df[nhpp_peaks_df['DISTRICT'] == districts[i]]['PROVINCE'].values[0])
        else:
            province.append(None)
    # Generate a Dataframe from the peakvisor_data
    # The ID column is the peak['HD_ID'] the NAME column is the peak['HD_NAME'], the ALTERNATE_NAMES colums is the
    # peak['HD_ALT_NAMES'], the LAT is the peakvisor_data[0], the LON is the peakvisor_data[1],
    # the DISTRICT and the ABOUT is the peakvisor_data[3]
    peakvisor_df = pd.DataFrame({
        'ID': [peak['HD_ID'] for peak in peaks],
        'NAME': [peak['HD_NAME'] for peak in peaks],
        'ALTERNATE_NAMES': [','.join(peak['HD_ALT_NAMES']) for peak in peaks],
        'LAT': [peakvisor_data[i][0] for i in range(len(peaks))],
        'LON': [peakvisor_data[i][1] for i in range(len(peaks))],
        'PROVINCE': province,
        'DISTRICT': districts,
        'DESCRIPTION': [peakvisor_data[i][3] for i in range(len(peaks))]
        })
    # Drop the rows where the LAT and LON are null
    peakvisor_df.dropna(subset=['LAT', 'LON'], inplace=True)
    # Save the peakvisor_df to a csv file
    peakvisor_df.to_csv(os.path.join(NHPP_DATA_DIR, 'peakvisor_peaks.csv'), index=False)
    return peakvisor_df


def merge_nepal_peaks_datasets(nhpp_peaks_df: pd.DataFrame, peakvisor_peaks_df: pd.DataFrame):
    """
    This function concatenates the peaks data collected from the NHPP and Peakvisor websites and manually collected data
    and adds the references from the Himalayan Database into result dataset.
    The function creates a new file called nhpp_peaks_with_hd_references.csv in the /data/all_nhpp_alt_names folder.
    :param nhpp_peaks_df: The NHPP peaks DataFrame
    :param peakvisor_peaks_df: The peakvisor peaks DataFrame
    :return: The merged DataFrame
    """
    additional_peaks_df = pd.read_csv(os.path.join(NHPP_DATA_DIR, 'manually_collected_peaks.csv'),
                                      sep=';', encoding='utf-8')
    nhpp_peaks_df = pd.concat([nhpp_peaks_df, peakvisor_peaks_df, additional_peaks_df])
    # Get the Himalayan Database peaks data into a Pandas DataFrame
    hd_peaks_df = pd.read_csv(os.path.join(HD_DATA_DIR, 'peaks.csv'))
    # In both datasets create a new column ALL_NAMES as a list containing the NAME and  the content of the alternate
    # name column transformed as a list split by comma and stripped from spaces
    nhpp_peaks_df['ALL_NAMES'] = nhpp_peaks_df[['NAME', 'ALTERNATE_NAMES']].fillna('').agg(','.join, axis=1)
    nhpp_peaks_df['ALL_NAMES'] = nhpp_peaks_df['ALL_NAMES'].apply(
        lambda x: [name.strip() for name in x.split(',') if name])
    hd_peaks_df['ALL_NAMES'] = hd_peaks_df[['PKNAME', 'PKNAME2']].fillna('').agg(','.join, axis=1)
    hd_peaks_df['ALL_NAMES'] = hd_peaks_df['ALL_NAMES'].apply(lambda x: [name.strip() for name in x.split(',') if name])
    # Explode both datasets so that each row contains only one peak name
    nhpp_peaks_df = nhpp_peaks_df.explode('ALL_NAMES')
    hd_peaks_df = hd_peaks_df.explode('ALL_NAMES')
    # Merge the datasets based on all their possible names
    nhpp_peaks_df = nhpp_peaks_df.merge(hd_peaks_df[['PEAKID', 'PKNAME', 'PKNAME2', 'ALL_NAMES']],
                                        how='left', on='ALL_NAMES')
    # Regroup the  peaks by ID keeping the first vlu o every column
    nhpp_peaks_df = nhpp_peaks_df.groupby('ID').first().reset_index()
    # Copy the ID into PEAKID when it is null
    nhpp_peaks_df['PEAKID'] = nhpp_peaks_df['PEAKID'].fillna(nhpp_peaks_df['ID'])
    # Drop the PKNAME, PKNAME2 and ALL_NAMES columns. We don't need them anymore
    nhpp_peaks_df.drop(['PKNAME', 'PKNAME2', 'ALL_NAMES'], axis=1, inplace=True)
    # Move the PEAKID column as the second column for easier comparison with the ID column
    cols = nhpp_peaks_df.columns.tolist()
    cols = cols[:1] + cols[-1:] + cols[1:-1]
    nhpp_peaks_df = nhpp_peaks_df[cols]
    # Sort the peaks by ID
    nhpp_peaks_df.sort_values('ID', inplace=True)
    # Save the dataset into a CSV file
    nhpp_peaks_df.to_csv(os.path.join(NHPP_DATA_DIR, 'preprocessed_nhpp_peaks.csv'), index=False)


if __name__ == "__main__":
    # Get all the peaks
    print("Web Scrapping all the peaks' URLs")
    all_peaks = get_all_nhpp_peak_table()
    # Get the peak profile for each peak
    print("Web Scrapping all the peaks' profiles")
    # Use multi-threading to load the peak details in parallel in groups of 8
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        peaks = list(tqdm(executor.map(get_nhpp_peak_profile, all_peaks), total=len(all_peaks)))
    # Save the peaks details in a CSV file
    print("Saving the peaks' details in a CSV file")
    nhpp_peaks_df = pd.DataFrame(peaks)
    # Save the NHPP dataset into a CSV file
    peaks_file = os.path.join(NHPP_DATA_DIR, 'nhpp_peaks.csv')
    os.makedirs(os.path.dirname(peaks_file), exist_ok=True)
    nhpp_peaks_df.to_csv(peaks_file, index=False, encoding='utf-8')
    # Below line is used when testing to avoid web scrapping again
    # nhpp_peaks_df = pd.read_csv(os.path.join(NHPP_DATA_DIR, 'nhpp_peaks.csv'))  # For testing
    # Get the peaks from both the NHPP and HD datasets which do not match
    non_matching_peaks_df = get_nhpp_and_hd_non_matching_peaks(nhpp_peaks_df)
    # Try to get the missing peaks from the Peakvisor website
    peakvisor_df = get_missing_peak_data_from_peakvisor(nhpp_peaks_df, non_matching_peaks_df)
    # Below line is used when testing to avoid web scrapping again
    # peakvisor_df = pd.read_csv(os.path.join(NHPP_DATA_DIR, 'peakvisor_peaks.csv'))  # For testing
    merge_nepal_peaks_datasets(nhpp_peaks_df, peakvisor_df)
