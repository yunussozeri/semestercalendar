
from pdfreader import SimplePDFViewer
import os

from ics import Event, Calendar
import datetime
from dateutil.rrule import rrulestr





os.chdir("//Users/yunussozeri/Desktop/takvimke")

# read pdf file
page = open("BWI3.pdf","rb")
viewer = SimplePDFViewer(page)

# get content from pdf

for canvas in viewer:
     page_strings = canvas.strings
     
    
# remove header
items = page_strings[18::]


# clean data, fix parsing errors such as single digits sliding 
index = 0
new_items = []

def clean_list(items:list = items) -> list:
     index = 0
     new_items = []
     while index < len(items):
          curr_item = items[index]
          
          #if the next element is single digit, append to previous and save into list
          if(len(items[index+1]) == 1):
               list_of_match = [curr_item,items[index+1]]
               matched = ''.join(list_of_match)

               items.remove(items[index+1])
               new_items.append(matched)

          else:
               # else, add to list
               new_items.append(curr_item)
          # BWL3 is remote, so add keine Raum

          if(curr_item == 'BWI3-BWL3' or curr_item == 'BWI3-BWLP3' ): new_items.append('KEINE RAUM')

          #increment index
          index = index +1

     return new_items

raw_fach_info = clean_list()

# group module information

def group_fach_info(raw_info)-> list:

     index = 0
     faecher = []
     while index < len(raw_fach_info):
          fach = raw_fach_info[index:index+6:]
          faecher.append(fach)
          index += 6
     return faecher

faecher = group_fach_info(raw_fach_info)

# reorganize module information

def map_courses() -> dict:
    fach_dict = dict()
    for fach in faecher:
         fach_desc = dict()
         fach_desc['kursname'] = (str)(fach[3]).replace('BWI3-','')
         fach_desc['beginn'] = fach[0]
         fach_desc['end'] = fach[2]
         fach_desc['dozent'] = fach[1]
         fach_desc['raum'] = fach[4]
         fach_desc['kalenderwochen'] = fach[5]
         fach_dict[fach[3]] = fach_desc
    return fach_dict

fach_dict = map_courses()

my_courses = dict()
def add_course(course_abr):
     for key in fach_dict.keys():
          if course_abr in key:
               my_courses[course_abr] = fach_dict.get(key)
               return

add_course('BWL3')
add_course('BWLP3')
add_course('AD')
add_course('ADP/03')
add_course('SEA1')
add_course('SEAP1/03')
add_course('WI2')
add_course('WIP2/04')

def add_days_of_week():

     for name, info in my_courses.items():
          if 'BWL' in name:
               info['day-of-week'] = 'Mi'

          if 'AD' in name:
               info['day-of-week'] = 'Do'

          if 'SEA1' in name:
               info['day-of-week'] = 'Di'

          if 'SEAP1' in name:
               info['day-of-week'] = 'Do'

          if 'WI' in name:
               info['day-of-week'] = 'Fr'
     return
     
add_days_of_week()     

reqs = list()
for info in my_courses.values():
     req = [info['kursname'],info['day-of-week'],info['kalenderwochen']]
     reqs.append(req)

def extract_intervals():
     for req in reqs:
          #remove commas from the week numbers
          req[2] = req[2].split(', ')
          for weeks in req[2]:
               # count the number of pairs in the form "##-##" and replace them with pair lists
               count = 0
               if '-' in weeks:
                    req[2].append(weeks.split('-'))
                    count += 1
               req[2] = req[2][count::]
         # print(req)
          
data = [['BWL3', 'Mi', [['42', '43'], ['45', '51'], ['54', '57']]],
        ['BWLP3', 'Mi', [['42', '43'], ['45', '51'], ['54', '57']]],
        ['AD', 'Do', [['42', '51'], ['54', '56']]],
        ['ADP/03', 'Do', ['45', '48', '51', '56']],
        ['SEA1', 'Di', [['42', '43'], ['45', '51'], ['54', '57']]],
        ['SEAP1/03', 'Do', ['46', '49', '54', '57']],
        ['WI2', 'Fr', [['42', '51'], ['54', '57']]],
        ['WIP2/04', 'Fr', ['44', '46', '48', '50', '54', '56']]]

def expand_intervals(data):
    result = []
    for item in data:
        if len(item) == 3 and isinstance(item[2], list):
            expanded_intervals = []
            for interval in item[2]:
                if isinstance(interval, list):
                    start, end = int(interval[0]), int(interval[1])
                    expanded_intervals.extend(list(range(start, end + 1)))
                else:
                    expanded_intervals.append(int(interval))
            item[2] = expanded_intervals
        result.append(item)
    return result

expanded_data = expand_intervals(data)

