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
quarantining = True #true or false
contact_tracing = True #true or false
initial_infected_fraction = 0.00
initial_removed_fraction = 0.05
incubation_period = 5.2 #used in discretized gamma
serial_interval = 5.8 #used in discretized gamma
symptomatic_fraction = 0.25
recovery_days = 14
quarantine_days = 14
days_indetectable = 3
R0 = 5.8
contact_rate = 19 #validation
npi_factor = 0.25

daily_outside_cases = [1,0,0,0] #this needs to be a vector the way the code is written; 1,0,0,0 corresponds to 1/4 (see paper)
contact_tracing_testing_rate = 1.0
contact_tracing_quarantine_rate = 1.0
contact_tracing_days = 2
daily_testing_fraction = 0.03
fpr = 0.001 #false positive rate of daily testing
fnr = 0.03 #false negative rate of daily testing
incubation_picker = probtools.DiscreteGammaFull(incubation_period,4) #discrete Gamma for generating incubation period for each case
serial_interval_distribution = probtools.DiscreteGammaFull(serial_interval,4).densities #infectiousness is a function of time since infection (discrete Gamma)

days = 213 #days simulation runs MUST MATCH days reported in  data.csv

#########WORLD PARAMETERS#############
students    = 20000
instructors =  2500
classes     =  3750
departments =   120
meeting_schedules = [[1,3],[1,3],[0,2,4],[0,2,4],[0,2]]

class_cohorts = 8

maximum_section_size = 150 #for each section
friendship_contacts = 4.0 #thes following contribute to Poisson process for contact (see paper appendix)
academic_contacts = 4.0
broad_social_contacts = 2.0
department_environmental_contacts = 4.0
broad_environmental_contacts = 4.0
residential_neighbors=1.0

online_transition = 30
residential_rate = 1
social_distancing = True

crowd_reduction_factor = 1.0
activity_reduction_factor = 1.0
recitation_rules = [50,20,80] #Classes over 50 have recitations of 20, with 80 student max PER TA
#class percentages
class_size_200 = 0.0075 #percentage of classes over the size of 200 people
class_size_100 = 0.0225 #percentage of classes from 100-199
class_size_50 = 0.07 #percentage of classes from 50-99
class_size_40 = 0.04 #percentage of classes from 40-49
class_size_30 = 0.1 #percentage of classes from 30-39
class_size_20 = 0.28 #percentage of classes from 20-29
class_size_10 = 0.31 #percentage of classes from 10-19
class_size_2 = 0.18 #percentage of classes from 2-9

in_class_base_rate = 0.0145 #these are used in worldbuilder2 to define contact rates; don't mess with
in_dept_base_rate =  0.116
in_frnd_base_rate_hi = 0.18
in_frnd_base_rate_low = in_frnd_base_rate_hi * 0.25
in_dept_broad_base_rate = 0.00158


#_poisson_computer = probtools.Poisson()
#typical_R0 = 4.0
#typical_contacts_per_day = 10.2
#incubation_period = lambda : _poisson_computer.draw(5.2)
#poisson = _poisson_computer.draw
