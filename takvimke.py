
from pdfreader import SimplePDFViewer
import os
from ics import Event, Calendar
from datetime import time, datetime
from isoweek import Week
import pytz

os.chdir("//Users/yunussozeri/Desktop/takvimke")

# read pdf file
page = open("BWI3.pdf","rb")
viewer = SimplePDFViewer(page)

# get content from pdf

for canvas in viewer:
     page_strings = canvas.strings
     
# remove headers and unnecessary information
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
         fach_desc['beginn'] = fach[0]
         fach_desc['dozent'] = fach[1]
         fach_desc['end'] = fach[2]
         fach_desc['kursname'] = (str)(fach[3]).replace('BWI3-','')
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

# add my courses to my_courses
add_course('SEA1'); add_course('BWL3') ;add_course('BWLP3') ;add_course('AD') ;add_course('ADP/03') ;add_course('SEAP1/03') ;add_course('WI2') ;add_course('WIP2/04')

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

     return tuple(nums) #return a tuple for ease of iteration and immutability

def convert_string_kalenderwochen_to_inttuples():
     for course,info in my_courses.items():
          kalenderwochen = list()
          kalenderwochen.append(info['kalenderwochen'])
          for wochen in kalenderwochen:
               info['kalenderwochen'] = str_to_intlist(wochen)

convert_string_kalenderwochen_to_inttuples()

def str_to_isotime(string:str):
     splitted = string.split(':')
     hours, minutes  = splitted[0],splitted[1]
     return str(time(int(hours),int(minutes)))

def dict_to_event(dictionary:dict) -> list:
    events = []
    for course, info in my_courses.items():
         event = Event()
         event.name = info['kursname']
         event.location = info['raum']
         event.organizer = info['dozent']
         
         for w in kw:
          if w > 52:
               w = w - 52
               date =get_day_from_weeknr( 2024, w, day)
          else: 
               date = get_day_from_weeknr( year, w, day)
               event.begin = date + " " + str_to_isotime(info['beginn'])
               event.end =  date + " " + str_to_isotime(info['end'])
         events.append(event)

def get_day_from_weeknr(year:int = 2023 , weeknr: int = None, day:str = None) -> str:
     date = Week(year,weeknr)

     if day == 'Mo':
          date = date.monday()
     elif day == 'Di':
          date = date.tuesday()
     elif day == 'Mi':
          date = date.wednesday()
     elif day == 'Do':
          date = date.thursday()
     elif day == 'Fr':
          date = date.friday()
     else:
          raise " Not implemented"
     
     return str(date)


calendar = Calendar()
timezone = pytz.timezone('Europe/Berlin')
format = '%Y-%m-%d %H:%M:%S'

for course, infos in my_courses.items():
     
     year =  2023

     kw = infos['kalenderwochen']
     day = infos['day-of-week']

     begin = str_to_isotime(infos['beginn'])
     end = str_to_isotime(infos['end'])

     dozent = infos['dozent']
     location = infos['raum']

     for w in kw:
          event = Event()
          if w > 52:
               w = w - 52
               date =get_day_from_weeknr( 2024, w, day)
          else: 
               date = get_day_from_weeknr( year, w, day)
          
          event.name = course
          event.begin = timezone.localize(datetime.strptime(date + " " + begin,format))
          event.end = timezone.localize(datetime.strptime(date + " " + end, format))
          event.organizer = dozent
          event.location = location

          calendar.events.add(event)
          
#print(help(calendar))
with open("caltest.ics", "w") as f: f.writelines(calendar)

'TODO: Terminal app and selection menu'



