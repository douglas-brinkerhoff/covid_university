#    pandemic.py : Simulates COVID-19 Transmission in a University Setting
#    Copyright (C) 2020 Philip T. Gressman <gresssman@math.upenn.edu> and Jennifer R. Peck <jpeck1@swarthmore.edu>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License.
#ness for each infected individual.The Gamma distribution is widely used in connectioness for each infected individual.The Gamma distribution is widely used in connection with COVIDmodeling [18] for these parameters; wn with COVIDmodeling [18] for these parameters; w
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.


import time,os,sys
import probtools,random
import universal
import worldbuilder2 as worldbuilder
import gather2 as gather

import csv
import pandas
from matplotlib import pyplot

# track MSE across multiple runs on target variables
diff_pos_tests_all_runs = []
diff_tot_tests_all_runs = []


class FiFoQueue(object):
    # Adds item in a first-in, first-out queue
    # Items are not allowed to be on the list more than once at a time
    # Existing entries block the addition of duplicates
    def __init__(self):
        self.order_dictionary = {}
        self.item_order = {}
        self.last = None
        self.lastno = -1
        self.firstno = 0
        self.fixed_endpoint = -1
    def reset(self):
        self.order_dictionary = {}
        self.item_order = {}
        self.last = None
        self.lastno = -1
        self.firstno = 0
        self.fixed_endpoint = -1
    def add(self,item,*,abort_if=None):
        if item in self.item_order or (abort_if is not None and item in abort_if):
            return False
        self.lastno += 1
        self.order_dictionary[self.lastno] = item
        self.item_order[item] = self.lastno
        return True
    def retrieve(self):
        if self.firstno > self.lastno:
            return None
        result = self.order_dictionary[self.firstno]
        del self.item_order[result]
        del self.order_dictionary[self.firstno]
        self.firstno += 1
        return result
    def __iter__(self):
        self.fixed_endpoint = self.lastno
        return self
    def __next__(self):
        if self.firstno <= self.fixed_endpoint:
            return self.retrieve()
        else:
            raise StopIteration
    def length(self):
        return self.lastno - self.firstno + 1


