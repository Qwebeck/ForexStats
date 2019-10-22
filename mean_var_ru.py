
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


def mean_std_momentum (in_data,period):
    momentum = []
    for i in range(period,len(in_data)-1):
        momentum.append(in_data.iloc[i]/in_data.iloc[i-period] * 100)
    momentum = numpy.array(momentum)
    return round(numpy.std(momentum),6),round(numpy.mean(momentum),6)


def show_dir(directory = os.path.dirname(os.path.realpath(__file__)),csv_volume = volumes):
    print('------------------------------------------------------------------------------------------------')
    if time_period:
        print('Текущий временной промежуток: ', time_period)
    else:
        print('Временной промежуток не указан')
    print(f'Файлы с валютной историей в папке {directory}:')
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
            print(f'-----{i+1}. {item} <--------- Описано {csv_volume[item][0]} день ---- Timeframe: {csv_volume[item][1][1]} {csv_volume[item][1][0].name}')
        elif str(csv_volume[item][0])[-1] == '0' or str(csv_volume[item][0])[-1] == '2':
            print(f'-----{i+1}. {item} <--------- Описано {csv_volume[item][0]} дней ---- Timeframe: {csv_volume[item][1][1]} {csv_volume[item][1][0].name}')

        
        else:
            print(f'-----{i+1}. {item} <--------- Описано {csv_volume[item][0]} дня ---- Timeframe: {csv_volume[item][1][1]} {csv_volume[item][1][0].name}')
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
    
    # if time_frame_type.value < time_period_type.value:
        #данные пользователя переводяться в данные в таймфрейме
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
            # print('В выбраном файле недостаточно данных чтобы просчитать значения для заданого периода')
            raise ValueError('Недостаточно данных в файле чтобы посчитать статистики на этом временном промежутке.')
        else:
            return data[-number_of_items:]
    elif time_period[-1] == 'd':
        number_of_items = convert_timeperiod_in_timeframe(time_frame_value, time_frame_type,time_period_value, TimeFrame.Day)
        if number_of_items > len(data.index):
            # print('В выбраном файле недостаточно данных чтобы просчитать значения для заданого периода')
            raise ValueError('Недостаточно данных в файле чтобы посчитать статистики на этом временно промежутке.')
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
            # print('В выбраном файле недостаточно данных чтобы просчитать значения для заданого периода')
            raise ValueError('Недостаточно данных в файле чтобы посчитать статистики на этом временном промежутке.')
        else:
            return data.where(data[0] >= day).dropna()
    else:
        print('Неправильно введенный промежуток')
        
        raise ValueError('Неправильно введенный временной промежуток.')
  


