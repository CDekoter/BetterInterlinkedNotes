# Notes Manager

# B.I.N.
# Better
# Interlinked
# Notes
# Verbalized B - I - N, lady

# from tkinter import *

import tkinter as tk

from tkinter import messagebox

import csv

import xml.etree.ElementTree as ET

# todo - be able to delete elements
# todo - be able to expand the canvas during use, will shrink to minimum size after closing + buffer
# todo - figure out if deleting elements and having a hanging id will be a problem...

def drag_start(event):

    if c_cont.type('current') != 'line':
    
        drag['x'], drag['y'] = event.x, event.y  # Return the current position of the element

    
def drag_motion(event):

    curr_ID = 0

    if c_cont.type('current') == 'rectangle':

        curr_ID = labels_dict[c_cont.itemcget('current', 'tags').split(' current')[0]]  # Return the canvas ID of the text

    elif c_cont.type('current') == 'text':

        curr_ID = labels_dict[c_cont.itemcget('current', 'text')]  
   
    x = c_cont.coords(curr_ID)[0] - drag['x'] + event.x # Current position, new cursor position
    y = c_cont.coords(curr_ID)[1] - drag['y'] + event.y

    r = c_cont.coords(rects_dict[c_cont.itemcget(curr_ID, 'text')])

    r[0] += -drag['x'] + event.x  # Update rectangle coordinates
    r[2] += -drag['x'] + event.x
    r[1] += -drag['y'] + event.y
    r[3] += -drag['y'] + event.y

    drag['x'] = event.x
    drag['y'] = event.y
    
    c_cont.coords(curr_ID, [x, y])  # Anchor is 'center'
    
    c_cont.coords(rects_dict[c_cont.itemcget(curr_ID, 'text')], r)

    if c_cont.itemcget(curr_ID, 'text') in lines_dict_2.keys():
        for end_i, end in enumerate(lines_dict_2[c_cont.itemcget(curr_ID, 'text')]):  # first point, send point

            for e in end:  # For each line that has an end

                if not end_i:
                    x_f, y_f = c_cont.coords(e)[2], c_cont.coords(e)[3]
                    #print([x, y, x_f, y_f])
                    c_cont.coords(e, [x, y, x_f, y_f])
                else:
                    x_f, y_f = c_cont.coords(e)[0], c_cont.coords(e)[1]
                    #print([x_f, y_f, x, y])
                    c_cont.coords(e, [x_f, y_f, x, y])
                

def resolve_name(name):  # Returns the ID of a note based on the name and context # hmmmmm
    pass

def escape_xpath(s):
    # Thanks to Elias Dorneles, may not work for some double quote scenarios
    if '"' in s and "'" in s:
        return 'concat(%s)' % ", '\"',".join('"%s"' % x for x in s.split('"'))
    elif '"' in s:
        return "'%s'" % s
    return '"%s"' % s

def on_closing():
    if messagebox.askokcancel("Quit and save positions", "Cancel to exit without saving positions"):
        save_pos()
        window.destroy()
    else:
        window.destroy()


def save_pos():

    for key in types_s:

        for et in root.findall(key):

            et_name = et.find('Name').text
            et.set('x', str(int(c_cont.coords(labels_dict[et_name])[0])))
            et.set('y', str(int(c_cont.coords(labels_dict[et_name])[1])))
            et.set('szx', str(int(c_cont.coords(rects_dict[et_name])[2]
                              - c_cont.coords(rects_dict[et_name])[0])))
            et.set('szy', str(int(c_cont.coords(rects_dict[et_name])[3]
                              - c_cont.coords(rects_dict[et_name])[1])))

    tree.write(xmlfile)

def show_info(event):
    
    if c_cont.type('current') != 'line':
        in_name_text.set(c_cont.itemcget('current', 'tags').split(' current')[0])
        find_data("<Button-3>")

