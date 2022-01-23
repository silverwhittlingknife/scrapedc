
import datetime
import re
import requests
import typing

import bs4
import sqlite3

class DateNotFound(ValueError): pass
#class is a keyword defining a class of objects
#there’s gonna be a class of things called “DateNotFound”
#hey’re all going to be ValueErrors. 
#after a colon, Python expects a command, 
#so you can write “pass” to avoid getting a syntax error
#this is defining the class, but not actually doing anything with the class 
#(“some subset of ValueErrors are DateNotFound errors”)
#the POINT is to distinguish errors in the PROGRAM from errors from not getting the date


dayMonthYearRE = re.compile('''(?:\| Day[ \t\r\f]*= (\d{1,2})[ \t\r\f]*(?:.*)?)?
\| (?:Pubm|M)onth[ \t\r\f]*= (\w+)?[ \t\r\f]*
\| (?:Puby|Y)ear[ \t\r\f]*= (\d\d\d\d)[ \t\r\f]*
''')

Writer1_1RE = re.compile('''\| Writer1_1[ \t\r\f]*= (.*)
''')

# ''' means python string that will break across multiple lines
# day line wasn't always present which is why it's all in (?:)? bc ? means optional and ?: means not a group
# \| means ACTUAL pipe not the special meaning (bc it's in the dcwiki document)

#usually A|B has a special meaning so the \ is to indicate it's a special character
#compile takes a string that's a regular expression & it makes it easier to use by re
#this will be used to match raw data dates from the html later & "recognize" them as dates

#the () around (\d{1,2}) mean "this is a group, save this & give it to me later"
#in this case it's group 1, day --> Day is either 1 digit or 2 digits
#(?:) means this is NOT a group, don't give it back

# square brackets [] are regular ex. notation that means there's going to be exactly one of these things (I don't know which one)
# [ \t\r\f] means that we're looking for a single character that's EITHER " " OR \t OR \r OR \f]
# this is for handling whitespace
# \t means tab
# \r means carriage return
# \f means form-feed
#  \w means "any letter OR any digit OR an underscore"
#  .  means "all of that PLUS special characters (> < etc.)" (but not new lines)


#"*" means 0 or more of them (applies to previous thing)
#"+" means 1 or more of them

#EXPLANATION OF ?
#? means "whatever came pre-? is either present or not present"
#a?b means it could be "b or it could be "ab" but ONLY for a single character
#you MIGHT have "Month" or you might have "Pubmonth"
#?: means "I'm putting this in parentheses" BUT it's NOT a group
#(?:Pubm|M) means "Pubm" or "M"

#(?:.*)?
#     (    )?   means might exist or not
#      ?:       means do not make a group
#         .*    means unlimited number of any kind of character EXCEPT a new line
# technically since you have a .* here you don't need the rest
# (.*) is the same as (.*)? because * can also be nothing

#this is a list of sample strings to test to make sure that the regular expression is working properly
# if matchObj with Day = 7 doesn't return 7 for group one, then regex is NOT working!!!


matchObj = Writer1_1RE.search('''| Editor1_1           = Elisabeth V. Gehrlein
| Editor1_2           = Jeanine Schaefer
| Editor1_3           = Peter Tomasi
| Editor1_4           = Mike Marts
| Writer1_1           = Adam Beechen
| Penciler1_1         = Freddie E. Williams II
''')
if matchObj.group(1) != 'Adam Beechen':
  raise Exception(matchObj.group(1))

matchObj = dayMonthYearRE.search('''| Issue               = 5
| Day                 = 7
| Month               = 12
| Year                = 2009
''')
if matchObj.group(1) != '7':
  raise Exception(matchObj.group(1))
assert int(matchObj.group(1)) == 7

matchObj = dayMonthYearRE.search('''| Issue               = 1
| Month               = October
| Year                = 2007
''')
assert matchObj.group(1) is None
assert int(matchObj.group(3)) == 2007

matchObj = dayMonthYearRE.search('''| Issue               = 1
| Month               = June 
| Year                = 2007
''')
assert matchObj
assert matchObj.group(1) is None
assert int(matchObj.group(3)) == 2007
assert matchObj.group(2) == 'June'
assert datetime.datetime.strptime(matchObj.group(2), '%B').month == 6

assert int(re.match('''Day[ \t\r\f]*= (\d{1,2})[ \t\r\f]*(?:.*)?''', 'Day                 = 29 <!-- http://www.mikesamazingworld.com/mikes/features/comic.php?comicid=4340 -->').group(1)) == 29

matchObj = dayMonthYearRE.search('''| Issue               = 1
| Day                 = 29 <!-- http://www.mikesamazingworld.com/mikes/features/comic.php?comicid=4340 -->
| Pubmonth            = May
| Pubyear             = 1997
| Year                = 1997
''')
assert matchObj
assert int(matchObj.group(1)) == 29
assert datetime.datetime.strptime(matchObj.group(2), '%B').month == 5
assert int(matchObj.group(3)) == 1997

#the file has three functions which are defined with "def"
#getDate (capitalization matters), getBookNames, and getBookDates
#sublimetext puts them in teal when they're being defined but blue when they're being used
#this program runs getBookNames first, then getBookDates (getDate is run within getBookDates)

#underscores is a variable that we're ASSIGNING and comicName is the variable we received
#so underscores is a comic name with any spaces replaced with underscores

