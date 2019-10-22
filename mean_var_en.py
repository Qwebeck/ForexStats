
import pip
import subprocess 
import sys
import os
from enum import Enum, auto

volumes = {}


class TimeFrame(Enum):
    Minute=auto()
    Hour = auto()
    Day = auto()
    Month = auto()
    Year = auto()

try:
    numpy = __import__('numpy')
except ImportError:
    subprocess.check_call("pip install numpy")
    numpy = __import__('numpy')
try:
    pandas = __import__('pandas')
except:
    subprocess.check_call("pip install pandas")
    pandas = __import__('pandas')
# _import('sys')



def clean_screen():
    if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
        os.system('clear')
    else:
        os.system('cls')

def mean_std_momentum (in_data,period):
    momentum = []
    for i in range(period,len(in_data)-1):
        momentum.append(in_data.iloc[i]/in_data.iloc[i-period] * 100)
    momentum = numpy.array(momentum)
    return round(numpy.std(momentum),6),round(numpy.mean(momentum),6)


def show_dir(directory = os.path.dirname(os.path.realpath(__file__)),csv_volume = volumes):
    print('------------------------------------------------------------------------------------------------')
    if time_period:
        print('Current time period: ', time_period)
    else:
        print('Time period not specified')
    print(f'Files with currency history in directory {directory}:')
    dircontent = os.listdir(directory)
    data_files = []
    for item in dircontent:
        filename, file_extension = os.path.splitext(item)
        if file_extension == '.csv':
            data_files.append(item)
    
    i = 0
    for item in data_files:
        
        
        if item not in csv_volume:
            csv_volume[item] = date_range_in_file(os.path.join(directory,item))

        if csv_volume[item][0] == 1:
            print(f'-----{i+1}. {item} <--------- Described {csv_volume[item][0]} day ---- Timeframe: {csv_volume[item][1][1]} {csv_volume[item][1][0].name}')
        else :
            print(f'-----{i+1}. {item} <--------- Described {csv_volume[item][0]} days ---- Timeframe: {csv_volume[item][1][1]} {csv_volume[item][1][0].name}')
        i += 1
    return data_files


def calculate_timeframe(data,is_print = True):
    if abs(int(data[1][1].split(':')[1]) - int(data[1][2].split(':')[1])):
        time = abs(int(data[1][1].split(':')[1]) - int(data[1][2].split(':')[1]))
        if is_print:
            print(f'Time frame: {time} M')
        return TimeFrame.Minute,time
    elif abs(int(data[1][1].split(':')[0]) - int(data[1][2].split(':')[0])):
        time = abs(int(data[1][1].split(':')[0]) - int(data[1][2].split(':')[0]))
        if is_print:
            print(f'Time frame: {time} H')
        return TimeFrame.Hour,time
    elif abs(int(data[0][1].split('.')[2]) - int(data[0][2].split('.')[2])):
        time = abs(int(data[0][1].split('.')[2]) - int(data[0][2].split('.')[2]))
        if is_print:
            print(f'Time frame: {time} D')
        return TimeFrame.Day,time
    elif abs(int(data[0][1].split('.')[1]) - int(data[0][2].split('.')[1])):
        time = abs(int(data[0][1].split('.')[1]) - int(data[0][2].split('.')[1]))
        if is_print:
            print(f'Time frame: {time} Month')
        return TimeFrame.Month,time
    elif abs(int(data[0][1].split('.')[0]) - int(data[0][2].split('.')[0])):
        time = abs(int(data[0][1].split('.')[0]) - int(data[0][2].split('.')[0]))
        if is_print:
            print(f'Time frame: {time} Years') 
        return TimeFrame.Year,time



def convert_timeperiod_in_timeframe(time_frame_value,time_frame_type,time_period_value, time_period_type):
    
    minutes_in_hour = 60
    hours_in_day = 24
    
    
    if time_frame_type == TimeFrame.Minute and time_period_type == TimeFrame.Hour:
        return int(time_period_value * minutes_in_hour / time_frame_value) + 1
    elif time_frame_type == TimeFrame.Minute and time_period_type == TimeFrame.Day:
        return int(time_period_value * minutes_in_hour * hours_in_day / time_frame_value) + 1
    elif time_frame_type == TimeFrame.Hour and time_period_type == TimeFrame.Hour:
        return time_period_value + 1
    elif time_frame_type == TimeFrame.Hour and time_period_type == TimeFrame.Day:  
        return int(time_period_value * hours_in_day / time_frame_value) + 1
    elif time_frame_type == TimeFrame.Day and time_period_type == TimeFrame.Day:
        
        return time_period_value + 1
        

