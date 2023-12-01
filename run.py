import click
from ics import Calendar
import json
from datetime import datetime
import os
import sqlite_utils


def filter_guests(event):
    EXCLUSION_CRITERIA = ["group.calendar.google.com", "info@cliffsidedev.com"]

    filtered_guests = []
    filtered_guest_names = []
    filtered_guest_emails = []

    for attendee in event.attendees:
        if attendee.email and not any(
            exclusion in attendee.email for exclusion in EXCLUSION_CRITERIA
        ):
            filtered_guests.append(f"{attendee.common_name} <{attendee.email}>")
            filtered_guest_names.append(attendee.common_name)
            filtered_guest_emails.append(attendee.email)

    return {
        "filtered_guests": filtered_guests,
        "filtered_guest_names": filtered_guest_names,
        "filtered_guest_emails": filtered_guest_emails,
    }


def event_to_json(event):
    guests = [a.email for a in event.attendees if a.email]
    guest_names = [a.common_name for a in event.attendees if a.common_name]

    return {
        "uid": event.uid,
        "title": event.name,
        "description": event.description,
        "guests": [f"{name} <{email}>" for name, email in zip(guest_names, guests)],
        "guest_names": guest_names,
        "guest_emails": guests,
        "date": event.begin.format("MM-DD-YYYY"),
    } | filter_guests(event)


def save_to_sqlite(events, dbname):
    # remove existing db file if exists
    try:
        os.remove(dbname)
    except OSError:
        pass

    db = sqlite_utils.Database(dbname)
    table = db.table("events", pk="uid")
    table.upsert_all(events, alter=True)

    create_view_sql = """
    CREATE VIEW IF NOT EXISTS events_with_guests AS
      SELECT *
      FROM events
      WHERE json_extract(guest_emails, '$') IS NOT NULL
        AND json_extract(guest_emails, '$') != '[]'
    """
    db.conn.execute(create_view_sql)

    # TODO should extract names and emails
    create_grouping_sql = """
    CREATE VIEW event_emails_with_count AS
      SELECT
          json_each.value AS email,
          COUNT(*) AS meeting_count
      FROM events,
          json_each(events.filtered_guest_emails)
      GROUP BY json_each.value
    """

    db.conn.execute(create_grouping_sql)


@click.command()
@click.argument("ics_files", type=click.File("r"), nargs=-1)
@click.option(
    "--output",
    type=click.Choice(["json", "sqlite"], case_sensitive=False),
    default="json",
)
@click.option("--dbname", default="events.db", help="Name of the SQLite database file")
def main(ics_files, output, dbname):
    print(ics_files)

    events = []
    for ics_file in ics_files:
        calendar = Calendar(ics_file.read())
        events.extend(event_to_json(e) for e in calendar.events)

    if output == "json":
        click.echo(json.dumps(events, indent=2))
    elif output == "sqlite":
        save_to_sqlite(events, dbname)
        click.echo(f"Data saved to {dbname} using Datasette")


if __name__ == "__main__":
    main()
