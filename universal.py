#    universal.py : Global Constants for Simulation Scenarios
#    Copyright (C) 2020 Philip T. Gressman <gresssman@math.upenn.edu> and Jennifer R. Peck <jpeck1@swarthmore.edu>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.


import probtools

#pandemic parameters
version = '2020-11-12-github' #date of code version
vaccine = True
quarantining = False #true or false
contact_tracing = True #true or false
initial_infected_fraction = 0.005
initial_removed_fraction = 0.052
incubation_period = 5.2 #used in discretized gamma
serial_interval = 6.599 #used in discretized gamma ad been 5.8
symptomatic_fraction = 0.2
recovery_days = 18
quarantine_days = 11
days_indetectable = 2
R0 = 3.567
contact_rate = 16.759 #validation
npi_factor = 0.621

daily_testing_false_negative = 0.031
daily_testing_false_positive = 0.001
contact_upscale_factor = 1.204

vaccine_effectiveness = 0  # decimal form
vaccine_rate = 0  # integer out of 100 i.e. 10% = 10  50% = 50

daily_outside_cases = [1,0,0,0] #this needs to be a vector the way the code is written; 1,0,0,0 corresponds to 1/4 (see paper)
contact_tracing_testing_rate = 0.902
contact_tracing_quarantine_rate = 1.137
contact_tracing_days = 1  # must be an integer
daily_testing_fraction = 0.00
fpr = 0.001 #false positive rate of daily testing
fnr = 0.03 #false negative rate of daily testing
incubation_picker = probtools.DiscreteGammaFull(incubation_period,4) #discrete Gamma for generating incubation period for each case
serial_interval_distribution = probtools.DiscreteGammaFull(serial_interval,4).densities #infectiousness is a function of time since infection (discrete Gamma)

days = 128 #days simulation runs MUST MATCH days reported in data_positives.csv and data_total_tests.csv

#########WORLD PARAMETERS#############
students    = 10487 #on+off campus; I'm pretty sure this includes Missoula College from the dashboard I've seen
instructors =  880 #includes about 100 TAs and 630 faculty
classes     =  2063 #this is inflated; there are co-convening classes and 105 single person classes I haven't accounted for
departments =   58       #58 departments, but 12 colleges; don't know if this makes a difference
meeting_schedules = [[1,3],[1,3],[0,2,4],[0,2,4],[0,2]] #same

class_cohorts = 8   #same

maximum_section_size = 172.681 #STILL UNSURE ABOUT THIS; I have TA'd for the largest class at UM and the largest section size is 30 so that the TA's only have that many

friendship_contacts = 3.97 #the following contribute to Poisson process for contact (see paper appendix); have not changed this thus far
academic_contacts = 3.379
broad_social_contacts = 1.985
department_environmental_contacts = 4.356
broad_environmental_contacts = 5.331
residential_neighbors= 1.276

online_transition = 80.721
residential_rate = 1
social_distancing = True

crowd_reduction_factor = 1.0
activity_reduction_factor = 1.0
recitation_rules = [50,20,80] #Classes over 50 have recitations of 20, with 80 student max PER TA; this could probably be changed to [50,30,90] from experience

#class percentages
class_size_200 = 0.001 #percentage of classes over the size of 200 people
class_size_100 = 0.016 #percentage of classes from 100-199
class_size_50 = 0.048 #percentage of classes from 50-99
class_size_40 = 0.042 #percentage of classes from 40-49
class_size_30 = 0.082 #percentage of classes from 30-39
class_size_20 = 0.169 #percentage of classes from 20-29
class_size_10 = 0.325 #percentage of classes from 10-19
class_size_2 = 0.266 #percentage of classes from 2-9
#class_size_1 = 0.051 #classes of 1 person; these should probably be combined with class_size_2

in_class_base_rate = 0.0145 #these are used in worldbuilder2 to define contact rates; don't mess with
in_dept_base_rate =  0.116
in_frnd_base_rate_hi = 0.18
in_frnd_base_rate_low = in_frnd_base_rate_hi * 0.25
in_dept_broad_base_rate = 0.00158


#_poisson_computer = probtools.Poisson()
#typical_R0 = 4.0
#typical_contacts_per_day = 10.2
incubation_period = 6.736
#poisson = _poisson_computer.draw
