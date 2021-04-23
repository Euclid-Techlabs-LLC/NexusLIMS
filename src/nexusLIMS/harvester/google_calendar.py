# This file has been edited by Euclid Techlabs.
# For LICENSING information, please refer to the LICENSE file in the root directory of NexusLIMS
import datetime
import json
from multiprocessing import Process, Manager

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

import nexusLIMS
from nexusLIMS.instruments import get_instrument_db, get_instr_from_calendar_name
from nexusLIMS.instruments import Instrument
from nexusLIMS.utils import local_datetime


def build_service(service, cred="credentials.json"):
    """
    Build Google Calendar service through OAuth2.
    For more information:
    https://developers.google.com/workspace/guides/create-credentials

    Parameters
    ----------
    service : dict
        An empty dictionary.
        This is needed because :py:class:`~multiprocessing.Process` is used
        to timeout the authorization process. If the user chooses to do nothing when the Google
        OAuth2 page pops out, or uses a wrong Google account without access to the Calendar,
        then the process is killed after 10 seconds.

    cred : str
        Path for the JSON credentials file downloaded from the Google Cloud Console.
        Default: "credentials.json" in the same folder as this script.

    Returns
    -------
    service : :py:class:`~googleapiclient.Resource`
        A Resource instance built for "calendar" and "v3" using the credentials from the ``cred``
        file.
    """
    # For safety reasons, do not store the credential token locally. Use tempfile.
    service = dict()
    scopes = ['https://www.googleapis.com/auth/calendar.readonly']
    flow = InstalledAppFlow.from_client_secrets_file(cred, scopes)
    creds = flow.run_local_server(port=0)
    with open("token.json", "w") as token:
        token.write(creds.to_json())
    service["service"] = build("calendar", "v3", credentials=creds)


def fetch_dict(instrument, dt_from=None, dt_to=None):
    """
    Get a dict of information from the Google Calendar event that best matches the datetime
    period specified by ``dt_from`` and ``dt_to`` for one ``instrument``.
    The current stage is that, if ``dt_from`` or ``dt_to`` is None, then the most recent Calendar
    event is returned. In the future this may change to a list of events (up to a certain maximum
    number).

    Due to how the Google Calendar API was set up, ``dt_from`` and ``dt_to`` have to be fairly
    close to the event of interest, since the query will only get a maximum of 1000 events
    between the two dates.

    Parameters
    ----------
    instrument : :py:class:`~nexusLIMS.instruments.Instrument`
        One of the NexusLIMS instruments contained in the
        :py:attr:`~nexusLIMS.instruments.instrument_db` database.
        Contains information about the api_url to be used to connect to the instrument Calendar.
    dt_from : :py:class:`~datetime.datetime` or None
        A :py:class:`~datetime.datetime` object representing the start of a
        calendar event to search for. Must be an RFC3339 timestamp with mandatory time zone offset.
        For example, 2011-06-03T10:00:00-07:00, 2011-06-03T10:00:00Z.
        If both ``dt_from`` and ``dt_to`` are `None`, no date filtering will be done.
        If just ``dt_from`` is `None`, all events from the beginning of the
        calendar record will be returned up until ``dt_to``.
    dt_to : :py:class:`~datetime.datetime` or None
        dt_to : :py:class:`~datetime.datetime` or None
        A :py:class:`~datetime.datetime` object representing the end of
        calendar event to search for. Must be an RFC3339 timestamp with mandatory time zone offset.
        For example, 2011-06-03T10:00:00-07:00, 2011-06-03T10:00:00Z.
        If ``dt_from`` and ``dt_to`` are `None`, no date filtering will be done.
        If just ``dt_to`` is `None`, all events from the ``dt_from`` to the
        present will be returned.

    Returns
    -------
    query : dict
        A :py:class:`~dict` with detailed information about the Google Calendar event returned
        from the query.
        The two most important keys for ``query`` are "timeZone" and "items".
        query["timeZone"] is the timezone of the Google Calendar, e.g. "America/Chicago";
        query["items"] is a list of Calendar events meeting the ``dt_from`` and ``dt_to`` time
        criteria, up to 1000 events. The events are sorted by time and in an ascending order.
        Each event is a :py:class:`~dict` itself, containing information about the event.
    """
    if isinstance(instrument, str):
        # try to convert from instrument PID string to actual instrument
        try:
            instrument = get_instrument_db()[instrument]
        except KeyError:
            raise KeyError("Entered instrument string '{}' could not be "
                           "parsed".format(instrument))
    elif isinstance(instrument, Instrument):
        pass
    else:
        raise ValueError("Entered instrument "
                         "'{}' could not be parsed".format(instrument))

    if dt_from is not None:
        if not isinstance(dt_from, datetime.datetime):
            raise TypeError("From google_calendar:fetch_dict: need datetime.datetime, got "
                            "{}".format(type(dt_from)))
        dt_from = dt_from.isoformat() + "Z"
    if dt_to is not None:
        if not isinstance(dt_to, datetime.datetime):
            raise TypeError("From google_calendar:fetch_dict: need datetime.datetime, got "
                            "{}".format(type(dt_to)))
        dt_to = dt_to.isoformat() + "Z"

    calendar_id = instrument.api_url
    with Manager() as manager:
        service = manager.dict()
        p = Process(target=build_service, args=(service,))
        p.start()
        p.join(10)
        if p.is_alive():
            print("Failed to get Google authentication in 10 seconds. The token is not saved and "
                  "the service is not built.")
            p.terminate()
        events = service["service"].events()
        query = events.list(calendarId=calendar_id, pageToken=None, maxResults=1000,
                            timeMax=dt_to, timeMin=dt_from).execute()
        return query


