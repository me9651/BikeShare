import os           # File system path resolution
import time         # Time measurement for statistic collection
import calendar     # Calendar month and day information
import datetime     # Date utilities
import pandas       # Numerical analysis and csv import


# Filenames and path of script execution
# Data files are expected to be in the same directory as the script
file_path = os.path.dirname(os.path.realpath(__file__))
chicago = 'chicago.csv'
new_york_city = 'new_york_city.csv'
washington = 'washington.csv'


def get_city_filename():
    '''Prompts user for a city and returns the fully qualified filename and path for that city's bike share data.

    Args:
        none.
    Returns:
        (str) Fully qualified filename and path for a city's bikeshare data.
    '''

    while True:
        city = input('Which city would you like to view? (\'Chicago\', \'New York\', or \'Washington\'): ')
        city = city.lower()

        if city == 'chicago':
            return os.path.join(file_path, chicago)
        elif city == 'new york':
            return os.path.join(file_path, new_york_city)
        elif city == 'washington':
            return os.path.join(file_path, washington)
        else:
            print('An invalid city was entered.\n')


def open_file(file_path: str):
    ''' Reads CSV file and returns structured data using Pandas.

    Args:
        file_path (str): The fully qualified file name and path of the CSV file containing city data
    Returns:
        DataFrame: A Pandas DataFrame with columns matching the provided CSV file
    '''

    data = pandas.read_csv(filepath_or_buffer=file_path,
                           sep=',',
                           header=0,
                           parse_dates=[0,1],
                           index_col=0,
                           memory_map=True)
    
    return data


def filter_city_data(city_data, time_period):
    ''' Filters city data to the month or day specified.

    Args:
        city_data (DataFrame): A Pandas DataFrame of city data
        time_period (dict): Specifies Year, Month, Day (inclusive) to filter city_data 
    Returns:
        DataFrame: A Pandas DataFrame including rows having a 'Start Time' within the time_period 
    '''
    # filter city_data to dates included within time_period
    return city_data[(city_data['Start Time'].dt.date >= datetime.date(time_period['year'], time_period['month'], time_period['day'][0]))
                        & (city_data['Start Time'].dt.date <= datetime.date(time_period['year'], time_period['month'], time_period['day'][1]))]


def get_time_period():
    '''Prompt user for a time period and returns the specified filter.

    Args:
        none.
    Returns:
        (dict): {period: str, year: int, month: int, day: [int, int]}
                Valid period are 'month', 'day', 'none' specifying granularity of filter.   
    '''

    while True:
        time_period = input('Filter data? (\'month\', \'day\', or \'none\'): ')
        time_period = time_period.lower()

        if time_period == 'month':
            m = get_month()
            last_day_of_month = calendar.monthrange(2017, m)[1]
            return {'period': 'month', 'year': 2017, 'month': m, 'day': [1, last_day_of_month]}
        elif time_period == 'day':
            m = get_month()
            d = get_day(m)
            return {'period': 'day', 'year': 2017, 'month': m, 'day': [d, d]}
        elif time_period == 'none':
            return {'period': 'none', 'year': None, 'month': None, 'day': [None, None]}
        else:
            print('An invalid filter was entered.\n')


def get_month():
    '''Asks the user for a month and returns the specified month as an integer.
       Limits input to allowable values based on project requirements.

    Args:
        none.
    Returns:
        (int): 1-indexed calendar month value
    '''

    valid_months = ['january', 'february', 'march', 'april', 'may', 'june']

    while True:
        month = input('\nWhich month? January, February, March, April, May, or June? ')
        month = month.lower()

        if month in valid_months:
            return valid_months.index(month) + 1
        else:
            print('An invalid month was entered.\n')


def get_day(month):
    '''Asks the user for a day and returns the specified day. Limits input to allowable values
       based on number of days in month.

    Args:
        none.
    Returns:
        (int): Number of day in calendar month. 1-indexed.
    '''

    # Get last valid day number of given month
    # scope document defines all data as being in year 2017
    month_year = calendar.month_name[month] + ' 2017'
    last_day_of_month = calendar.monthrange(2017, month)[1]
    day_range = '[1...{}]'.format(last_day_of_month)

    while True:
        day = input('\nWhich day of ' + month_year + '? Valid days are ' + day_range + ': ')

        try:
            day = int(day)
        except ValueError:
            print('An invalid day was entered.\n')
            continue

        if 1 <= day <= last_day_of_month:
            return day
        else:
            print('An invalid day was entered.\n')


def popular_month(city_file):
    '''Answer question: What is the most popular month for start time?
    
    Args:
        city_file: Pandas DataFrame of city data
    Returns:
        (tuple): [0]: Calendar month name of start time
                 [1]: Number of times month appears in start time
    '''
    
    # Pandas Series in descending order, counting occurrences of unique values
    month_values = city_file['Start Time'].dt.month.value_counts()
    
    # Get readable calendar name and number of occurrences from 0th position
    return (calendar.month_name[month_values.index[0]], month_values.iloc[0])


