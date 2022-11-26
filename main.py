import argparse
import Weather_getter

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--num', type=str, help='''1 - Добавление прогнозов за диапазон дат в базу данных,
                        2 - Получение прогнозов за диапазон дат из базы, 
                        3 - Создание открыток из полученных прогнозов,
                        4 - Выведение полученных прогнозов на консоль''')
    parser.add_argument('--date_1', type=str,
                        help='Введите с какой даты вы хотите увидеть прогноз в формате год-месяц-день!')
    parser.add_argument('--date_2', type=str,
                        help='Введите до какой даты вы хотите увидеть прогноз в формате год-месяц-день!')

    arg = parser.parse_args()

    weather_machine = Weather_getter.WeatherForecaster(num=arg.num, date_1=arg.date_1, date_2=arg.date_2)
    weather_machine.do_stuff()