def crop_data_by_time_period(time_frame_value, time_frame_type, time_period, data):
    time_period_value = int(time_period[:-1])
    
  
    if time_period[-1] == 'h': 
        number_of_items = convert_timeperiod_in_timeframe(time_frame_value, time_frame_type,time_period_value, TimeFrame.Hour)
        if number_of_items > len(data.index):
        
            raise ValueError('Not enough data to calculate statistics for required period.')
        else:
            return data[-number_of_items:]
    elif time_period[-1] == 'd':
        number_of_items = convert_timeperiod_in_timeframe(time_frame_value, time_frame_type,time_period_value, TimeFrame.Day)
        if number_of_items > len(data.index):
        
            raise ValueError('Not enough data to calculate statistics for required period.')
        else:
            return data[-number_of_items:]
    elif time_period[-1] == 'm':
        start_month = data[0].max().month
        start_year = data[0].max().year
        start_day = data[0].max().day
        time_period_value += 12 - start_month
        year_diff = int(time_period_value / 12)
        month = 12 - time_period_value % 12
        if month < 10:
            month = '0' + str(month)
        else:
            month = str(month)
        day = str(start_year - year_diff) + '.' + str(month) + '.' + str(start_day)
        day = pandas.to_datetime(day)
        if data[0].min() > day:
        
            raise ValueError('Not enough data to calculate statistics for required period.')
        else:
            return data.where(data[0] >= day).dropna()
    else:
        print('Incorrectly entered time frame')
        
        raise ValueError('Incorrectly entered time frame.')
  


def read_file(file):
    try:
        data = pandas.read_csv(file, header = None, sep=',', low_memory = False)    
        if len(data.columns) < 5:
            '''
            Handling another separator
            '''
            data = pandas.read_csv(file, header = None, sep='\t', low_memory = False)    
        
        try:
         
            int(data.iloc[5,0])
        except ValueError:
            data = data.iloc[1:]
        return data
    
    except FileExistsError:
            print('File does not exist')
    
            



def stats_for_file(functions,file,time_period = 0):
   
    print('------------------------------------------------------------------------------------------------')
    data = read_file(file)

    if data.dtypes[5] == 'object':
        data[5] = data[5].astype(float)
    time_frame_type,timeframe = calculate_timeframe(data)
    data[0] = pandas.to_datetime(data[0],infer_datetime_format = True)
    try:
        if time_period:
            data = crop_data_by_time_period(timeframe,time_frame_type,time_period,data)
        if type(time_period) != int and time_period[-1] == 'h':
            print(f"Data from {data.iloc[0][0].date()} {data.iloc[0][1]} untill {data.iloc[-1][0].date()} {data.iloc[-1][1]}")
        else:
            print(f"Data from {data.iloc[0][0].date()} untill {data.iloc[-1][0].date()}")

        mean = round(numpy.mean(data[5]),6)
        std = round(numpy.std(data[5]),6)

        for function in functions:
            if function == 'mean':
                
                print('Mean:',mean)
            
            elif function == 'std':
                print('Sigma:',std)
                print('Mean + 2.6 * sigma: ', round(mean + std * 2,6))
                print('Mean - 2.6 * sigma: ', round(mean - std * 2,6))
            elif len(function.split('_')) != 1 and function != sys.argv[0]:
                # and len(function.split('.')) == 0
                periods = function.split('_')[1:]
                for period in periods:
                  
                    current = mean_std_momentum(data[5],int(period))
                    print(f'Momentum ({period}), sigma: {current[0]}' )
                    print(f'Momentum ({period}), mean: {current[1]}' )

    except ValueError as e:
     
        print(e)
        
        
    print('------------------------------------------------------------------------------------------------')
    
    