def popular_day(city_file):
    '''Answer question: What is the most popular day of week (Monday, Tuesday, etc.) for start time?
    
    Args:
        city_file: Pandas DataFrame of city data
    Returns:
        (tuple): [0]: Calendar day name of start time
                [1]: Number of times day appears in start time
    '''

    # Pandas Series in descending order, counting occurrences of unique values
    day_values = city_file['Start Time'].dt.weekday.value_counts()
    
    # Get readable calendar name and number of occurrences from 0th position
    return (calendar.day_name[day_values.index[0]], day_values.iloc[0])


def popular_hour(city_file):
    '''Answer question: What is the most popular hour of day for start time?
    
    Args:
        city_file: Pandas DataFrame of city data
    Returns:
        (tuple): [0]: Hour number (24-hour format) of start time
                 [1]: Number of times hour appears in start time
    '''

    # Pandas Series in descending order, counting occurrences of unique values
    hour_values = city_file['Start Time'].dt.hour.value_counts()
    
    # Hour and number of occurrences
    return (hour_values.index[0], hour_values.iloc[0])


def trip_duration(city_file):
    '''Answer question: What is the total trip duration and average trip duration? Return in precision of minutes.
    
    Args:
        city_file: Pandas DataFrame of city data
    Returns:
        (dict): {total: int, mean: float}
                total: sum of trips
                mean: arithmetic mean of trips
    '''

    return {'total': city_file['Trip Duration'].sum(),
            'mean': city_file['Trip Duration'].mean()}


def popular_stations(city_file):
    '''Answer question: What is the most popular start station and most popular end station?
    
    Args:
        city_file: Pandas DataFrame of city data
    Returns:
        (dict): {start: (str, int), end: (str, int)}
                start: most popular starting station
                    [0]: Name of Station
                    [1]: Number of occurrences
                start: most popular ending station
                    [0]: Name of Station
                    [1]: Number of occurrences
    '''

    # Number of unique occurrences
    start = city_file['Start Station'].value_counts()
    end = city_file['End Station'].value_counts()

    return {'start': (start.index[0], start.iloc[0]),
            'end': (end.index[0], end.iloc[0])}


def popular_trip(city_file):
    '''Answer question: What is the most popular trip?
    
    Args:
        city_file: Pandas DataFrame of city data
    Returns:
        (tuple): (str, int)
                    [0]: 'Start Station' to 'End Station', expressed as a string
                    [1]: Number of trips between the stations
    '''
    trip = (city_file.groupby(['Start Station', 'End Station'])
                     .size()
                     .sort_values(ascending=False)
                     .reset_index(name='count'))

    return (trip['Start Station'][0] + ' to ' + trip['End Station'][0], trip['count'][0])


def users(city_file):
    '''Answer question: What are the counts of each user type?
    
    Args:
        city_file: Pandas DataFrame of city data
    Returns:
        Series: A Pandas Series with User Types and unique counts of occurrences
    '''
    return city_file['User Type'].value_counts().reset_index()


def gender(city_file):
    '''Answer question: What are the counts of gender?
    
    Args:
        city_file: Pandas DataFrame of city data
    Returns:
        Series: A Pandas Series with Genders and unique counts of occurrences
    '''
    return city_file['Gender'].value_counts().reset_index()


def birth_years(city_file):
    '''Answer question: What are the earliest (i.e. oldest user), most recent (i.e. youngest user),
    and most popular birth years?
    
    Args:
        city_file: Pandas DataFrame of city data
    Returns:
        (dict): {oldest: int, youngest: int, mode: int}
                    oldest: The lowest numeric birth year
                    youngest: The highest numeric birth year
                    mode: The arithmetic mode (most frequently occurring) birth year
    '''
    return {'oldest': int(city_file['Birth Year'].min()),
            'youngest': int(city_file['Birth Year'].max()),
            'mode': int(city_file['Birth Year'].value_counts().index[0])}


def display_tabular_data(city_file):
    '''Displays five lines of data. After displaying five lines, ask the user if they would like to see five more,
    continuing asking until they say stop.

    Args:
        none.
    Returns:
        none.
    '''

    x = 5   # number of rows to display per pass
    i = 0   # counter for current start row
    rows, cols = city_file.shape

    print('\nUser trip details:')
    while True:
        # Print x rows in the range 
        # print(tabulate(city_file[i:i+x], headers='keys', showindex=False, tablefmt='psql'))
        print(city_file[i:i+x].to_string(index=False, na_rep='', justify='left'))
        i = i + x
        
        if i > rows:
            print('End of trip details file.\n')
            break

        response = input('Continue? (\'c\', anything else to stop): ')
        response = response.lower()

        if response == 'continue' or response == 'c':
            print('\n')
            pass
        else:
            break


