
from pdfreader import SimplePDFViewer
import os
import pprint as pp
from ics import Calendar
import datetime as dt
from dateutil import relativedelta as rd




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

new_items = clean_list()
#while index < len(items):
#     curr_item = items[index]
#     #if the next element is single digit, append to previous and save into list
#     if(len(items[index+1]) == 1):
#          list_of_match = [curr_item,items[index+1]]
#          matched = ''.join(list_of_match)
#          
#          items.remove(items[index+1])
#          new_items.append(matched)
#          
#     else:
#          # else, add to list
#          new_items.append(curr_item)
#     # BWL3 is remote, so add keine Raum
#
#     if(curr_item == 'BWI3-BWL3' or curr_item == 'BWI3-BWLP3' ): new_items.append('KEINE RAUM')
#
#     #increment index
#     index = index +1
#          
#     
# group module information
index = 0
faecher = []
while index < len(new_items):
     fach = new_items[index:index+6:]
     faecher.append(fach)
     index += 6


# reorganize module information
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


#for fach,infos in fach_dict.items():
     #print(f'Fach: {fach} \n -----\n Infos: {infos}\n ~~~~~')
#     
#print('------------------------')

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

#for name,info in my_courses.items():
 #    print(f"{name} findet am {info['day-of-week']} vom {info['beginn']} bis {info['end']} in {info['raum']} von {info['dozent']} während Kalenderwochen {info['kalenderwochen']} statt.")

calender = Calendar()

# Convert year and week number into a date
#date_string = "2023-W42"
#date_format = "%Y-W%W"
#date = datetime.datetime.strptime(date_string, date_format)
#
# Add 6 days to get the last day of the week
#
#end_date = date + dateutil.relativedelta.relativedelta(days=6)
#
#event = ics.Event()
#event.name = "My Event"
#event.begin = date
#event.end = end_date
reqs = list()
for info in my_courses.values():
     req = [info['kursname'],info['day-of-week'],info['kalenderwochen']]
     reqs.append(req)

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

for req in reqs:
     for i,weeks in enumerate(req[2]):
          if isinstance(weeks,str):
               weeks = '2023-W'+weeks
               req[2][i] = weeks
          elif isinstance(weeks,list):
               for j,week in enumerate(weeks):
                    week = '2023-W'+week
                    req[2][i][j] = week
     print(req)
