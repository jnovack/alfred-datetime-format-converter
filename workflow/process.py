# -*- coding: utf-8 -*-

import re
import operator
import alfred
import calendar
from dateutil.tz import tzlocal
from dateutil.parser import parse as parse_datetime
from datetime import datetime
from datetime import timedelta
from datetime import timezone

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
        query_str = str(query_str or '').strip('"\' ').strip()
        if not query_str:
            query_str = 'now'

        match = re.match(r'^(\+|\-)(\d+)([smhdwMy])$|^now$', query_str, re.IGNORECASE)

        if match is not None:
            if query_str.lower() == 'now':
                d = datetime.now(tzlocal())
            else:
                d = shift_time(match.group(1), match.group(2), match.group(3))
        else:
            # Parse numeric timestamp input first (seconds, fractional seconds, or milliseconds)
            try:
                if re.match(r'^\d{13}$', query_str):
                    ts_value = float(query_str) / 1000.0
                elif re.match(r'^-?\d+(\.\d+)?$', query_str):
                    ts_value = float(query_str)
                else:
                    raise ValueError('not a numeric timestamp')
                d = datetime.fromtimestamp(ts_value, timezone.utc).astimezone(tzlocal())
            except (ValueError, OverflowError):
                d = parse_datetime(query_str)
                if d.tzinfo is None:
                    d = d.replace(tzinfo=tzlocal())
                else:
                    d = d.astimezone(tzlocal())
    except (TypeError, ValueError, OverflowError):
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

    # Convert value + measure to seconds and apply to current UTC time.
    seconds = multiplier * int(value)
    current_utc = datetime.now(timezone.utc)
    shifted_utc = current_utc + timedelta(seconds=op_map[op](0, seconds))
    return shifted_utc.astimezone(tzlocal())

def alfred_items_for_value(value):
    """
    Given a delorean datetime object, return a list of
    alfred items for each of the results
    """

    index = 0
    results = []

    if value.tzinfo is None:
        value = value.replace(tzinfo=tzlocal())

    localtime = value.astimezone(tzlocal())
    utctime = localtime.astimezone(timezone.utc)

    # First item as timestamp (UTC seconds)
    unixtime = calendar.timegm(utctime.utctimetuple())
    results.append(alfred.Item(
        title=str(unixtime),
        subtitle=u'UTC Timestamp',
        attributes={
            # 'uid': alfred.uid(index),
            'arg': unixtime,
        },
        icon='icon.png',
    ))
    index += 1

    # Add support for UTC timestamps in millisecond format // Warning: Millisecond precision is lost during conversion
    results.append(alfred.Item(
        title=str(int(unixtime)*int('1000')),
        subtitle=u'UTC Timestamp (Milliseconds)',
        attributes={
            # 'uid': alfred.uid(index),
            'arg': int(unixtime)*int('1000'),
        },
        icon='icon.png',
    ))
    index += 1

    # Add ISO 8601 UTC
    utc_iso = utctime.strftime("%Y-%m-%dT%H:%M:%SZ")
    results.append(alfred.Item(
        title=str(utc_iso),
        subtitle='ISO 8601 (UTC)',
        attributes={
            # 'uid': alfred.uid(index),
            'arg': utc_iso,
        },
    icon='icon.png',
    ))
    index += 1

    # ISO 8601 local
    item_value = localtime.strftime("%Y-%m-%dT%H:%M:%S%z")
    results.append(alfred.Item(
        title=str(item_value),
        subtitle='ISO 8601 (Local)',
        attributes={
            # 'uid': alfred.uid(index),
            'arg': item_value,
        },
    icon='icon.png',
    ))


    # Various formats
    formats = [
        # Sun, 19 May 2002 15:21:36
        ("%a, %d %b %Y %H:%M:%S %Z (%z)", 'RFC1123'),
        # 2018-W13
        ("%Y-W%W", 'Week of Year'),
        # 2018-W13-1
        ("%Y-W%W-%w", 'Week of Year with Day'),
        # 2018-211
        ("%Y-%j", 'Day of Year'),
    ]
    for format, description in formats:
        item_value = localtime.strftime(format)
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
        query_str = 'now'
    process(query_str)
