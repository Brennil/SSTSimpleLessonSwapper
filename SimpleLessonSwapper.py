import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
import csv
from collections import defaultdict
import random
import time

st.title("Simple Lesson Swapper (Working Title)")

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']

credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"],scopes = scope)

gc = gspread.authorize(credentials)
    
db = dict()

def open_db(filename):
    spread = gc.open(filename)
    worksheet = spread.worksheet("2024T1") #CHANGE THIS WHEN CHANGING TERM DATABASES!!!
    csvdb = worksheet.get_all_values()
    
    db['Monday'] = defaultdict()
    db['Tuesday'] = defaultdict()
    db['Wednesday'] = defaultdict()
    db['Thursday'] = defaultdict()
    db['Friday'] = defaultdict()
    for row in csvdb:
        temprow = row[2:]
        while "" in temprow:
            temprow.remove("")
        if row[0] == "":
            break
        db[row[0]][int(row[1])] = temprow

def open_class_db(filename):
    spread = gc.open(filename)
    worksheet = spread.worksheet("Sheet2") #CHANGE THIS WHEN CHANGING TERM DATABASES!!!
    csvdb = worksheet.get_all_values()
    teacherdb = {}
    for row in csvdb:
        temprow = row[1:]
        while "" in temprow:
            temprow.remove("")
        if row[0] == "":
            break
        teacherdb[row[0]] = temprow
    return teacherdb
    
def availableper(teacher):
    teachfree = dict()
    for day in db.keys():
        teachfree[day] = []
        for per in db[day].keys():
            if teacher in db[day][per]:
                teachfree[day].append(per)
    return teachfree

def sublist(lst1, lst2):
    ls1 = [element for element in lst1 if element in lst2]
    ls2 = [element for element in lst2 if element in lst1]
    return ls1 == ls2
    
timings = {
        1: ['8:00', '8:20'],
        2: ['8:20', '8:40'],
        3: ['8:40', '9:00'],
        4: ['9:00', '9:20'],
        5: ['9:20', '9:40'],
        6: ['9:40', '10:00'],
        7: ['10:00', '10:20'],
        8: ['10:20', '10:40'],
        9: ['10:40', '11:00'],
        10: ['11:00', '11:20'],
        11: ['11:20', '11:40'],
        12: ['11:40', '12:00'],
        13: ['12:00', '12:20'],
        14: ['12:20', '12:40'],
        15: ['12:40', '13:00'],
        16: ['13:00', '13:20'],
        17: ['13:20', '13:40'],
        18: ['13:40', '14:00'],
        19: ['14:00', '14:20'],
        20: ['14:20', '14:40'],
        21: ['14:40', '15:00'],
        22: ['15:00', '15:20'],
        23: ['15:20', '15:40'],
        24: ['15:40', '16:00'],
        25: ['16:00', '16:20'],
        26: ['16:20', '16:40'],
        27: ['16:40', '17:00'],
        28: ['17:00', '17:20'],
        29: ['17:20', '17:40'],
        30: ['17:40', '18:00'],
        31: ['18:00', '18:20']}