def find_data(event):
    
    if in_name_text.get() != 'Enter a Name' and in_name_text.get() != '':

        if in_name_text.get() in labels_dict.keys():  # If the element already exists populate the current data

            element = root.find(".//*[Name="+escape_xpath(in_name.get())+"]")
                                     
            in_ID_text.set(element.attrib['ID'])
            in_source_text.set(element.find('Source').text)
            in_author_text.set(element.find('Author').text)
            in_type_text.set(element.tag)
            # Name set by user during search
            temp = ''
            for t in element.findall('Tag'):
                if t.text:
                    temp += '#'+t.text+'\n'
                    
            in_tags.replace('1.0', 'end', temp)

            temp = ''
            for l in element.findall('Link'):
                if l.attrib['LT']:
                    temp += l.attrib['LT'] + ' : ' + l.attrib['BTWN'] + '\n'

            in_links.replace('1.0', 'end', temp)

            in_header_text.set(element.find('Description').text)
            in_para.replace('1.0', 'end', element.find('Paragraph').text)
        
        else:

            in_ID_text.set(f'{int(root.attrib["n"])+1:05}')  # Set to the next ID
            in_source_text.set('Report of the Warren Commision')
            in_author_text.set('Bantam Books')
            in_type_text.set('')
            # Name is set
            in_tags.delete('1.0', 'end')
            in_links.delete('1.0', 'end')
            in_header_text.set('Short Description')
            in_para.delete('1.0', 'end')
            

    else:
        print('Enter a name')

def save_data(event):

    if messagebox.askokcancel('Overwrite Data', 'Cancel'):
        
        if in_name_text.get() in labels_dict.keys():
            element = root.find(".//*[Name="+escape_xpath(in_name.get())+"]")
        # Check to make sure that the ID matches the name

            if element.attrib['ID'] != in_ID_text.get():
                messagebox.showerror('Name doesn\'t match ID\nSearch Again')

            element.find('Source').text = in_source_text.get()  # Overwrite! 
            element.find('Author').text = in_author_text.get()
            # Don't change the name
            
            temp = in_tags.get('1.0', 'end').lstrip('#').rstrip('\n\n').split('\n#')
            for old in element.findall('Tag'):
                element.remove(old)
            for t in temp:
                ET.SubElement(element, 'Tag').text = t

            temp = in_links.get('1.0', 'end').rstrip('\n').split('\n')

            for old in element.findall('Link'):
                element.remove(old)

            if temp != ['']:
                for l in temp:
                    l = l.split(' : ')
                    ET.SubElement(element, 'Link', attrib={'LT':l[0], 'BTWN':l[1]})

            element.find('Description').text = in_header_text.get()

            element.find('Paragraph').text = in_para.get('1.0', 'end')

        else:

            root.set('n', in_ID_text.get()) # Update the current length of the ID list
            
            element = ET.SubElement(root, in_type_text.get(), attrib={'ID':in_ID_text.get(),
                                                                      'x':'200', 'y':'200',
                                                                      'szx':'150', 'szy':'50'})

            ET.SubElement(element, 'Source').text = in_source_text.get()  # Overwrite! 
            ET.SubElement(element, 'Author').text = in_author_text.get()
            ET.SubElement(element, 'Name').text = in_name_text.get()
            
            temp = in_tags.get('1.0', 'end').lstrip('#').rstrip('\n\n').split('\n#')
            for t in temp:
                ET.SubElement(element, 'Tag').text = t

            temp = in_links.get('1.0', 'end').rstrip('\n').split('\n')
            if temp != ['']:
                for l in temp:
                    l = l.split(' : ')
                    ET.SubElement(element, 'Link', attrib={'LT':l[0], 'BTWN':l[1]})

            ET.SubElement(element, 'Description').text = in_header_text.get()

            ET.SubElement(element, 'Paragraph').text = in_para.get('1.0', 'end')
                    
        tree.write(xmlfile)
        
        print('Saved Data: ' + in_ID_text.get())
    else:
        print('No Data Saved')