def display_data():
    ''' Ask the user if they would like to see detailed trip data displayed

    Args:
        none.
    Returns:
        bool: True: view individual trip data.
    '''

    while True:
        display = input('\nView individual trip data? (\'yes\' or \'no\').\n')
        display = display.lower()

        if display == 'yes':
            return True
        elif display == 'no':
            return False
        else:
            print('An invalid response was entered.\n')


def statistics():
    '''Calculates and prints out the descriptive statistics about a city and time period
    specified by the user via raw input.

    Args:
        none.
    Returns:
        none.
    '''

    print('\nHello! Let\'s explore some US bikeshare data!\n')

    # Filter by city (Chicago, New York, Washington)
    city_file_name = get_city_filename()

    # Load city data from file
    start_time = time.time()
    city_data = open_file(city_file_name)
    city_data_elements = [x.lower() for x in city_data]
    print("Loading data took: {0:.2f} seconds.\n".format(time.time() - start_time))
    
    # Prompt to filter by time period (month, day, none), then filter data
    time_period = get_time_period()

    if time_period['period'] == 'month' or time_period['period'] == 'day':
        start_time = time.time()
        city_data = filter_city_data(city_data, time_period)
        print("Filtering data took: {0:.2f} seconds.\n".format(time.time() - start_time))
    
    print('\n=== Statistics ===\n')

    # What is the most popular month for start time?
    if time_period['period'] == 'none':
        start_time = time.time()
        print('{0} is the most popular month: {1} rides.'.format(*popular_month(city_data)))
        print("({0:.2f} seconds)\n".format(time.time() - start_time))

    # What is the most popular day of week (Monday, Tuesday, etc.) for start time?
    if time_period['period'] == 'none' or time_period['period'] == 'month':
        start_time = time.time()
        print('{0} is the most popular day: {1} rides.'.format(*popular_day(city_data)))
        print("({0:.2f} seconds)\n".format(time.time() - start_time))

    # What is the most popular hour of day for start time?
    start_time = time.time()
    stat_popular_hour = popular_hour(city_data)
    if stat_popular_hour is not None:
        print('{0} is the most popular hour: {1} rides.'.format(*stat_popular_hour))
        print("({0:.2f} seconds)\n".format(time.time() - start_time))
    else:
        print('Most popular hour not available in filtered data.\n')

   # What is the total trip duration and average trip duration?
    start_time = time.time()
    trip_length = trip_duration(city_data)
    print('Total trip duration: {0} minutes'.format(trip_length['total']))
    print('Average trip duration: {0:.2f} minutes'.format(trip_length['mean']))
    print("({0:.2f} seconds)\n".format(time.time() - start_time))

    # What is the most popular start station and most popular end station?
    start_time = time.time()
    popular_station = popular_stations(city_data)
    print('"{0}" is the most popular starting station: {1} rides.'.format(*popular_station['start']))
    print('"{0}" is the most popular ending station: {1} rides.'.format(*popular_station['end']))
    print("({0:.2f} seconds)\n".format(time.time() - start_time))
    
    # What is the most popular trip?
    start_time = time.time()
    stat_popular_trip = popular_trip(city_data)
    print('"{0}" is the most popular trip: {1} rides.'.format(*stat_popular_trip))
    print("({0:.2f} seconds)\n".format(time.time() - start_time))

    # What are the counts of each user type?
    start_time = time.time()
    print('User type counts:')
    # print(tabulate(users(city_data), headers=['User Type', 'Count'], showindex=False, tablefmt='psql'))
    print(users(city_data).to_string(index=False, header=['User Type', 'Count']))
    print("({0:.2f} seconds)\n".format(time.time() - start_time))

    # What are the counts of gender?    
    if 'gender' in city_data_elements:
        start_time = time.time()
        print('Gender counts:')
        #print(tabulate(gender(city_data), headers=['Gender', 'Count'], showindex=False, tablefmt='psql'))
        print(gender(city_data).to_string(index=False, header=['Gender', 'Count']))
        print("({0:.2f} seconds)\n".format(time.time() - start_time))
    else:
        print('Gender data not available.\n')

    # What are the earliest (i.e. oldest user), most recent (i.e. youngest user), and
    # most popular birth years?
    if 'birth year' in city_data_elements:
        start_time = time.time()
        stats_birth_years = birth_years(city_data)
        print('Oldest birth year: {0}'.format(stats_birth_years['oldest']))
        print('Newest birth year: {0}'.format(stats_birth_years['youngest']))    
        print('Most common birth year: {0}'.format(stats_birth_years['mode']))
        print("({0:.2f} seconds)\n".format(time.time() - start_time))
    else:
        print('Birth year data not available.\n')

    # Display five lines of data at a time if user specifies that they would like to
    if display_data():
        display_tabular_data(city_data)

    # Restart?
    restart = input('\nWould you like to restart? (\'yes\', or anything else to quit): ')
    if restart.lower() == 'yes':
        city_data = None
        statistics()


if __name__ == "__main__":
    statistics()