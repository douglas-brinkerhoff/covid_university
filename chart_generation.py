from matplotlib import pyplot
import pandas


def show_total_active_cases(run_number):
    model_series = pandas.read_csv('timeSeries%s.csv' % run_number, index_col="Day",
                                   usecols=['Day', 'Infected'])
    actual_series = pandas.read_csv('data_actives.csv')
    pyplot.plot(model_series, label='Predicted')
    pyplot.plot(actual_series, label='Actual')
    pyplot.legend()
    pyplot.xlabel("Day")
    pyplot.ylabel("Active Cases")
    pyplot.title("Daily Number of Active COVID-19 Cases at UMT")
    pyplot.show()


def show_total_num_tests(run_number):
    model_series = pandas.read_csv('timeSeries%s.csv' % run_number, index_col="Day", usecols=['Day', 'Tests Today']).cumsum()
    actual_series = pandas.read_csv('data_total_tests.csv').cumsum()
    pyplot.plot(model_series, label='Predicted')
    pyplot.plot(actual_series, label='Actual')
    pyplot.legend()
    pyplot.xlabel("Day")
    pyplot.ylabel("Number of  Tests Administered")
    pyplot.title("Total Number of COVID19 Tests Administered at UMT (Includes Negatives)")
    pyplot.show()


def show_total_pos_tests(run_number):
    model_series = pandas.read_csv('timeSeries%s.csv' % run_number, index_col="Day", usecols=['Day', 'Pos. Tests Today']).cumsum()
    actual_series = pandas.read_csv('data_positives.csv').cumsum()
    pyplot.plot(model_series, label = 'Predicted')
    pyplot.plot(actual_series, label = 'Actual')
    pyplot.legend()
    pyplot.xlabel("Day")
    pyplot.ylabel("Number of Positive Tests")
    pyplot.title("Total Number of Positive COVID19 Tests at UMT")
    pyplot.show()


def show_daily_pos_tests(run_number):
    model_series = pandas.read_csv('timeSeries%s.csv' % run_number, index_col="Day", usecols=['Day','Pos. Tests Today'])
    actual_series = pandas.read_csv('data_positives.csv')
    pyplot.plot(model_series, label = 'Predicted')
    pyplot.plot(actual_series, label = 'Actual')
    pyplot.legend()
    pyplot.xlabel("Day")
    pyplot.ylabel("Number of Positive Tests")
    pyplot.title("Daily Number of Positive COVID19 Tests at UMT")
    pyplot.show()


def show_daily_total_tests(run_number):
    model_series = pandas.read_csv('timeSeries%s.csv' % run_number, index_col="Day", usecols=['Day', 'Tests Today'])
    actual_series = pandas.read_csv('data_total_tests.csv')
    pyplot.plot(model_series, label='Predicted')
    pyplot.plot(actual_series, label='Actual')
    pyplot.legend()
    pyplot.xlabel("Day")
    pyplot.ylabel("Number of  Tests Administered")
    pyplot.title("Daily Number of  COVID19 Tests at UMT")
    pyplot.show()