#.format means replace {} with the thing inside ()
#and responses runs the package "requests" which has a function called "get"
#this isn't a normal python function which is why you have to use "requests"

#responses --> might be the page it requested, or some kind of error
#"response" is HTTP (how you request webpages, 404 errors, Amazon)
#"content" is HTML (the book that Amazon delivers)

#BeautifulSoup is a package/command that looks at html and parses it
# textarea = soup.find('textarea') is looking for the html tag that says "textarea"
#(this works bc their page has only one textarea in the html)
#textarea.string is the text that's inside the text area (title, image, writer, etc.)
# "search" and "find" mean the same thing but "find" is BeautifulSoup and "search" is re

#dayMonthYearRE.search searches for a substring in the text that matches the re expression
#group is what the RE package calls a sub-regular expression

#if afdsafdsa is true, do this; ELSE (if it's false) do this

def getTextareaString(comicName: str):
  underscores = comicName.replace(' ', '_')
  url = 'https://dc.fandom.com/wiki/{}?action=edit'.format(underscores)
  response = requests.get(url)
  soup = bs4.BeautifulSoup(response.content)
  textarea = soup.find('textarea')
  if textarea is None:
    raise DateNotFound(comicName, url)
  return textarea.string

def extractDateFromTextarea(textareastring: str):
  matchObj = dayMonthYearRE.search(textareastring)
  if matchObj is None:
    raise DateNotFound(comicName + 'Failed to find datetime regular expresison in ' + DCDBcomicTemplate)
  if matchObj.group(1) is None:
    day = None
  else:
    day = int(matchObj.group(1))
  year = int(matchObj.group(3))
  if matchObj.group(2) is None:
    month = None
  else:
    if matchObj.group(2) == 'Winter':
      month = 1
    elif matchObj.group(2) == 'Spring':
      month = 4
    elif matchObj.group(2) == 'Summer':
      month = 7
    elif matchObj.group(2) == 'Fall':
      month = 10
    elif matchObj.group(2) == 'Holiday':
      month = 12
    else:
      try:
        month = int(matchObj.group(2))
      except ValueError:
        try:
          month = datetime.datetime.strptime(matchObj.group(2), '%B').month
        except ValueError:
          month = datetime.datetime.strptime(matchObj.group(2), '%b').month
  # Since we do not always have the day, we cannot make a date.
  return (year, month, day)

def getDate(comicName: str):
  DCDBcomicTemplate = getTextareaString(comicName)
  return extractDateFromTextarea(DCDBcomicTemplate)

def getAuthor(comicName: str):
  DCDBcomicTemplate = getTextareaString(comicName)
  return extractAuthorFromTextarea(DCDBcomicTemplate)

#this is the code that was supposed to get the comic names from the sqlite database
#def getBookNames(DBpath: str = 'comics.sqlite'):
  #conn = sqlite3.connect(DBpath)
  #curs = conn.cursor()
  #curs.execute('''SELECT DISTINCT name FROM BookNames;''')
  #return [row[0] for row in curs.fetchall()]

#the new code for getBookNames gets it from allcomics.txt instead
#allcomics.txt is not in python [] list format
#so the command line.strip etc. takes allcomics.txt and turns it into python list format

def getBookNames(DBpath: str = 'comics.sqlite'):
  return [line.strip() for line in open('allcomics.txt')]

def putBookDatesInCursor(curs: sqlite3.Cursor, bookNames: typing.List[str]):
  for name in bookNames:
    if 'novel' in name or name == 'Batman: Fear Itself': continue
    try:
      year, month, day = getDate(name)
    except DateNotFound:
      print('No date found for ' + name)
      continue
    # print(name, year, month, day)
    curs.execute('''INSERT INTO Book VALUES (?, ?, ?, ?, ?)''', (name, name, year, month, day))

def putAuthorsInCursor(curs: sqlite3.Cursor):
  for name in bookNames:
    if 'novel' in name or name == 'Batman: Fear Itself': continue
    try:
      author = getAuthor(name)
    curs.execute('''INSERT INTO BookHasAuthor VALUES (?, ?)''', (name, author))

def openDBandDoSomething(DBpath: str = 'comics.sqlite', doSomething: typing.Callable[[sqlite.Cursor], None]):
  conn = sqlite3.connect(DBpath)
  curs: sqlite3.Cursor = conn.cursor()
  doSomething(curs)
  curs.close()
  conn.commit()
  conn.close()

def getBookDates(DBpath: str = 'comics.sqlite'):
  bookNames = getBookNames(DBpath)
  conn = sqlite3.connect(DBpath)
  curs: sqlite3.Cursor = conn.cursor()
  putBookDatesInCursor(curs, bookNames)
  curs.close()
  conn.commit()
  conn.close()

def getBookAuthors(DBpath: str = 'comics.sqlite'):
  bookNames = getBookNames(DBpath)
  conn = sqlite3.connect(DBpath)
  curs: sqlite3.Cursor = conn.cursor()
  putAuthorsInCursor(curs, bookNames)
  curs.close()
  conn.commit()
  conn.close()

# print(getDate('Batman and Robin Vol 1 5'))
# getBookDates()

#after you run this file there will be a table in the sqlite comics.sqlite database
#the table is called Book and it has all the dates in it


