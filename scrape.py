
import datetime
import re
import requests

import bs4
import sqlite3

class DateNotFound(ValueError): pass

dayMonthYearRE = re.compile('''(?:\| Day[ \t\r\f]*= (\d{1,2})[ \t\r\f]*(?:.*)?)?
\| (?:Pubm|M)onth[ \t\r\f]*= (\w+)?[ \t\r\f]*
\| (?:Puby|Y)ear[ \t\r\f]*= (\d\d\d\d)[ \t\r\f]*
''')

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

def getDate(comicName: str):
  underscores = comicName.replace(' ', '_')
  url = 'https://dc.fandom.com/wiki/{}?action=edit'.format(underscores)
  response = requests.get(url)
  soup = bs4.BeautifulSoup(response.content)
  textarea = soup.find('textarea')
  if textarea is None:
    raise DateNotFound(comicName, url)
  DCDBcomicTemplate = textarea.string
  matchObj = dayMonthYearRE.search(DCDBcomicTemplate)
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

def getBookNames(DBpath: str = 'comics.sqlite'):
  conn = sqlite3.connect(DBpath)
  curs = conn.cursor()
  curs.execute('''SELECT DISTINCT name FROM BookNames;''')
  return [row[0] for row in curs.fetchall()]

def getBookDates(DBpath: str = 'comics.sqlite'):
  bookNames = getBookNames(DBpath)
  conn = sqlite3.connect(DBpath)
  curs = conn.cursor()
  for name in bookNames:
    if 'novel' in name or name == 'Batman: Fear Itself': continue
    try:
      year, month, day = getDate(name)
    except DateNotFound:
      print('No date found for ' + name)
      continue
    # print(name, year, month, day)
    curs.execute('''INSERT INTO Book VALUES (?, ?, ?, ?, ?)''', (name, name, year, month, day))
  curs.close()
  conn.commit()
  conn.close()

# print(getDate('Batman and Robin Vol 1 5'))
print(getBookDates())