class Disease(object):
    """
    Primary class for simulating pandemic
    """
    def get_parameter(self,parameter,default):
        """
        Return parameter value if specified        
        """
        value = default
        if parameter in self.user_specified_options:
            value = self.user_specified_options[parameter]
        if '_applied' not in self.user_specified_options:
            self.user_specified_options['_applied'] = {'version' : self.version}
        self.user_specified_options['_applied'][parameter] = value
        return value

    def parameter_audit(self):
        """
        Ensures that all parameters are specified
        """
        should_raise = self.get_parameter('parameter_checking',True)
        must_raise = False
        message = 'Unknown parameters: '
        for key in self.user_specified_options:
            if key != '_applied' and key not in self.user_specified_options['_applied']:
                print("Unknown parameter",key)
                if should_raise:
                    must_raise = True
                    message += key + ' '
        print(self.user_specified_options['_applied'])
        if must_raise:
            raise Exception(message)

    def __init__(self,optionsdict={}):
        self.version = '2020-06-25-github'
        self.user_specified_options = optionsdict

        # Parameter - whether a quarantine procedure is in place
        self.quarantining = self.get_parameter('quarantining',True)

        # Parameter - whether contact tracing is in place
        self.contact_tracing = self.get_parameter('contact_tracing',True)

        # Parameter - fraction of population that is initially infected
        self.initial_infected_fraction = self.get_parameter('initial_infected_fraction',0.00)

        # Parameter - fraction of population that is initially immune
        self.initial_removed_fraction = self.get_parameter('initial_removed_fraction',0.05)

        # ?
        self.removed_cohorts = self.get_parameter('removed_cohorts',[])

        # Parameter - mean incubation perion
        self.incubation_period = self.get_parameter('incubation_period',5.2)

        # Parameter - Mean serial interval
        self.serial_interval = self.get_parameter('serial_interval',5.8)

        # Parameter - fraction of cases that are symptomatic
        self.symptomatic_fraction = self.get_parameter('symptomatic_fraction',0.25)

        # Number of days from infection to recovery
        self.recovery_days = 14

        # Number of days spent before being released from quarantine
        self.quarantine_days = 14

        # Days after infection in which diseased state cannot be detected by tests
        self.days_indetectable = 3

        # Basic reproduction number : this is used to parameterize contact transmission probability
        self.R0 = self.get_parameter('R0',3.8)

        # Average contact rate ??
        self.contact_rate = self.get_parameter('contact_rate',19)

        # Transmission probability reduction from using masks
        self.npi_factor = self.get_parameter('npi_factor',0.5)

        # Number of outside cases to occur per day
        self.daily_outside_cases = self.get_parameter('daily_outside_cases',[1,0,0,0])

        # Number of traced contacts who can be tested
        self.contact_tracing_testing_rate = self.get_parameter('contact_tracing_testing_rate',1.0)

        # Number of traced contacts who get quarantined
        self.contact_tracing_quarantine_rate = self.get_parameter('contact_tracing_quarantine_rate',1.0)

        # Number of days it takes to complete contact tracing
        self.contact_tracing_days = self.get_parameter('contact_tracing_days',2)

        # Surveillance testing rate
        self.daily_testing_fraction = self.get_parameter('daily_testing_fraction',0.03)

        # False positive rate
        self.daily_testing_false_positive = self.get_parameter('daily_testing_false_positive',0.001)

        # False negative rate
        self.daily_testing_false_negative = self.get_parameter('daily_testing_false_negative',0.030)

        # Create a list of all the people in the University (student plus instructors)
        self.people = universal.students + universal.instructors
        
        # Create discrete gamma distributions for incubation time and serial interval with means given
        # by parameters defined above, and k=4
        self.incubation_picker = probtools.DiscreteGammaFull(self.incubation_period,4)
        self.serial_interval_distribution = probtools.DiscreteGammaFull(self.serial_interval,4).densities

        # This just shows the marginal probability of pre-symptomatic transmission.  Doesn't affect 
        # anything else
        result = 0
        for index1 in range(14):
            for index2 in range(14):
                if index1 < index2:
                    result += self.serial_interval_distribution[index1] * self.incubation_picker.densities[index2]
        print('+++++ Presymptomatic Transmission:',result)

        # This part is pretty confusing.  So they start out by modelling serial interval as a 
        # discretized gamma distribution with mean 5.8 (days) and k = 4.  This provides a probability
        # distribution over length of time between contracting the virus and *potentially* transmitting
        # it to someone else.  They then argue that an individual's transmission probability is 
        # proportional to this distribution, i.e. a person't transmission probability is highest
        # at the most likely serial interval.  They then normalize the resulting transmission 
        # probabilities so that given a certain number of contacts (self.contact_rate), the expected 
        # reproduction rate is R0 (i.e. if you simulate 19 contacts per day, with transmission
        # probability given by self.serial_interval_distribution[day], then add up the total number
        # of people infected over all days, then the expected value of that number is R0).  This is confused by
        # the presence of npi_factor here, which simply reduces the transmission probabilities.  The 
        # factor of 2.0 comes from the fact that the R0 that they like to use (3.8) is computed from
        # a circumstance in which npi_factor is already estimated to be 0.5, so they divide it out.  
        # Very stupid hard-coded thing, and we should change it, but I leave it here for consistency.
        for index in range(len(self.serial_interval_distribution)):
            myval = self.serial_interval_distribution[index] * self.R0 * 2.0 / self.contact_rate * self.npi_factor
            if myval > 1.0:
                Exception('contact_rate is incompatibly small for given R0')
            # After these reassignments, self.serial_interval_distribution is no longer 
            # actually serial interval, but rather transmission probabilities as a function of days since infection.  
            self.serial_interval_distribution[index] = myval

        # I'm not sure how this computes the attack rate, but it doesn't affect anything else.
        probsympt = 1.0
        probasympt = 1.0
        for prob in self.serial_interval_distribution:
            probsympt *= (1-1.6*prob)
            probasympt *= (1-0.8*prob)
        probsympt = 1- probsympt
        probasympt = 1-probasympt
        print('+++++ Attack Rate: ',probasympt + (probsympt - probasympt) * self.symptomatic_fraction)

        # Initialize a special data structure that acts as a hybrid between a queue and a set (a 
        # queue with no duplicates).
        self.testing_queue = FiFoQueue()
        self.contact_tracing_queue = FiFoQueue()

        # Get the worldbuilder and generate a random population
        self.registrar = worldbuilder.University(optionsdict)
        self.registrar.generate()

        self.recorded_info = {}
        self.recorder = worldbuilder.HistoryRecord()

        self.reset(False)
        self.scenario_name = self.get_parameter('scenario_name','')
        self.test = self.get_parameter('test',False)
        self.run_days = self.get_parameter('run_days',universal.days)
        self.filename = self.get_parameter('filename','(automatic)')
        if self.filename == '(automatic)':
            self.filename = str(int(time.time()))
        self.parameter_audit()
        self.recorder.information = self.user_specified_options['_applied']

    def reset(self,regenerate=True):
        """
        Reset the simulation (for multiple runs)
        """
        self.recorder.reset(regenerate)
        self.testing_queue.reset()
        self.contact_tracing_queue.reset()

        self.day = 0
        self.recorded_info = {'day' : self.day}
        if regenerate:
            self.registrar.generate()
            self.contact_generator = self.registrar.contact_process

        self.all_individuals = {}
        self.person_state = {}
        self.susceptible = {}
        self.infected = {}
        self.infection_start_date = {}
        self.symptomatic_infecteds = {}
        self.symptomatic_day = {}
        self.infection_detectable_day = {}
        self.infection_end_day = {}
        self.infection_transmissions = {}
        self.removed = {}
        self.quarantined = {}
        self.quarantine_start_day = {}
        self.quarantine_end_day = {}
        self.recorded_info = {}
        self.completed_infections = 0
        self.average_transmissions = 0

        for person in range(self.people):
            action = probtools.random_threshold({'removed' : self.initial_removed_fraction, 'infected' : self.initial_infected_fraction})
            if 'infected' in action:
                self.event('new person',person,infected=True)
            elif 'removed' in action:
                self.event('new person',person,removed=True)
            else:
                self.event('new person',person)

    def event(self,etype,person,**kwargs):
        if etype == 'quarantined':
            self.quarantined[person] = True
            self.quarantine_end_day[person] = self.quarantine_days + self.day
            self.quarantine_start_day[person] = self.day
            self.registrar.register_departure(person)
            self._record_state_change(person,'quarantined')
            return
        elif etype == 'dequarantined':
            del self.quarantined[person]
            self.registrar.register_return(person)
            self._record_state_change(person,'dequarantined')
            return
        elif etype == 'removed':
            self.removed[person] = True
            if person in self.symptomatic_infecteds:
                del self.symptomatic_infecteds[person]
            del self.infected[person]
            del self.infection_start_date[person]
            if 'artificial' not in kwargs:
                self.average_transmissions *= self.completed_infections
                self.completed_infections += 1
                self.average_transmissions += self.infection_transmissions[person]
                self.average_transmissions /= self.completed_infections
            self._record_state_change(person,'removed')
            return
        elif etype == 'infected':
            del self.susceptible[person]
            self.infected[person] = True
            self.infection_start_date[person] = self.day
            self.infection_detectable_day[person] = self.day + self.days_indetectable
            self.infection_transmissions[person] = 0
            if probtools.random_event(self.symptomatic_fraction):
                self.symptomatic_infecteds[person] = True
                self.symptomatic_day[person] = self.day + self.incubation_picker.draw()
            self.infection_end_day[person] = self.day + self.recovery_days
            self._record_state_change(person,'infected')
            return
        elif etype == 'new person':
            if person in self.registrar.student_data:
                pstring = 'student ' + str(self.registrar.student_data[person]['cohort'])
            else:
                pstring = 'instructor'
            self.susceptible[person] = True
            self.person_state[person] = ('nonquarantined','susceptible',pstring)
            self.all_individuals[person] = True
            self._record_state_change(person,None)
            if 'infected' in kwargs and kwargs['infected'] == True:
                self.event('infected',person,infected_by=None,message='Initially Infected')
            elif 'removed' in kwargs and kwargs['removed'] == True:
                self.event('infected',person,infected_by=None,artificial=True,message='Infection-Pending Initial Removal')
                self.event('removed',person,artificial=True,message='Initially Removed')
            return
        raise Exception('Unknown event',etype)
    def _record_state_change(self,person,change):
        if change is None:
            if self.person_state[person] not in self.recorded_info:
                self.recorded_info[self.person_state[person]] = 0
            self.recorded_info[self.person_state[person]] += 1
        else:
            self.recorded_info[self.person_state[person]] -= 1
            oldstate = self.person_state[person]
            if change == 'quarantined' or change == 'dequarantined':
                self.person_state[person] = (change,oldstate[1],oldstate[2])
            elif change == 'susceptible' or change == 'infected' or change == 'removed':
                self.person_state[person] = (oldstate[0],change,oldstate[2])
            if self.person_state[person] not in self.recorded_info:
                self.recorded_info[self.person_state[person]] = 0
            self.recorded_info[self.person_state[person]] += 1

    def get_test_result(self,person):
        self.tests_performed_today += 1
        dice = random.random()
        if person in self.infected and self.infection_detectable_day[person] <= self.day:
            if dice < self.daily_testing_false_negative:
                return -1   # False Negative Test Result
            self.positive_tests_today += 1
            return 1        # True Positive Test Result
        # Person is either not infected or not yet detectably infected
        if dice < self.daily_testing_false_positive:
            self.positive_tests_today += 1
            return 1 # False Positive Result
        return -1
    def transmission_success(self,person,contact_strength):
        days_infected = self.day - self.infection_start_date[person]
        likelihood = self.serial_interval_distribution[days_infected]
        if person in self.symptomatic_infecteds:
            likelihood *= 1.6
        else:
            likelihood *= 0.8
        return probtools.random_event(1-(1-likelihood)**contact_strength)

    def execute_main_step(self):
        self.day += 1
        self.registrar.update_query_system()
        self.tests_performed_today = 0
        self.contact_traces_performed_today = 0
        self.positive_tests_today = 0

        if self.quarantining:
            for person in self.all_individuals:
                if probtools.random_event(self.daily_testing_fraction):
                    result = self.testing_queue.add(person,abort_if=self.quarantined)
            for person in self.testing_queue:
                test_result = self.get_test_result(person) # Need to change so that all tests are forced
                if test_result > 0 and person not in self.quarantined:
                    self.event('quarantined',person,message='Quarantined on Positive Test Result')
                if test_result > 0 and self.contact_tracing:
                    self.contact_tracing_queue.add(person)
            for person in self.symptomatic_infecteds:
                if self.day == self.symptomatic_day[person]:
                    if person not in self.quarantined:
                        self.event('quarantined',person,message='Quarantined on Reported Symptoms')
                        if self.contact_tracing:
                            self.contact_tracing_queue.add(person)

        to_be_released = {}
        for person in self.quarantined:
            if self.day == self.quarantine_end_day[person]:
                to_be_released[person] = True
        for person in to_be_released:
            self.event('dequarantined',person,message='Released from Quarantine today')
        to_be_removed = {}
        for person in self.infected:
            if self.day == self.infection_end_day[person]:
                to_be_removed[person] = True
        for person in to_be_removed:
            self.event('removed',person,message='Removed from infection')

        if self.contact_tracing:
            for person in self.contact_tracing_queue:
                self.contact_traces_performed_today += 1
                first_trace_day = self.day - self.contact_tracing_days
                post_trace_day = self.day
                if person in self.quarantined:
                    post_trace_day = min(post_trace_day,self.quarantine_start_day[person]+1)
                for trace_day in range(first_trace_day,post_trace_day):
                    identified_contacts = self.registrar.query_contacts(person,trace_day-self.day)
                    for found_individual in identified_contacts:
                        if found_individual in self.all_individuals and found_individual not in self.quarantined:
                            actions = probtools.random_threshold({'test' : self.contact_tracing_testing_rate, 'quarantine' : self.contact_tracing_quarantine_rate})
                            if 'test' in actions:
                                self.testing_queue.add(found_individual,abort_if=self.quarantined)
                            if 'quarantine' in actions and found_individual not in self.quarantined:
                                self.event('quarantined',found_individual,message='Quarantined on Contact Trace')


        to_be_infected = {}
        for person in self.infected:
            if person not in self.quarantined:
                contact_information = self.registrar.query_transmit(person)
                for potential_infected in contact_information:
                    if potential_infected in self.susceptible and potential_infected not in self.quarantined and potential_infected not in to_be_infected and self.transmission_success(person,contact_information[potential_infected]):
                        to_be_infected[potential_infected] = person
                        self.infection_transmissions[person] += 1

        for person in to_be_infected:
            self.event('infected',person,infected_by=to_be_infected[person],message='Infection by transmission')

        new_cases_to_create = self.daily_outside_cases
        if type(new_cases_to_create) == list:
            new_cases_to_create = probtools.list_select(new_cases_to_create)
        for index in range(new_cases_to_create):
            person = probtools.list_select(list(self.susceptible.keys()))
            if person is not None and person not in self.quarantined:
                self.event('infected',person,infected_by=None,message='infected by outside source')

        self.recorded_info['tests_performed_today'] = self.tests_performed_today
        self.recorded_info['contact_traces_performed_today'] = self.contact_traces_performed_today
        self.recorded_info['positive_tests_today'] = self.positive_tests_today
        self.recorded_info['day'] = self.day
        self.recorded_info['R'] = self.average_transmissions
        for key,value in self.registrar.get_attendance().items():
            self.recorded_info[key] = value

    def run(self, number):
        self.recorder.record(self.recorded_info)

        # create CSV containing time series data
        run_number = number + 1
        with open('timeSeries%s.csv' % run_number, 'w', newline='') as series:
            writer = csv.writer(series)
            writer.writerow(['Run', 'Day', 'Pos. Tests Today', 'Positivity Rate', 'Susceptible', 'Infected', 'Removed',
                             'Quarantined', 'Contact Traces Today', 'Tests Today', 'Average Transmissions'])
            for index in range(self.run_days):
                self.execute_main_step()
                # the print statement below came with the code and I have used this as a template to write csv data
                # print('%04i-%03i  S %05i  I %05i  R %05i  Q %05i  CT %05i  TP %05i  R %5.3f' % (number+1,index+1,len(self.susceptible),len(self.infected),len(self.removed),len(self.quarantined),self.contact_traces_performed_today,self.tests_performed_today,self.average_transmissions))
                # John's addition
                writer.writerow([number + 1, index + 1, self.positive_tests_today,
                                 '%8.6f' % (self.positive_tests_today / self.tests_performed_today),
                                 len(self.susceptible), len(self.infected), len(self.removed), len(self.quarantined),
                                 self.contact_traces_performed_today, self.tests_performed_today,
                                 self.average_transmissions])
                self.recorder.record(self.recorded_info)

        # create time series charts using matplotlib

        # NON CUMULATIVE CHARTS:

        # POSITIVE TESTS
        # model_series = pandas.read_csv('timeSeries%s.csv' % run_number, index_col="Day", usecols=['Day','Pos. Tests Today'])
        # actual_series = pandas.read_csv('data_positives.csv')
        # pyplot.plot(model_series, label = 'Predicted')
        # pyplot.plot(actual_series, label = 'Actual')
        # pyplot.legend()
        # pyplot.xlabel("Day")
        # pyplot.ylabel("Number of Positive Tests")
        # pyplot.title("Predicting Number of Positive COVID19 Tests per Day at UMT")
        # pyplot.show()

        # TOTAL TESTS
        # model_series = pandas.read_csv('timeSeries%s.csv' % run_number, index_col="Day", usecols=['Day', 'Tests Today'])
        # actual_series = pandas.read_csv('data_total_tests.csv')
        # pyplot.plot(model_series, label='Predicted')
        # pyplot.plot(actual_series, label='Actual')
        # pyplot.legend()
        # pyplot.xlabel("Day")
        # pyplot.ylabel("Number of  Tests Administered")
        # pyplot.title("Predicting Number of  COVID19 Tests per Day at UMT")
        # pyplot.show()

        #  CUMULATIVE CHARTS:

        # POSITIVE TESTS
        # model_series = pandas.read_csv('timeSeries%s.csv' % run_number, index_col="Day", usecols=['Day', 'Pos. Tests Today']).cumsum()
        # actual_series = pandas.read_csv('data_positives.csv').cumsum()
        # pyplot.plot(model_series, label = 'Predicted')
        # pyplot.plot(actual_series, label = 'Actual')
        # pyplot.legend()
        # pyplot.xlabel("Day")
        # pyplot.ylabel("Number of Positive Tests")
        # pyplot.title("Predicting Number of Positive COVID19 Tests per Day at UMT")
        # pyplot.show()

        # TOTAL TESTS
        # model_series = pandas.read_csv('timeSeries%s.csv' % run_number, index_col="Day", usecols=['Day', 'Tests Today']).cumsum()
        # actual_series = pandas.read_csv('data_total_tests.csv').cumsum()
        # pyplot.plot(model_series, label='Predicted')
        # pyplot.plot(actual_series, label='Actual')
        # pyplot.legend()
        # pyplot.xlabel("Day")
        # pyplot.ylabel("Number of  Tests Administered")
        # pyplot.title("Predicting Number of COVID19 Tests per Day at UMT")
        # pyplot.show()


        # calculate difference between actual and predicted  across all trial runs for positive tests amd total tests
        actual_data_pos_tests = pandas.read_csv('data_positives.csv')
        sum_actual_pos_tests = actual_data_pos_tests.sum()
        actual_data_tot_tests = pandas.read_csv('data_total_tests.csv')
        sum_actual_tot_tests = actual_data_tot_tests.sum()

        run_data = pandas.read_csv('timeSeries%s.csv' % run_number)

        predicted_data_pos_tests = run_data['Pos. Tests Today']
        sum_predicted_pos_tests = predicted_data_pos_tests.sum()
        predicted_data_tot_tests = run_data['Tests Today']
        sum_predicted_tot_tests = predicted_data_tot_tests.sum()

        diff_pos_tests = abs(sum_predicted_pos_tests - sum_actual_pos_tests)
        diff_tot_tests = abs(sum_predicted_tot_tests - sum_actual_tot_tests)

        print('Difference on positive tests for run %i:' % run_number)
        print('%4.2f' % diff_pos_tests)
        diff_pos_tests_all_runs.append(diff_pos_tests)
        print('Difference on total tests for run %i:' % run_number)
        print('%4.2f' % diff_tot_tests)
        diff_tot_tests_all_runs.append(diff_tot_tests)

        print('Difference averaged for positive tests:')
        print('%4.2f' % (sum(diff_pos_tests_all_runs) / len(diff_pos_tests_all_runs)))
        print('Difference averaged for total tests:')
        print('%4.2f' % (sum(diff_tot_tests_all_runs) / len(diff_tot_tests_all_runs)))

    def multiple_runs(self,number):
        output_every = max(int(number / 4),1)
        for runno in range(number):
            try:
                self.run(runno)
            except:
                raise
            if runno != number-1:
                self.reset()
        self.recorder.reset(True)



if __name__ == '__main__':
    print('''pandemic.py  Copyright (C) 2020 Philip T. Gressman and Jennifer R. Peck
This program is distributed under the GNU General Public License Version 3
See <https://www.gnu.org/licenses/gpl-3.0.html>
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.''')
    print('=' * 40)
    print('''This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.''')
    pandemic = Disease({})
    pandemic.multiple_runs(2)

    dc = gather.DataCollector(pandemic)
    dc.register_report('Total Infected',{'susceptible' : False},lambda x: x[-1] - x[0])
    dc.register_report('Peak Quarantined',{'quarantined' : True},lambda x : max(x))
    dc.register_report('Total Student Infections',{'susceptible' : False, 'instructor' : False},lambda x: x[-1] - x[0])
    dc.register_report('Total Instructor Infections',{'susceptible' : False, 'instructor' : True},lambda x: x[-1] - x[0])
    result = dc.generate_csv()

    file = open('mytestout.csv','w')
    file.write(result.output())

    diff_pos_tests_all_runs.clear()  # clear list containing MSE for each run of this trial
    diff_tot_tests_all_runs.clear()