def date_range_in_file(csv_file):
    data = read_file(csv_file)
    timeframe = calculate_timeframe(data, is_print = False)
    data[0] = pandas.to_datetime(data[0],infer_datetime_format = True)
    delta = (data[0].max() - data[0].min()).days
    
    if delta:
        return delta, timeframe
    else:
        return 1, timeframe


    
def help(init = False):
    time_period = 0
# print('Вызов скрипта с определенными параметрами для конкретного файла: stats func1 [func2] ... [временной_промежуток] filename')
    if init:
        print('------------------------------------------------------------------------------------------------')
        print('Running the script in his home directory: stats home [time frame]')
        print('Running script in current directory: stats [time frame]') 
    print('------------------------------------------------------------------------------------------------')
    print('Example of possible timeframe input: 60h, 20d. Possible formats of timeframe: ')
    print('h -- hour')
    print('d -- day')
    print('m -- month')
    print('An unspecified time interval means calculating statistics taking into account all the data in the file')
    print('------------------------------------------------------------------------------------------------')
    print('Possible functions:')
    print('mean -- mean of price')
    print('std  -- standart deviation')
    print('mnt_period1_[period2]_...  -- Mean and standart deviation for every of entered periods')
    print('------------------------------------------------------------------------------------------------') 
    option = input('Press 0 to exit, any key to resume')
    try:
        if int(option) == 0:
            exit()
            
    except ValueError:
        pass


if len(sys.argv) == 1:
    time_period = 0
elif len(sys.argv) == 2 and sys.argv[1] != 'home' and sys.argv[1] != 'help':
       
    time_period = sys.argv[1]
elif sys.argv[1] == 'home':
    if len(sys.argv) == 3:
        time_period = sys.argv[-1]
    else:
        time_period = 0
elif sys.argv[1] == 'help':
    time_period = 0
            




while True:
    clean_screen()
    if len(sys.argv) == 1:
        directory_content = show_dir(os.getcwd())
        directory = os.getcwd()
  
    elif len(sys.argv) == 2 and sys.argv[1] != 'home' and sys.argv[1] != 'help':
           
        directory_content = show_dir(os.getcwd())
        directory = os.getcwd()
            
            
    elif sys.argv[1] == 'help':
        help(init=True)
        directory_content = show_dir(os.path.dirname(os.path.realpath(__file__)))
        directory = os.getcwd()
            
    elif sys.argv[1] == 'home':
        directory_content = show_dir(os.path.dirname(os.path.realpath(__file__)))
        directory = os.path.dirname(os.path.realpath(__file__))
            
    
    print('-----0. Exit')
    print(' ')


    option = input('Commands in format func1,func2,...,number of file in list. You can type only number of file in order to show mean and standart deviation ')
    try:
        if len(option) == 1 and int(option) == 0:
            exit(0)
        elif len(option) == 1:
                
            stats_for_file(['mean','std'],os.path.join(directory,directory_content[int(option)-1]), time_period)
        else:
            args = option.split(',')
            if args[-1] == 0:
                print('The file number is replaced by the exit option')
            else:
                stats_for_file(args[:-1],os.path.join(directory,directory_content[int(args[-1])-1]), time_period)    
    except ValueError:
        print('Incorrectly written functions (mean, std, mnt_ ), no comma or no file selected ')
    except IndexError:
        print('Choosen option is not in list')
    except TypeError:
        print('The type of time period specified is less than the type of time frame in file. For example, the interval of 30m, could not be based on data in file that stores value of price for every hour ' )
    print(' ')
    option = input('To change the period -- enter a new value, to continue with the old period -- press enter \nCalculate stats for all dat ain file: all. Exit: 0. Help: help \n .... ')
    try:
        if option == 'help':
           help()        
        elif option == 'all':
            time_period = 0
        elif len(option) > 1 and (option[-1] =='h' or option[-1] =='m' or  option[-1] =='d') :
            time_period = option
        elif int(option) == 0:
            exit(0)
        else:
            print('Incorrect time format')
            input("Enter ...")
        clean_screen()
    except ValueError:
        clean_screen()
        continue
    
            

   

 