class GCalendarEvent:
    """
    A representation of a single calendar "entry" returned from the Google Calendar
    API. Datetime attributes should be timezone-aware, i.e. matching the timezone used in the
    instrument calendar.

    Attributes
    ----------
    title : str
        The title of the event (present at
        ``/feed/entry/content/m:properties/d:TitleOfExperiment``)
    instrument : ~nexusLIMS.instruments.Instrument
        The instrument associated with this calendar entry (fetched using
        the name of the calendar, present at ``/feed/title``)
    updated : datetime.datetime
        The time this event was last updated (present at
        ``/feed/entry/updated``)
    username : str
        The NIST "short" username of the user indicated in this event (present
        at ``/feed/entry/link[@title="UserName"]/m:inline/feed/entry/content
        /m:properties/d:UserName``)
    created_by : str
        The NIST "short" username of the user that created this event (present
        at ```/feed/entry/link[@title="CreatedBy"]/m:inline/feed/entry/content
        /m:properties/d:UserName``)
    start_time : datetime.datetime
        The time this event was scheduled to start (present at
        ``/feed/entry/content/m:properties/d:StartTime``)
        The API response returns this value without a timezone, in the timezone
        of the sharepoint server
    end_time : datetime.datetime
        The time this event was scheduled to end (present at
        ``/feed/entry/content/m:properties/d:EndTime``)
    category_value : str
        The "type" or category of this event (such as User session, service,
        etc.) (present at ``/feed/entry/content/m:properties/d:CategoryValue``)
    experiment_purpose : str
        The user-entered purpose of this experiment (present at
        ``/feed/entry/content/m:properties/d:ExperimentPurpose``)
    sample_details : str
        The user-entered sample details for this experiment (present at
        ``/feed/entry/content/m:properties/d:SampleDetails``)
    project_id : str
        The user-entered project identifier for this experiment (present at
        ``/feed/entry/content/m:properties/d:ProjectID``)
    """

    def __init__(self, title=None, instrument=None, updated=None,
                 username=None, created_by=None, start_time=None,
                 end_time=None, category_value=None, experiment_purpose=None,
                 sample_details=None, project_id=None):
        self.title = title
        self.instrument = instrument
        self.updated = updated
        self.username = username
        self.created_by = created_by
        self.start_time = start_time
        self.end_time = end_time
        self.category_value = category_value
        self.experiment_purpose = experiment_purpose
        self.sample_details = sample_details
        self.project_id = project_id

    @classmethod
    def from_dict(cls, query):
        last_event = query["items"][-1]
        extra_info = last_event["description"]
        extra_dict = dict()
        try:
            extra_dict = json.loads(extra_info)
        except json.decoder.JSONDecodeError as e:
            print(str(e))
            print("From google_calendar.py:GCalendarEvent:from_dict:\nThe description of the "
                  "event has to be JSON decoder-compatible. e.g. '{'category_value': 'XXX'}'")
            print("The event description will be ignored. Search for experimental information "
                  "will not be performed. The GCalendarEvent instance will have None for those "
                  "attributes.")
        title = last_event.get("summary", "(No Title)")
        instrument = get_instr_from_calendar_name(query["summary"])
        updated_utc = datetime.datetime.fromisoformat(query["updated"].rstrip("Z"))
        updated = local_datetime(updated_utc, query["timeZone"])
        username = last_event.get("creator", "")
        created_by = last_event.get("creator", "")
        start_time = last_event.get("start", None)
        end_time = last_event.get("end", None)
        if start_time is None or end_time is None:
            print("From google_calendar.py:GCalendarEvent:from_dict:\n"
                  "Invalid start_time or end_time. Default to a time period between an hour before "
                  "now and now (local timezone).")
            end_time = datetime.datetime.now()
            start_time = end_time - datetime.timedelta(hours=1)

        category_value = extra_dict.get("category_value", "")
        experiment_purpose = extra_dict.get("experiment_purpose", "")
        sample_details = extra_dict.get("sample_details", "")
        project_id = extra_dict.get("project_id", "")

        return GCalendarEvent(title=title,
                              instrument=instrument,
                              updated=updated,
                              username=username,
                              created_by=created_by,
                              start_time=start_time,
                              end_time=end_time,
                              category_value=category_value,
                              experiment_purpose=experiment_purpose,
                              )