def str_to_intlist(string: str) -> tuple:
     comma_splitted = string.split(',')
     nums = []
     if '-' not in string: ## if no intervals, just convert the list to int 
          for numstr in comma_splitted:
               nums.append(int(numstr))
          
     else: ## otherwise, get the individual intervals, remove the strings so that you only have the list
          for index,strinterval in enumerate(comma_splitted):
              comma_splitted[index] = strinterval.split('-')

          for interval in comma_splitted:
               start, end = int(interval[0]), int(interval[1])
               nums.extend(list(range(start, end + 1)))

     return tuple(nums)
          
for course,info in my_courses.items():
     kalenderwochen = list()
     kalenderwochen.append(info['kalenderwochen'])
     for wochen in kalenderwochen:
          info['kalenderwochen'] = str_to_intlist(wochen)
     print(course, info['kalenderwochen'])




# append 2023-W in front of all week numbers to get convert them into date time conform format
def format_week_numbers():    
    for req in reqs:
         prefix23 = '2023-W'
         prefix24 = '2024-W'
         for i,weeks in enumerate(req[2]):
              if isinstance(weeks,str):
                   if(int)(weeks) > 52:
                        w = (int)(weeks)
                        diff = w - 52
                        week = prefix24+(str)(diff)
                        req[2][i] = week
                   else:
                        weeks = prefix23+weeks
                        req[2][i] = weeks
              
              elif isinstance(weeks,list):
                   for j,week in enumerate(weeks):
                        # if week number larger than 52, calculate the recess in the next year and reformat with next years literal
                        if(int)(week) > 52:
                             w = (int)(week)
                             diff = w - 52
                             week = prefix24+(str)(diff)
                             req[2][i][j] = week
                        else: 
                             week = prefix23+week
                             req[2][i][j] = week

#date_format = "%Y-W%W"



from ics import Event, Calendar
from datetime import time
from isoweek import Week
#events = []
def dater(start:time,end:time,day:str,name:str,place:str,holder:str,weeks:list):
     events = []
     start_time = start
     end_time = end
     day_of_week = day
     event_name = name
     event_place = place
     event_holder = holder
     weeks_of_year = weeks

     for week in weeks_of_year:
          if isinstance(week, list):
               start_week, end_week = week
               for current_week in range(int(start_week.split('-W')[1]), int(end_week.split('-W')[1]) + 1):
                   year = int(start_week.split('-W')[0])
                   current_date = Week(year, current_week).monday()
                   if day_of_week != "Mo":
                        current_date = Week(year, current_week).tuesday()
                   start_date = current_date.replace(hour=start_time.hour, minute=start_time.minute)
                   end_date = current_date.replace(hour=end_time.hour, minute=end_time.minute)
       
                   event = Event()
                   event.name = event_name
                   event.begin = start_date
                   event.end = end_date
                   event.location = event_place
                   event.organizer = event_holder
       
                   # Create the recurrence rule for each week
                   recurrence_rule = f" RRULE:FREQ=WEEKLY;COUNT=10;WKST=SU;BYDAY=MO,FR"
                   event.rrule = rrulestr("""RRULE:FREQ=WEEKLY;INTERVAL=10;COUNT=5;WKST=SU;BYDAY=MO,FR""")
       
                   events.append(event)
          else:
              start_week = week
              year = int(start_week.split('-W')[0])
              current_date = Week(year, int(start_week.split('-W')[1])).thursday()
              start_date = datetime.combine(current_date, start_time)
              end_date = datetime.combine(current_date, end_time)
          
              event = Event()
              event.name = event_name
              event.begin = start_date
              event.end = end_date
              event.location = event_place
              event.organizer = event_holder
          

              # Create the recurrence rule for the single week event
              recurrence_rule =  rrulestr("FREQ=DAILY;INTERVAL=10;COUNT=5")
              event.rrule = rrulestr("FREQ=WEEKLY;INTERVAL=10;COUNT=5")
          
              print(event)
              events.append(event)
     
# Define the event information
event_holder = "DENEMEKE"
start_time = time(8, 15)
end_time = time(11, 30)
day_of_week = "MO"
event_name = "DENEME EVENTI"
event_place = "DENEME MEKANI"
#weeks_of_year = ["2023-W43", ["2023-W44", "2024-W2"], "2024-W9"]

# Create a list to store individual events
#dater(start_time,end_time,day_of_week,event_name,event_place,event_holder,weeks_of_year)
#dater(time(9, 30),time(11, 15),"TU","Test event","test event location","test event holder",weeks_of_year)


# Create a Calendar and add all events to it
#calendar = Calendar()
#calendar.events.update(events)
# Print the events as an .ics file
#print(calendar)

#with open("my_calendar.ics", "w") as f: f.writelines(calendar)



