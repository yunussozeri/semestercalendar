
from pdfreader import SimplePDFViewer
import os

os.chdir("//Users/yunussozeri/Desktop/takvimke")

# read pdf file
page = open("BWI3.pdf","rb")
viewer = SimplePDFViewer(page)

# get content from pdf

for canvas in viewer:
     page_strings = canvas.strings
     
    
# remove header
items = page_strings[18::]
print(items)

# clean data, fix parsing errors such as single digits sliding 
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
     fach_desc['beginn'] = fach[0]
     fach_desc['end'] = fach[2]
     fach_desc['dozent'] = fach[1]
     fach_desc['raum'] = fach[4]
     fach_desc['kalenderwochen'] = fach[5]
     fach_dict[fach[3]] = fach_desc


for fach,infos in fach_dict.items():
     print(f'Fach: {fach} \n -----\n Infos: {infos}\n ~~~~~')
     
print('------------------------')

     


#print(help(page))