def update_labels(event):

    for key in types_s:

        for et in root.findall(key):

            et_name = et.find('Name').text # Grabs the name of the element

            et_tags = et.findall('Tag')

            # Compare list of selected tags with list of tags on element
            
            for lk in et.findall('Link'):

                if [et_name, lk.attrib['BTWN']] not in list(lines_dict.values()):
                    # print('    Link: ' + et_name + ' - ' + lk.attrib['BTWN'])
                    x1 = int(et.attrib['x'])
                    y1 = int(et.attrib['y'])
                    
                    if lk.attrib['LT'] in link_c.keys():
                        lk_c = link_c[lk.attrib['LT']]
                    else:
                        lk_c = 'black'

                    if lk.attrib['LT'] in link_l.keys():
                        lk_l = link_l[lk.attrib['LT']]
                    else:
                        lk_l = None
    
                    lk_temp = root.find(".//*[Name="+escape_xpath(lk.attrib['BTWN'])+"]")
                    x2 = int(lk_temp.attrib['x'])
                    y2 = int(lk_temp.attrib['y'])
                    lines.append(c_cont.create_line(x1, y1, x2, y2, width=2, fill=lk_c, dash=lk_l, tag='line'))
                    lines_dict[lines[-1]] = [et_name, lk.attrib['BTWN']]
                    
                    if et_name in lines_dict_2.keys():
                        lines_dict_2[et_name][0].append(lines[-1])
                    else:
                        lines_dict_2[et_name] = [[lines[-1]], []]

                    if lk.attrib['BTWN'] in lines_dict_2.keys():
                        lines_dict_2[lk.attrib['BTWN']][1].append(lines[-1])
                    else:
                        lines_dict_2[lk.attrib['BTWN']] = [[], [lines[-1]]]
                    
                    c_cont.tag_lower('line')

            if et_name not in labels_dict.keys():
                print('Label: ' + et_name)
                
                rects_dict[et_name] = c_cont.create_rectangle(int(et.attrib['x']) + int(int(et.attrib['szx'])/2),
                                               int(et.attrib['y']) + int(int(et.attrib['szy'])/2),
                                               int(et.attrib['x']) - int(int(et.attrib['szx'])/2),
                                               int(et.attrib['y']) - int(int(et.attrib['szy'])/2),
                                               fill=types_c[key], tags=et_name)  # Add the name to the tag for show_info

                c_cont.tag_bind(rects_dict[et_name], "<Button-1>", drag_start)
                c_cont.tag_bind(rects_dict[et_name], "<B1-Motion>", drag_motion)
                c_cont.tag_bind(rects_dict[et_name], "<Button-3>", show_info)

                labels_dict[et_name] = c_cont.create_text(int(et.attrib['x']), int(et.attrib['y']), text=et_name,
                                                          fill='white', width=120, justify=tk.CENTER,
                                                          tags=et_name)

                c_cont.tag_bind(labels_dict[et_name], "<Button-1>", drag_start)
                c_cont.tag_bind(labels_dict[et_name], "<B1-Motion>", drag_motion)
                c_cont.tag_bind(labels_dict[et_name], "<Button-3>", show_info)

    c_cont.tag_lower('line')

def delete_note(event):

    if messagebox.askokcancel('Delete Note?', 'Cancel'):

        if in_name_text.get() in labels_dict.keys():
            element = root.find(".//*[Name="+escape_xpath(in_name.get())+"]")

        e2del = element.find('Name').text  # Element to delete

        # Remove element graphic elements from dictionaries
        
        # Get the current note shown in the "Note Info" window

        # labels_dict = {}  # List of labels and associated elements
        # lines = []  # List of line objects
        for k in lines_dict.keys():
            if e2del in lines_dict[k]:  # Key Line Number
                c_cont.delete(lines_dict[e2del])  # Delete line element
                del lines_dict[k]  # Delete the line entry that tracks the
                
        c_cont.delete(rects_dict[e2del])  # Delete rectangle entities
        del rects_dict[e2del]

        c_cont.delete(labels_dict[e2del])
        del labels_dict[e2del]

        if e2del in lines_dict_2.keys():
            del lines_dict_2[element.find('Name').text]  # Dictionary that tracks lines
        # All lines have been deleted already
        
        # Use the root.remove(child) method to delete the info in the xml tree
        root.remove(element)  # Remove the xml tree node

        in_ID_text.set('')
        in_source_text.set('')
        in_author_text.set('')
        in_name_text.set('Enter a Name')
        in_type_text.set('Type')
        in_tags.replace('1.0', 'end', '')
        in_links.replace('1.0', 'end', '')
        in_header_text.set('')
        in_para.replace('1.0', 'end', '')
        filt_tags_text.set('')

        print('Removed ' + e2del)  # Print the result of the deleting action
    

