# trackcopy start -- 0
# Source: https://github.com/micktwomey/pyiso8601/blob/4b463ebeff76c438bd40145ef3dc56d0cac20b6e/iso8601/iso8601.py#L11-L14
import datetime
from decimal import Decimal
import sys
import re
# trackcopy end

# trackcopy start -- 1
# Source: https://github.com/micktwomey/pyiso8601/blob/4b463ebeff76c438bd40145ef3dc56d0cac20b6e/iso8601/iso8601.py#L20
_basestring = str
# trackcopy end

# trackcopy start -- 2
# Source: https://github.com/micktwomey/pyiso8601/blob/4b463ebeff76c438bd40145ef3dc56d0cac20b6e/iso8601/iso8601.py#L25-L71
# Adapted from http://delete.me.uk/2005/03/iso8601.html
ISO8601_REGEX = re.compile(
    r"""
    (?P<year>[0-9]{4})
    (
        (
            (-(?P<monthdash>[0-9]{1,2}))
            |
            (?P<month>[0-9]{2})
            (?!$)  # Don't allow YYYYMM
        )
        (
            (
                (-(?P<daydash>[0-9]{1,2}))
                |
                (?P<day>[0-9]{2})
            )
            (
                (
                    (?P<separator>[ T])
                    (?P<hour>[0-9]{2})
                    (:{0,1}(?P<minute>[0-9]{2})){0,1}
                    (
                        :{0,1}(?P<second>[0-9]{1,2})
                        ([.,](?P<second_fraction>[0-9]+)){0,1}
                    ){0,1}
                    (?P<timezone>
                        Z
                        |
                        (
                            (?P<tz_sign>[-+])
                            (?P<tz_hour>[0-9]{2})
                            :{0,1}
                            (?P<tz_minute>[0-9]{2}){0,1}
                        )
                    ){0,1}
                ){0,1}
            )
        ){0,1}  # YYYY-MM
    ){0,1}  # YYYY only
    $
    """,
    re.VERBOSE
)

class ParseError(ValueError):
    """Raised when there is a problem parsing a date string"""
# trackcopy end

# trackcopy start -- 3
# Source: https://github.com/micktwomey/pyiso8601/blob/4b463ebeff76c438bd40145ef3dc56d0cac20b6e/iso8601/iso8601.py#L74-L79
UTC = datetime.timezone.utc
def FixedOffset(offset_hours, offset_minutes, name):
    return datetime.timezone(
        datetime.timedelta(
            hours=offset_hours, minutes=offset_minutes),
        name)
# trackcopy end

# trackcopy start -- 4
# Source: https://github.com/micktwomey/pyiso8601/blob/4b463ebeff76c438bd40145ef3dc56d0cac20b6e/iso8601/iso8601.py#L137-L214
def to_int(d, key, default_to_zero=False, default=None, required=True):
    """Pull a value from the dict and convert to int

    :param default_to_zero: If the value is None or empty, treat it as zero
    :param default: If the value is missing in the dict use this default

    """
    value = d.get(key) or default
    if (value in ["", None]) and default_to_zero:
        return 0
    if value is None:
        if required:
            raise ParseError("Unable to read %s from %s" % (key, d))
    else:
        return int(value)

def parse_timezone(matches, default_timezone=UTC):
    """Parses ISO 8601 time zone specs into tzinfo offsets

    """

    if matches["timezone"] == "Z":
        return UTC
    # This isn't strictly correct, but it's common to encounter dates without
    # timezones so I'll assume the default (which defaults to UTC).
    # Addresses issue 4.
    if matches["timezone"] is None:
        return default_timezone
    sign = matches["tz_sign"]
    hours = to_int(matches, "tz_hour")
    minutes = to_int(matches, "tz_minute", default_to_zero=True)
    description = "%s%02d:%02d" % (sign, hours, minutes)
    if sign == "-":
        hours = -hours
        minutes = -minutes
    return FixedOffset(hours, minutes, description)

def parse_date(datestring, default_timezone=UTC):
    """Parses ISO 8601 dates into datetime objects

    The timezone is parsed from the date string. However it is quite common to
    have dates without a timezone (not strictly correct). In this case the
    default timezone specified in default_timezone is used. This is UTC by
    default.

    :param datestring: The date to parse as a string
    :param default_timezone: A datetime tzinfo instance to use when no timezone
                             is specified in the datestring. If this is set to
                             None then a naive datetime object is returned.
    :returns: A datetime.datetime instance
    :raises: ParseError when there is a problem parsing the date or
             constructing the datetime instance.

    """
    if not isinstance(datestring, _basestring):
        raise ParseError("Expecting a string %r" % datestring)
    m = ISO8601_REGEX.match(datestring)
    if not m:
        raise ParseError("Unable to parse date string %r" % datestring)
    groups = m.groupdict()

    tz = parse_timezone(groups, default_timezone=default_timezone)

    groups["second_fraction"] = int(Decimal("0.%s" % (groups["second_fraction"] or 0)) * Decimal("1000000.0"))

    try:
        return datetime.datetime(
            year=to_int(groups, "year"),
            month=to_int(groups, "month", default=to_int(groups, "monthdash", required=False, default=1)),
            day=to_int(groups, "day", default=to_int(groups, "daydash", required=False, default=1)),
            hour=to_int(groups, "hour", default_to_zero=True),
            minute=to_int(groups, "minute", default_to_zero=True),
            second=to_int(groups, "second", default_to_zero=True),
            microsecond=groups["second_fraction"],
            tzinfo=tz,
        )
    except Exception as e:
        raise ParseError(e)
# trackcopy end
