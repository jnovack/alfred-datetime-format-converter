# -*- coding: utf-8 -*-

import re
import operator
import alfred
import calendar
from dateutil.tz import tzlocal
from datetime import datetime
from delorean import utcnow, parse, epoch

def process(query_str):
    """ Entry point """
    value = parse_query_value(query_str)

    if value is not None:
        results = alfred_items_for_value(value)
        xml = alfred.xml(results) # compiles the XML answer
        alfred.write(xml) # writes the XML back to Alfred

def parse_query_value(query_str):
    """ Return value for the query string """
    try:
        query_str = str(query_str).strip('"\' ')
        match = re.match('(\+|\-)(\d+)([smhdwMy])|now', query_str)

        if match is not None:
            if match.group(0) == 'now':
                d = datetime.now(tzlocal())
            else:
                d = shift_time(match.group(1), match.group(2), match.group(3))
        else:
            # Parse datetime string or timestamp
            try:
                if query_str.isdigit() and len(query_str) == 13:
                    query_str = query_str[:10] + '.' + query_str[10:]
                d = epoch(float(query_str))
            except ValueError:
                d = parse(str(query_str))
    except (TypeError, ValueError):
        d = None
    return d

def shift_time(op, value, measure):
    # Create operator map, to avoid some if/else's
    op_map = {'+' : operator.add, '-' : operator.sub}
    multiplier = 1

    if measure == 'm':
        multiplier = 60
    elif measure == 'h':
        multiplier = 60*60
    elif measure == 'd':
        multiplier = (60*60)*24
    elif measure == 'w':
        multiplier = ((60*60)*24)*7
    elif measure == 'M':
        multiplier = ((60*60)*24)*30 # egh..
    elif measure == 'y':
        multiplier = ((60*60)*24)*365

    # Convert our value + measure to seconds
    seconds = multiplier * int(value)
    current_ts = calendar.timegm(datetime.now().timetuple())

    return epoch(op_map[op](current_ts, seconds))

def alfred_items_for_value(value):
    """
    Given a delorean datetime object, return a list of
    alfred items for each of the results
    """

    index = 0
    results = []

    # First item as timestamp
    item_value = calendar.timegm(value.utctimetuple())
    results.append(alfred.Item(
        title=str(item_value),
        subtitle=u'UTC Timestamp',
        attributes={
            # 'uid': alfred.uid(index),
            'arg': item_value,
        },
        icon='icon.png',
    ))
    index += 1

    #Add support for UTC timestamps in millisecond format
    results.append(alfred.Item(
        title=str(int(item_value)*int('1000')),
        subtitle=u'UTC Timestamp (Milliseconds)',
        attributes={
            # 'uid': alfred.uid(index),
            'arg': int(item_value)*int('1000'),
        },
        icon='icon.png',
    ))
    index += 1

    # Add ISO 8601 UTC
    item_value = utcnow().datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
    results.append(alfred.Item(
        title=str(item_value),
        subtitle='ISO 8601 (UTC)',
        attributes={
            # 'uid': alfred.uid(index),
            'arg': item_value,
        },
    icon='icon.png',
    ))
    index += 1

    # Various formats
    formats = [
        # Sun, 19 May 2002 15:21:36
        ("%a, %d %b %Y %H:%M:%S %Z", 'RFC1123'),
        # 1996-12-19T16:39:57-0800
        ("%Y-%m-%dT%H:%M:%S%z", 'ISO 8601'),
        # 1937-01-01 12:00:27
        ("%Y-%m-%d %H:%M:%S", 'ISO 8601 Non-Standard'),
        # 2018-W13
        ("%Y-W%W", 'Week of Year'),
        # 2018-W13-1
        ("%Y-W%W-%w", 'Week of Year with Day'),
        # 2018-211
        ("%Y-%j", 'Day of Year'),
    ]
    for format, description in formats:
        item_value = value.strftime(format)
        results.append(alfred.Item(
            title=str(item_value),
            subtitle=description,
            attributes={
                # 'uid': alfred.uid(index),
                'arg': item_value,
            },
        icon='icon.png',
        ))
        index += 1

    return results

if __name__ == "__main__":
    try:
        query_str = alfred.args()[0]
    except IndexError:
        query_str = None
    process(query_str)