def filter_labels(event):

    # Get list of active tags from text box
    tag_list = filt_tags_text.get()  # Return the list of values from the tag entry form

    if tag_list:
        
        tag_list = tag_list.lstrip('#').split(' #')
        
       
        k_show_list = []  # List of visible labels

        for k in labels_dict.keys():

            # Get a list of tags associated with the key

            k_tags = root.find(".//*[Name="+escape_xpath(k)+"]").findall('Tag')  # Return the relevant element
           
            k_show = any(kk.text in tag_list for kk in k_tags)


            if k_show:
                k_show_list.append(k)  # List of names of labels to make visible

            if c_cont.itemcget(labels_dict[k], 'state') != tk.HIDDEN and not k_show: # If the text should not be shown and is
                c_cont.itemconfigure(labels_dict[k], state=tk.HIDDEN)
                
            elif not c_cont.itemcget(labels_dict[k], 'state') != tk.HIDDEN and k_show:  # If the text should be shown and isn't
                c_cont.itemconfigure(labels_dict[k], state=tk.NORMAL)

            if c_cont.itemcget(rects_dict[k], 'state') != tk.HIDDEN and not k_show: # If the rect should not be shown and is
                c_cont.itemconfigure(rects_dict[k], state=tk.HIDDEN)
                
            elif not c_cont.itemcget(rects_dict[k], 'state') != tk.HIDDEN and k_show:  # If the rect should be shown and isn't
                c_cont.itemconfigure(rects_dict[k], state=tk.NORMAL)
            
        for el in lines_dict.keys():

            if lines_dict[el][0] in k_show_list and lines_dict[el][1] in k_show_list:
                c_cont.itemconfigure(el, state='normal')

            else:
                c_cont.itemconfigure(el, state='hidden')

        print('Filtered Tags: ', tag_list)
                
    else:

        for k in list(labels_dict.items()):
            
            c_cont.itemconfigure(k[1], state=tk.NORMAL)
            c_cont.itemconfigure(rects_dict[k[0]], state=tk.NORMAL)

        for line in lines_dict:

            c_cont.itemconfigure(line, state='normal')
        
        print('Cleared filters')


def scroll(event, widget):
    widget.yview_scroll(int(-1 * (event.delta / 120)), "units")


def final_scroll(event, widget, func):
    widget.bind_all("<MouseWheel>", func)


def stop_scroll(event, widget):
    widget.unbind_all("<MouseWheel>")
        
# Dictionaries of Types, Shapes and Colors
types_s = {'character': 'circle',
           'location': 'square',
           'organization': 'triangle'}

types_c = {'character': 'blue',
           'location': 'green',
           'organization': 'red'}

link_l = {'Acquaintance': (6,6),
          'Telephone': (10, 4),
          'Contact': (10, 4),
          'Alleged': (2, 4)} # Change this according to the tkinter line types

link_c = {'Killed' : 'red',
          'Attacked' : 'red',
          'Target' : 'red',
          'Location' : 'green',
          'Business' : 'blue'}

          
# Read XML File

path = {'tcol49' : r'C:\Users\Calvin\Documents\California\Notes\notes\note_TheCryingOfLot49.xml',
        'rwc' : r'C:\Users\Calvin\Documents\California\Notes\notes\note_rwc.xml',
        'mhd' : r'C:\Users\Calvin\Documents\California\Notes\notes\note_MulhollandDrive.xml',
        'bm' : r'4'}

xmlfile = path[input('Select a note: ')]  # Input the shorthand for the file
tree = ET.parse(xmlfile)

root = tree.getroot()

labels_dict = {}  # List of labels and associated elements
lines = []  # List of line objects
lines_dict = {}  # Key Line Number
rects_dict = {}
lines_dict_2 = {} # Updated method to track lines