def time_converter(all_avail):
    cols = []
    headers = []
    all_avail_times = {}
    for key in all_avail.keys():
        all_avail_times[key] = []
        for period in all_avail[key]:
            all_avail_times[key].append(timings[int(period)])
        i = 0
        while True:
            current = all_avail_times[key]
            while i < len(current)-1 and current[i][1] == current[i+1][0]:
                current[i][1] = current[i+1][1]
                current.remove(current[i+1])
            i += 1
            if i >= len(current)-1:
                all_avail_times[key] = current
                col = []
                headers.append(key)
                for time in current:
                    col.append("{} - {}".format(time[0],time[1]))
                cols.append(col)
                break

    longest = max([len(x) for x in cols])
    for col in cols:
        while len(col) < longest:
            col.append("")
        
    df = pd.DataFrame(zip(*cols), columns = headers)
    
    # style
    th_props = [
    ('font-size', '14px'),
    ('text-align', 'center'),
    ('font-weight', 'bold'),
    ('color', '#6d6d6d'),
    ('background-color', '#f7ffff')
    ]
                               
    td_props = [
    ('font-size', '14px')
    ]
                                 
    styles = [
    dict(selector="th", props=th_props),
    dict(selector="td", props=td_props)
    ]

    # table
    df2=df.style.set_properties().set_table_styles(styles)
    
    # CSS to inject contained in a string
    hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """
    
    # Inject CSS with Markdown
    st.markdown(hide_table_row_index, unsafe_allow_html=True)
    
    # Display a static table
    st.table(df2)

teachers = gc.open('TeacherList')
worksheet = teachers.worksheet("Sheet1")
teachers_list = [x[0] for x in worksheet.get_all_values()]
class_list = ['S1-01','S1-02','S1-03','S1-04','S1-05','S1-06','S1-07','S1-08','S1-09','S1-10',
              'S2-01','S2-02','S2-03','S2-04','S2-05','S2-06','S2-07','S2-08','S2-09','S2-10',
              'S3-01','S3-02','S3-03','S3-04','S3-05','S3-06','S3-07','S3-08','S3-09',
              'S4-01','S4-02','S4-03','S4-04','S4-05','S4-06','S4-07','S4-08','S4-09']
time_list = ['8:00','8:20','8:40','9:00','9:20','9:40','10:00','10:20','10:40','11:00','11:20','11:40',
             '12:00','12:20','12:40','13:00','13:20','13:40','14:00','14:20','14:40','15:00','15:20','15:40',
             '16:00','16:20','16:40','17:00','17:20','17:40','18:00','18:20']

'''
### Enter Lesson to Swap

'''
class_toswap = st.selectbox("Select a class...", class_list)
day = st.selectbox("Select the lesson day...", ["Odd Monday", "Odd Tuesday", "Odd Wednesday", "Odd Thursday", "Odd Friday", "Even Monday", "Even Tuesday", "Even Wednesday", "Even Thursday", "Even Friday"])
lesson_start = st.selectbox("Select the lesson start time...", time_list)
lesson_end = st.selectbox("Select the lesson end time...", time_list)
lesson_period_start = [key for key in timings.keys() if timings[key][0] == lesson_start]
lesson_period_end = [key for key in timings.keys() if timings[key][1] == lesson_end]

teacherdb = open_class_db('TeacherList')
teachers_free = []
teachers_class_free = []
other_teachers = []

if st.button("Click me to see who is free!"):
    while lesson_period_end <= lesson_period_start: 
        st.write("Error! Please ensure that your lesson end time is after your lesson start time!")
    lesson_period = lesson_period_start + lesson_period_end
    while lesson_period[0] + 1 != lesson_period[1]:
        lesson_period.insert(1, lesson_period[1] - 1)
    exp = 0
    while True:
        try:
            if day[0] == "O": open_db('TeacherAvailDatabase_ODD')
            elif day[0] == "E": open_db('TeacherAvailDatabase_EVEN')
            break
        except:
            if 2**exp > 120: 
                st.write("Sorry, we are having issues connecting to our database. Please try again later.")
                st.stop()
            else:
                st.write("Error connecting to database... We will try again in {} seconds...".format(2**exp))
                waittime = 2**exp + random.random()/100
                time.sleep(waittime)
                exp += 1
    for teach in teachers_list:
        x = availableper(teach)
        if sublist(lesson_period, x[day.split()[1]]):
            st.write(teach)
            if teach in teacherdb.keys() and class_toswap in teacherdb[teach]:
                teachers_class_free.append(teach)
            else:
                teachers_free.append(teach)
        elif teach in teacherdb.keys() and class_toswap in teacherdb[teach]:
            other_teachers.append(teach)

'''
### Results
'''

st.write("Teachers who are available during your lesson and teach the class:")
st.write(teachers_class_free)

if st.button("I may need a multi-way swap..."):
    st.write("Teachers who are available during your lesson but DO NOT teach the class :")
    st.write(teachers_free)
