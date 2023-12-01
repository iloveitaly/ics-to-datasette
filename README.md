# ICS to SQLite

This repository contains a script that converts ICS calendar files to SQLite databases. It's useful for analyzing and manipulating calendar data, especially when combined with [Datasette](https://datasette.io).

## Usage

Run the script with the following command:

```shell
poetry run python run.py <ics_file_paths> --output=json
```

## Views

* `events_with_guests`. Only events that have at least one guest are included in this view. Guests entries like `%group.calendar.google.com` are excluded.
* `event_emails_with_count`. This view contains a list of all emails along with the number of events that each email appears in. Helpful for determining your most popular contacts.

### Library Options

Some of the python ical parsing library options I explored:

* <https://allenporter.github.io/ical/ical.html#recurring-events>
* <https://github.com/ics-py/ics-py>


## TODO

- [ ] add option for additional exclusions