drag = {'ID':0, 'x':0, 'y':0}

window = tk.Tk(screenName='B.I.N.')  # Creates a top level window

c_cont = tk.Canvas(window, bg='lightgrey')  # Create the canvas where draggable elements live

Scroll_H = tk.Scrollbar(window)
Scroll_V = tk.Scrollbar(window)

c_cont.config(xscrollcommand=Scroll_H.set, yscrollcommand=Scroll_V.set, highlightthickness=0)  # Attach commands

Scroll_H.config(orient=tk.HORIZONTAL, command=c_cont.xview)
Scroll_V.config(orient=tk.VERTICAL, command=c_cont.yview)

c_cont.grid(column=0, row=0, sticky='nsew')  # Canvas in the top left
window.columnconfigure(0, weight=1)  # Expand the canvas as needed to fill the window
window.rowconfigure(0, weight=1)

Scroll_H.grid(column=0, row=1, sticky='ew')  # fill=tk.X, side=tk.BOTTOM, expand=tk.FALSE)
Scroll_V.grid(column=1, row=0, sticky='ns')  # fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)



c_cont.update_idletasks()

c_cont.config(scrollregion=(0, 0, 3000, 1600))  # todo make this scale to limits of current graph



# Character Name # Search
# If character name exists, load all existing data

# ID        in_ID_text
# Source    in_source_text
# Author    in_author_text
# Name      in_name_text    Search
# Tags      text (multiline?)
# Links     text (multiline, space separated)
# Header    in_header_text
# Paragraph text

rc = 0
px = 5
py = 5

f_cont = tk.Frame(window, bg='lightgrey')
f_cont.grid(row=0, rowspan=2, column=2, sticky='nsew')
window.columnconfigure(2, minsize=500)

# Grid method to add note tools
title = tk.Label(f_cont, text='Note Info', bg='darkgrey', fg='white')
title.grid(row=0, column=0, columnspan=3, sticky='ew', padx=px, pady=py)
f_cont.columnconfigure(0, weight=1)

f_cont.columnconfigure(1, weight=1)
f_cont.columnconfigure(2, weight=2)

rc += 1  # Increment the row count

in_ID_Label = tk.Label(f_cont, bg='darkgrey', text='ID#: ')
in_ID_Label.grid(row=rc, column=0, sticky='ew', padx=px, pady=py)
in_ID_text = tk.StringVar()
in_ID = tk.Label(f_cont, bg='white', textvariable=in_ID_text)  # Load the ID or generate a new sequential one
in_ID.grid(row=1, column=1, sticky='ew', padx=px, pady=py)
rc += 1

in_source_Label = tk.Label(f_cont, bg='darkgrey', text='Source: ')
in_source_Label.grid(row=rc, column=0, sticky='ew', padx=px, pady=py)
in_source_text = tk.StringVar()
in_source = tk.Entry(f_cont, textvariable=in_source_text)  # Load the source of the element
in_source.grid(row=rc, column=1, columnspan=2, sticky='ew', padx=px, pady=py)
rc += 1

in_author_Label = tk.Label(f_cont, bg='darkgrey', text='Author: ')
in_author_Label.grid(row=rc, column=0, sticky='ew', padx=px, pady=py)
in_author_text = tk.StringVar()
in_author = tk.Entry(f_cont, textvariable=in_author_text)  # Load the author of the source
in_author.grid(row=rc, column=1, columnspan=2, sticky='ew', padx=px, pady=py)
rc+= 1

in_name_Label = tk.Label(f_cont, bg='darkgrey', text='Name: ')
in_name_Label.grid(row=rc, column=1, sticky='ew', padx=px, pady=py)
in_name_text = tk.StringVar()
in_name_text.set('Enter a Name')
in_name = tk.Entry(f_cont, textvariable=in_name_text)  # Load the character name or allow a search for a new one
in_name.grid(row=rc, column=2, sticky='ew', padx=px, pady=py)

in_search = tk.Label(f_cont, text='Search', bg='darkgrey', fg='white')
in_search.grid(row=rc, column=0, sticky='ew', padx=px, pady=py)
in_search.bind("<Button-1>", find_data)
rc += 1