def read_file(file):
    try:
        data = pandas.read_csv(file, header = None, sep=',', low_memory = False)    
        if len(data.columns) < 5:
            '''
            Handling another separator
            '''
            data = pandas.read_csv(file, header = None, sep='\t', low_memory = False)    
        
        try:
            '''
            Проверка на разные типы сепараторов. Если нельзя конвертировать цену закрытия в int значит нет такой колоны, 
            то есть сепаратор неправильный
            '''
            
            int(data.iloc[5,0])
        except ValueError:
            data = data.iloc[1:]
        return data
    
    except FileExistsError:
            print('Несуществующий файл')
    
            



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
            print(f"Данные от {data.iloc[0][0].date()} {data.iloc[0][1]} до {data.iloc[-1][0].date()} {data.iloc[-1][1]}")
        else:
            print(f"Данные от {data.iloc[0][0].date()} до {data.iloc[-1][0].date()}")

        mean = round(numpy.mean(data[5]),6)
        std = round(numpy.std(data[5]),6)

        for function in functions:
            if function == 'mean':
                
                print('Средняя:',mean)
            
            elif function == 'std':
                print('Сигма:',std)
                print('Средняя + 2 сигма: ', round(mean + std * 2,6))
                print('Средняя - 2 сигма: ', round(mean - std * 2,6))
            elif len(function.split('_')) != 1 and function != sys.argv[0]:
                # and len(function.split('.')) == 0
                periods = function.split('_')[1:]
                for period in periods:
                  
                    current = mean_std_momentum(data[5],int(period))
                    print(f'Momentum ({period}), сигма: {current[0]}' )
                    print(f'Momentum ({period}), средняя: {current[1]}' )

    except ValueError as e:
        # print('Недостаточно данных чтобы посчитать значения для выбраного периода')
        print(e)
        
        
    print('------------------------------------------------------------------------------------------------')
    
    


    # number_of_items = convert_timeperiod_in_timeframe(time_frame_value, time_frame_type,time_period)
    # return data


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
# print('Вызов скрипта с определенными параметрами для конкретного файла: stats func1 [func2] ... [временной_промежуток] filename')
    if init:
        print('------------------------------------------------------------------------------------------------')
        print('Запуск скрипта в его домашней директории: stats home [временной_промежуток]')
        print('Запуск скрипта в текущей директории: stats [временной_промежуток]') #-- случай 1
    print('------------------------------------------------------------------------------------------------')
    print('Пример временного промежутка: 60h, 20d. Возможные форматы временного промежутка: ')
    print('h -- час')
    print('d -- день')
    print('m -- месяц')
    print('Неуказанный временной промежуток значит рассчёт статистик с учётом всех данных в файле')
    print('------------------------------------------------------------------------------------------------')
    print('Возможные функции:')
    print('mean -- Средняя цены')
    print('std  -- Отклонение цены')
    print('mnt_период1_[период2]_...  -- Средняя и отклонения моментума для указаного периода в свечах')
    print('------------------------------------------------------------------------------------------------') 
    option = input('Для выхода нажать 0, enter чтобы продолжить')
    try:
        if int(option) == 0:
            exit()
    except ValueError:
        pass




os.system('cls')
if len(sys.argv) == 1:
    time_period = 0
elif len(sys.argv) == 2 and sys.argv[1] != 'home':
        # случай 1
    time_period = sys.argv[1]
elif sys.argv[1] == 'home':
    if len(sys.argv) == 3:
        time_period = sys.argv[-1]
    else:
        time_period = 0
            




while True:
    if len(sys.argv) == 1:
        directory_content = show_dir(os.getcwd())
        directory = os.getcwd()
        #время которое принимаеться во внимание
    elif len(sys.argv) == 2 and sys.argv[1] != 'home' and sys.argv[1] != 'help':
            # случай 1
        directory_content = show_dir(os.getcwd())
        directory = os.getcwd()
            
            
    elif sys.argv[1] == 'help':
        help(init=True)
        directory_content = show_dir(os.path.dirname(os.path.realpath(__file__)))
        directory = os.getcwd()
            
    elif sys.argv[1] == 'home':
        directory_content = show_dir(os.path.dirname(os.path.realpath(__file__)))
        directory = os.path.dirname(os.path.realpath(__file__))
            
        #else:
        #   stats_for_file(sys.argv[:-1],sys.argv[-1])
        #    continue 
    print('-----0. Выйти')
    print(' ')


    option = input('Команды в формате func1,func2,...,номер файла из списка. Номер файла чтобы показать среднюю и отклонение ')
    try:
        if len(option) == 1 and int(option) == 0:
            exit(0)
        elif len(option) == 1:
                
            stats_for_file(['mean','std'],os.path.join(directory,directory_content[int(option)-1]), time_period)
        else:
            args = option.split(',')
            if args[-1] == 0:
                print('Вместо номера файла указана опция выхода')
            else:
                stats_for_file(args[:-1],os.path.join(directory,directory_content[int(args[-1])-1]), time_period)    
    except ValueError:
        print('Неправильно записанные функции(mean,std,mnt_ ), не поставлена запятая или не выбран файл ')
    except IndexError:
        print('Выбрана опция которой нет в списке ')
    except TypeError:
        print('Тип временного указаного временного промежутка меньше типа таймфрейма. Например промежуток 30m, timeframe 1d ')
    print(' ')
    option = input('Для изменения периода введите новое значение, чтобы продолжить со старым периодом нажмите enter \nУбрать ограничения с временного промежутка: all. Выход: 0. Помощь: help \n .... ')
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
            print('Неправильный формат времени')
            input("Enter ...")
        os.system('cls') 
    except ValueError:
        os.system('cls')
        continue
    
            

   

 