in_type_Label = tk.Label(f_cont, bg='darkgrey', text='Type: ')
in_type_Label.grid(row=rc, column=0, sticky='ew', padx=px, pady=py)
in_type_text = tk.StringVar()
in_type_text.set('Type')
in_type = tk.Entry(f_cont, textvariable=in_type_text)  # Load the character name or allow a search for a new one
in_type.grid(row=rc, column=1, columnspan=2, sticky='ew', padx=px, pady=py)
rc += 1

in_tags_Label = tk.Label(f_cont, bg='darkgrey', text='Tags: ', height=3)
in_tags_Label.grid(row=rc, column=0, sticky='ew', padx=px, pady=py)
in_tags = tk.Text(f_cont, wrap=tk.WORD, width=1, height=3)  # Display list of tags associated with the character in list form
in_tags.grid(row=rc, column=1, columnspan=2, sticky='ew', padx=px, pady=py)
rc += 1

in_links_Label = tk.Label(f_cont, bg='darkgrey', text='Links: ', height=5)
in_links_Label.grid(row=rc, column=0, sticky='ew', padx=px, pady=py)
in_links = tk.Text(f_cont, wrap=tk.WORD, height=5, width=1)  # Display list of tags associated with the character in list form
in_links.grid(row=rc, column=1, columnspan=2, sticky='ew', padx=px, pady=py)
rc += 1

in_header_Label = tk.Label(f_cont, bg='darkgrey', text='Description: ')
in_header_Label.grid(row=rc, column=0, sticky='ew', padx=px, pady=py)
in_header_text = tk.StringVar()
in_header_text.set('Short Description')
in_header = tk.Entry(f_cont, textvariable=in_header_text)  # Load the character name or allow a search for a new one
in_header.grid(row=rc, column=1, columnspan=2, sticky='ew', padx=px, pady=py)    
rc += 1

in_para_Label = tk.Label(f_cont, bg='darkgrey', text='Notes: ')
in_para_Label.grid(row=rc, column=0, columnspan=3, sticky='ew', padx=px, pady=py)
rc += 1
in_para = tk.Text(f_cont, wrap=tk.WORD, width=1, height=1)  # Display paragraph written about character, fill space
in_para.grid(row=rc, column=0, columnspan=3, sticky='nsew', padx=px, pady=py)
f_cont.rowconfigure(rc, weight=1)  # This cell should have a weight of 1, all others zero
rc += 1

tags_filter = tk.Label(f_cont, text='Filter by Tag (#<tag> #<tag>)', bg='darkgrey', fg='black')
tags_filter.grid(row=rc, column=0, columnspan=2, sticky='ew', padx=px, pady=py)
tags_filter.bind("<Button-1>", filter_labels)
filt_tags_text = tk.StringVar()
filt_tags = tk.Entry(f_cont, textvariable=filt_tags_text)  # Load the character name or allow a search for a new one
filt_tags.grid(row=rc, column=2, sticky='ew', padx=px, pady=py)
rc += 1

in_save = tk.Label(f_cont, text='Save Data', bg='darkgrey', fg='black')
in_save.grid(row=rc, column=0, sticky='ew', padx=px, pady=py)
in_save.bind("<Button-1>", save_data)

in_update_labels = tk.Label(f_cont, text='Update Notes', bg='darkgrey', fg='black')
in_update_labels.grid(row=rc, column=1, sticky='ew', padx=px, pady=py)
in_update_labels.bind("<Button-1>", update_labels)

in_delete_labels = tk.Label(f_cont, text='Delete Note', bg='darkgrey', fg='black')
in_delete_labels.grid(row=rc, column=2, sticky='ew', padx=px, pady=py)
in_delete_labels.bind("<Button-1>", delete_note)


window.geometry('2000x1000')
window.title('B.I.N.')

window.protocol("WM_DELETE_WINDOW", on_closing)

#frame.bind('<Configure>', lambda event, canvas=canvas: onFrameConfigure(canvas))

update_labels("<Button-1>")

window.mainloop()
