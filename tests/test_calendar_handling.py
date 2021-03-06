import os
import pytest
import requests
from lxml import etree
from datetime import datetime as dt
from nexusLIMS.harvester import sharepoint_calendar as sc
from nexusLIMS.utils import parse_xml as _parse_xml
from nexusLIMS.utils import nexus_req as _nexus_req
from nexusLIMS.harvester.sharepoint_calendar import AuthenticationError
# from nexusLIMS import instruments
from nexusLIMS.instruments import instrument_db
from collections import OrderedDict

import warnings

warnings.filterwarnings(
    action='ignore',
    message=r"DeprecationWarning: Using Ntlm()*",
    category=DeprecationWarning)
warnings.filterwarnings(
    'ignore',
    r"Manually creating the cbt stuct from the cert hash will be removed",
    DeprecationWarning)


# class TestCalendarHandling:
#     SC_XSL_FILE = os.path.abspath(
#         os.path.join(os.path.dirname(sc.__file__), 'cal_parser.xsl'))
#     CREDENTIAL_FILE_ABS = os.path.abspath(
#         os.path.join(os.path.dirname(__file__),
#                      '..',
#                      'credentials.ini.example'))
#     CREDENTIAL_FILE_REL = os.path.join('..', 'credentials.ini.example')

#     # get xml content from the FEI Titan for use with parse_xml (we do it at
#     # class level so we don't have to hit the server more than once)
#     #  The only modification made is the manual removal of
#     #  'xmlns="http://www.w3.org/2005/Atom"' from the top level element,
#     #  since this is done by fetch_xml() in the actual processing
#     instr_url = instrument_db['instrument_00'].api_url + \
#                 '?$expand=CreatedBy'
#     xml_content = _nexus_req(instr_url, requests.get).text.replace(
#         'xmlns="http://www.w3.org/2005/Atom"', '')

#     @pytest.fixture
#     def parse_xml(self):
#         """
#         Use the parse_xml method to actually parse the xml through the XSLT
#         stylesheet, which we can then compare to parsing the raw calendar
#         events directly.
#         """
#         # return the xml parsed from the file
#         file_content = bytes(TestCalendarHandling.xml_content, encoding='utf-8')

#         # parsed_xml items will be an _XSLTResultTree object with many
#         # <event>...</event> tags on the same level
#         parsed_xml = dict()
#         # should be 403 items
#         parsed_xml['all'] = _parse_xml(xml=file_content,
#                                        xslt_file=self.SC_XSL_FILE)
#         # should be 10 items
#         parsed_xml['user'] = _parse_xml(xml=file_content,
#                                         xslt_file=self.SC_XSL_FILE,
#                                         user="**REMOVED**")
#         # should be 2 items
#         parsed_xml['date'] = _parse_xml(xml=file_content,
#                                         xslt_file=self.SC_XSL_FILE,
#                                         date='2019-03-06')
#         # should be 1 item
#         parsed_xml['date_and_user'] = _parse_xml(xml=file_content,
#                                                  xslt_file=self.SC_XSL_FILE,
#                                                  date='2019-03-06',
#                                                  user='**REMOVED**')

#         # convert parsing result to string and wrap so we have well-formed xml:
#         xml_strings = dict()
#         for k, v in parsed_xml.items():
#             xml_strings[k] = sc._wrap_events(str(v))

#         # get document tree from the raw file and the ones we parsed:
#         parsed_docs = dict()
#         raw_doc = etree.fromstring(file_content)
#         for k, v in xml_strings.items():
#             parsed_docs[k] = etree.fromstring(v)

#         return raw_doc, parsed_docs

#     # @pytest.mark.parametrize('instrument', list(instrument_db.values()),
#     #                          ids=list(instrument_db.keys()))
#     # def test_downloading_valid_calendars(self, instrument):
#     #     # Handle the two test instruments that we put into the database,
#     #     # which will raise an error because their url values are bogus
#     #     if instrument.name in ['**REMOVED**',
#     #                            '**REMOVED**']:
#     #         pass
#     #     else:
#     #         sc.fetch_xml(instrument)

#     # def test_download_with_date(self):
#     #     doc = etree.fromstring(
#     #         sc.fetch_xml(instrument=instrument_db['**REMOVED**'],
#     #                      dt_from=dt.fromisoformat('2018-11-13T00:00:00'),
#     #                      dt_to=dt.fromisoformat('2018-11-13T23:59:59')))
#     #     # This day should have one entry:
#     #     assert len(doc.findall('entry')) == 1

#     # def test_download_date_w_multiple_entries(self):
#     #     # This should return an event by '**REMOVED**' from 1PM to 5PM on 11/20/2019
#     #     doc = etree.fromstring(
#     #         sc.fetch_xml(instrument=instrument_db['**REMOVED**'],
#     #                      dt_from=dt.fromisoformat('2019-11-20T13:40:20'),
#     #                      dt_to=dt.fromisoformat('2019-11-20T17:30:00'))
#     #     )
#     #     # This day should have one entry (pared down from three):
#     #     assert len(doc.findall('entry')) == 1
#     #     # entry should be user **REMOVED** and title "NexusLIMS computer testing"
#     #     assert doc.find('entry/title').text == "NexusLIMS computer testing"
#     #     assert doc.find('entry/link[@title="UserName"]/'
#     #                     'm:inline/feed/entry/content/m:properties/d:UserName',
#     #                     namespaces=doc.nsmap).text == "**REMOVED**"

#     def test_downloading_bad_calendar(self):
#         with pytest.raises(KeyError):
#             sc.fetch_xml('bogus_instr')

#     def test_bad_username(self, monkeypatch):
#         with monkeypatch.context() as m:
#             m.setenv('nexusLIMS_user', 'bad_user')
#             with pytest.raises(AuthenticationError):
#                 sc.fetch_xml(instrument_db['instrument_00'])

#     def test_absolute_path_to_credentials(self, monkeypatch):
#         from nexusLIMS.harvester.sharepoint_calendar import get_auth
#         with monkeypatch.context() as m:
#             # remove environment variable so we get into file processing
#             m.delenv('nexusLIMS_user')
#             _ = get_auth(self.CREDENTIAL_FILE_ABS)

#     def test_relative_path_to_credentials(self, monkeypatch):
#         from nexusLIMS.harvester.sharepoint_calendar import get_auth
#         os.chdir(os.path.dirname(__file__))
#         with monkeypatch.context() as m:
#             # remove environment variable so we get into file processing
#             m.delenv('nexusLIMS_user')
#             _ = get_auth(self.CREDENTIAL_FILE_REL)

#     def test_bad_path_to_credentials(self, monkeypatch):
#         from nexusLIMS.harvester.sharepoint_calendar import get_auth
#         with monkeypatch.context() as m:
#             # remove environment variable so we get into file processing
#             m.delenv('nexusLIMS_user')
#             cred_file = os.path.join('bogus_credentials.ini')
#             with pytest.raises(AuthenticationError):
#                 _ = get_auth(cred_file)

#     def test_bad_request_response(self, monkeypatch):
#         with monkeypatch.context() as m:
#             class MockResponse(object):
#                 def __init__(self):
#                     self.status_code = 404

#             def mock_get(url, auth, verify):
#                 return MockResponse()

#             # User bad username so we don't get a valid response or lock miclims
#             m.setenv('nexusLIMS_user', 'bad_user')

#             # use monkeypatch to use our version of get for requests that
#             # always returns a 404
#             monkeypatch.setattr(requests, 'get', mock_get)
#             with pytest.raises(requests.exceptions.ConnectionError):
#                 sc.fetch_xml(instrument_db['instrument_00'])

#     def test_fetch_xml_instrument_none(self, monkeypatch):
#         with monkeypatch.context() as m:
#             # use bad username so we don't get a response or lock miclims
#             m.setenv('nexusLIMS_user', 'bad_user')
#             with pytest.raises(AuthenticationError):
#                 sc.fetch_xml(instrument_db['instrument_00'])

#     def test_fetch_xml_instrument_bogus(self, monkeypatch):
#         with monkeypatch.context() as m:
#             # use bad username so we don't get a response or lock miclims
#             m.setenv('nexusLIMS_user', 'bad_user')
#             with pytest.raises(ValueError):
#                 sc.fetch_xml(instrument=5)

#     # def test_fetch_xml_only_dt_from(self):
#     #     # at the time of writing this code (2020-06-26), there were 8 records
#     #     # on the Hitachi S4700 after Jan 1. 2020, which should only increase
#     #     # over time
#     #     xml = sc.fetch_xml(instrument_db['**REMOVED**'],
#     #                        dt_from=dt.fromisoformat('2020-01-01T00:00:00'))
#     #     doc = etree.fromstring(xml)
#     #     assert len(doc.findall('entry')) >= 8

#     # def test_fetch_xml_only_dt_to(self):
#     #     # There are five events prior to May 1, 2016 on the Hitachi S4700
#     #     xml = sc.fetch_xml(instrument_db['**REMOVED**'],
#     #                        dt_to=dt.fromisoformat('2016-05-01T00:00:00'))
#     #     doc = etree.fromstring(xml)
#     #     assert len(doc.findall('entry')) == 5

#     # def test_fetch_xml_calendar_event(self):
#     #     xml = \
#     #         sc.fetch_xml(instrument=instrument_db['**REMOVED**'],
#     #                      dt_from=dt.fromisoformat('2018-11-13T00:00:00'),
#     #                      dt_to=dt.fromisoformat('2018-11-13T23:59:59'))
#     #     cal_event = sc.CalendarEvent.from_xml(xml)
#     #     assert cal_event.title == 'Martensite search'
#     #     assert cal_event.sharepoint_id == 470
#     #     assert cal_event.username == '**REMOVED**'
#     #     assert cal_event.start_time == dt.fromisoformat(
#     #         '2018-11-13T09:00:00-05:00')

#     # def test_fetch_xml_calendar_event_no_entry(self):
#     #     # tests when there is no matching event found
#     #     xml = \
#     #         sc.fetch_xml(instrument=instrument_db['**REMOVED**'],
#     #                      dt_from=dt.fromisoformat('2010-01-01T00:00:00'),
#     #                      dt_to=dt.fromisoformat('2010-01-01T00:00:01'))
#     #     cal_event = sc.CalendarEvent.from_xml(xml)
#     #     assert cal_event is None

#     def test_calendar_event_repr(self):
#         s = dt(2020, 8, 20, 12, 0, 0)
#         e = dt(2020, 8, 20, 16, 0, 40)
#         c = sc.CalendarEvent('Test event',
#                              instrument_db['instruments_00'],
#                              dt.now(), '`username`', 'CREATED BY', s, e, 'category',
#                              'purpose', 'sample details', 'projectID', 999)
#         assert c.__repr__() == 'Event for `username` on instruments_00 from ' \
#                                '2020-08-20T12:00:00 to 2020-08-20T16:00:40'

#         c = sc.CalendarEvent()
#         assert c.__repr__() == 'No matching calendar event'

#         c = sc.CalendarEvent(instrument=instrument_db['instruments_10'])
#         assert c.__repr__() == 'No matching calendar event for ' \
#                                'instruments_10'

#     # def test_dump_calendars(self, tmp_path):
#     #     from nexusLIMS.harvester.sharepoint_calendar import dump_calendars
#     #     f = os.path.join(tmp_path, 'cal_output.xml')
#     #     dump_calendars(instrument='**REMOVED**', filename=f)

#     # def test_division_group_lookup(self):
#     #     from nexusLIMS.harvester.sharepoint_calendar import get_events
#     #     events = get_events(instrument='**REMOVED**',
#     #                         dt_from=dt.fromisoformat('2019-03-06T09:00:00'),
#     #                         dt_to=dt.fromisoformat('2019-03-06T11:00:00'),
#     #                         user='**REMOVED**')
#     #     doc = etree.fromstring(events)
#     #     assert doc.find('event/project/division').text == '642'
#     #     assert doc.find('event/project/group').text == '00'

#     # def test_get_events_good_date(self):
#     #     from nexusLIMS.harvester.sharepoint_calendar import get_events
#     #     events_1 = get_events(instrument='**REMOVED**',
#     #                           dt_from=dt.fromisoformat('2019-03-13T08:00:00'),
#     #                           dt_to=dt.fromisoformat('2019-03-13T16:00:00'))
#     #     doc = etree.fromstring(events_1)
#     #     assert doc.find('event/user/userName').text == '**REMOVED**'
#     #     assert doc.find('event/title').text == '**REMOVED**'

#     def test_calendar_parsing_event_number(self, parse_xml):
#         """
#         We will assume that if the number of elements for each case is the
#         same, then we probably are parsing okay. This could be improved by
#         actually testing the content of the elements (although that is done
#         by test_parsed_event_content()). The number of events is going to
#         increase as time goes on (since we're getting the calendar response
#         dynamically), so we cannot know `a priori` how many there should be.
#         """
#         # Unpack the fixture tuple to use in our method
#         raw_doc, parsed_docs = parse_xml

#         # there should be 403 events to match the 403 entries in the raw xml
#         parsed_event_list = parsed_docs['all'].findall('event')
#         raw_entry_list = raw_doc.findall('entry')
#         assert len(parsed_event_list) == len(raw_entry_list)
#         # assert len(parsed_event_list) == 403

#     def test_calendar_parsing_username(self, parse_xml):
#         """
#         We will assume that if the number of elements for each case is the
#         same, then we probably are parsing okay. This could be improved by
#         actually testing the content of the elements (although that is done
#         by test_parsed_event_content())
#         """
#         # Unpack the fixture tuple to use in our method
#         raw_doc, parsed_docs = parse_xml

#         # test user parsing:
#         # user '**REMOVED**' has 10 events on the Titan calendar
#         raw_user_list = raw_doc.xpath("entry[./link/m:inline/entry/content/"
#                                       "m:properties/d:UserName/text() = '**REMOVED**']",
#                                       namespaces=raw_doc.nsmap)
#         # parsed_docs['user'] is root <events> tag
#         parse_xml_user_list = parsed_docs['user'].findall('event')

#         assert len(raw_user_list) == len(parse_xml_user_list)
#         assert len(parse_xml_user_list) == 10

#     def test_calendar_parsing_date(self, parse_xml):
#         """
#         We will assume that if the number of elements for each case is the
#         same, then we probably are parsing okay. This could be improved by
#         actually testing the content of the elements (although that is done
#         by test_parsed_event_content())
#         """
#         # Unpack the fixture tuple to use in our method
#         raw_doc, parsed_docs = parse_xml

#         # test date parsing:
#         # 2019-03-06 has 2 events on the Titan calendar
#         raw_date_list = raw_doc.xpath("entry[contains("
#                                       "./content/m:properties/d:StartTime/"
#                                       "text(), '2019-03-06')]",
#                                       namespaces=raw_doc.nsmap)
#         # parsed_docs['user'] is root <events> tag
#         parse_xml_date_list = parsed_docs['date'].findall('event')

#         assert len(raw_date_list) == len(parse_xml_date_list)
#         assert len(parse_xml_date_list) == 2

#     def test_calendar_parsing_username_and_date(self, parse_xml):
#         """
#         We will assume that if the number of elements for each case is the
#         same, then we probably are parsing okay. This could be improved by
#         actually testing the content of the elements (although that is done
#         by test_parsed_event_content())
#         """
#         # Unpack the fixture tuple to use in our method
#         raw_doc, parsed_docs = parse_xml

#         # test date and user parsing:
#         # 2019-03-06 has 2 events on the Titan calendar, one of which was
#         # made by **REMOVED**
#         raw_date_list = raw_doc.xpath("entry[contains("
#                                       "./content/m:properties/d:StartTime/"
#                                       "text(), '2019-03-06') and "
#                                       "./link/m:inline/entry/content/"
#                                       "m:properties/d:UserName/text() = "
#                                       "'**REMOVED**']",
#                                       namespaces=raw_doc.nsmap)
#         # parsed_docs['user'] is root <events> tag
#         parse_xml_date_list = parsed_docs['date_and_user'].findall('event')

#         assert len(raw_date_list) == len(parse_xml_date_list)
#         assert len(parse_xml_date_list) == 1

#     def test_basic_auth(self):
#         from nexusLIMS.harvester.sharepoint_calendar import get_auth
#         res = get_auth(basic=True)
#         assert isinstance(res, tuple)

#     def test_parsed_event_content(self, parse_xml):
#         """
#         Test the content of the event that was parsed with the XSLT
#         """
#         # Unpack the fixture tuple to use in our method
#         raw_doc, parsed_docs = parse_xml

#         parsed_xml = parsed_docs['date_and_user']
#         assert parsed_xml.tag == 'events'

#         # Should be one event matching this condition
#         event = parsed_docs['date_and_user'].find('event')
#         tag_dict = OrderedDict([
#             ('dateSearched', '2019-03-06'),
#             ('userSearched', '**REMOVED**'),
#             ('title', 'Bringing up HT'),
#             ('instrument', '**REMOVED**'),
#             ('user', '\n  '),
#             ('purpose', 'Still need to bring up HT '
#                         'following water filter replacement'),
#             ('sampleDetails', 'No sample'),
#             ('description', None),
#             ('startTime', '2019-03-06T09:00:00'),
#             ('endTime', '2019-03-06T11:00:00'),
#             ('link', instrument_db['**REMOVED**'].api_url + '(501)'),
#             ('eventId', '501')])

#         user = parsed_docs['date_and_user'].find('event/user')
#         link_idx = instrument_db['**REMOVED**'].api_url.rfind('/')
#         lnk_base = instrument_db['**REMOVED**'].api_url[:link_idx]
#         user_dict = OrderedDict([
#             ('userName', '**REMOVED**'),
#             ('name', '**REMOVED**'),
#             ('email', '**REMOVED**'),
#             ('phone', '**REMOVED**'),
#             ('office', '**REMOVED**'),
#             ('link', f'{lnk_base}/UserInformationList(224)'),
#             ('userId', '224')])

#         for k, v in tag_dict.items():
#             if k == 'user':
#                 continue
#             else:
#                 assert event.find(k).text == v

#         for k, v in user_dict.items():
#             assert user.find(k).text == v

#     def test_get_sharepoint_date_string(self):
#         date_str = sc._get_sharepoint_date_string(
#             dt(year=2020, month=6, day=29, hour=1, minute=23, second=48))
#         assert date_str == '2020-06-28T21:23:48'

#     def test_get_sharepoint_date_string_no_env_var(self, monkeypatch):
#         with monkeypatch.context() as m:
#             # remove environment variable to test error raising
#             m.delenv('nexusLIMS_timezone')
#             with pytest.raises(EnvironmentError):
#                 sc._get_sharepoint_date_string(dt.now())

#     def test_get_sharepoint_tz(self, monkeypatch):
#         assert sc._get_sharepoint_tz() in ['America/New_York',
#                                            'America/Chicago',
#                                            'America/Denver',
#                                            'America/Los_Angeles',
#                                            'Pacific/Honolulu']

#         # Create a fake response object that will have the right xml (like
#         # would be returned if the server were in different time zones)
#         class MockResponse(object):
#             def __init__(self, text):
#                 self.text = \
#                     """<?xml version="1.0" encoding="utf-8"?>
# <feed xml:base="https://**REMOVED**/**REMOVED**/_api/"
#       xmlns="http://www.w3.org/2005/Atom"
#       xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices"
#       xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata"
#       xmlns:georss="http://www.georss.org/georss"
#       xmlns:gml="http://www.opengis.net/gml">
# """ + text + "</feed>"

#         def mock_get_et(url, req):
#             return MockResponse(text="""
#             <content type="application/xml">
#                 <m:properties>
#                     <d:Description>(UTC-05:00) Eastern Time (US and 
#                     Canada)</d:Description>
#                     <d:Id m:type="Edm.Int32">11</d:Id>
#                     <d:Information m:type="SP.TimeZoneInformation">
#                         <d:Bias m:type="Edm.Int32">360</d:Bias>
#                         <d:DaylightBias m:type="Edm.Int32">-60</d:DaylightBias>
#                         <d:StandardBias m:type="Edm.Int32">0</d:StandardBias>
#                     </d:Information>
#                 </m:properties>
#             </content>
#             """)

#         def mock_get_ct(url, req):
#             return MockResponse(text="""
#             <content type="application/xml">
#                 <m:properties>
#                     <d:Description>(UTC-06:00) Central Time (US and 
#                     Canada)</d:Description>
#                     <d:Id m:type="Edm.Int32">11</d:Id>
#                     <d:Information m:type="SP.TimeZoneInformation">
#                         <d:Bias m:type="Edm.Int32">360</d:Bias>
#                         <d:DaylightBias m:type="Edm.Int32">-60</d:DaylightBias>
#                         <d:StandardBias m:type="Edm.Int32">0</d:StandardBias>
#                     </d:Information>
#                 </m:properties>
#             </content>
#             """)

#         def mock_get_mt(url, req):
#             return MockResponse(text="""
#             <content type="application/xml">
#                 <m:properties>
#                     <d:Description>(UTC-07:00) Mountain Time (US and 
#                     Canada)</d:Description>
#                     <d:Id m:type="Edm.Int32">12</d:Id>
#                     <d:Information m:type="SP.TimeZoneInformation">
#                         <d:Bias m:type="Edm.Int32">420</d:Bias>
#                         <d:DaylightBias m:type="Edm.Int32">-60</d:DaylightBias>
#                         <d:StandardBias m:type="Edm.Int32">0</d:StandardBias>
#                     </d:Information>
#             </m:properties>
#             </content>
#             """)

#         def mock_get_pt(url, req):
#             return MockResponse(text="""
#             <content type="application/xml">
#                 <m:properties>
#                     <d:Description>(UTC-08:00) Pacific Time (US and 
#                     Canada)</d:Description>
#                     <d:Id m:type="Edm.Int32">13</d:Id>
#                     <d:Information m:type="SP.TimeZoneInformation">
#                         <d:Bias m:type="Edm.Int32">480</d:Bias>
#                         <d:DaylightBias m:type="Edm.Int32">-60</d:DaylightBias>
#                         <d:StandardBias m:type="Edm.Int32">0</d:StandardBias>
#                     </d:Information>
#                 </m:properties>
#             </content>
#             """)

#         def mock_get_ht(url, req):
#             return MockResponse(text="""
#             <content type="application/xml">
#                 <m:properties>
#                     <d:Description>(UTC-10:00) Hawaii</d:Description>
#                     <d:Id m:type="Edm.Int32">15</d:Id>
#                     <d:Information m:type="SP.TimeZoneInformation">
#                         <d:Bias m:type="Edm.Int32">600</d:Bias>
#                         <d:DaylightBias m:type="Edm.Int32">-60</d:DaylightBias>
#                         <d:StandardBias m:type="Edm.Int32">0</d:StandardBias>
#                     </d:Information>
#                 </m:properties>
#             </content>
#             """)

#         monkeypatch.setattr(sc, '_nexus_req', mock_get_et)
#         assert sc._get_sharepoint_tz() == 'America/New_York'
#         monkeypatch.setattr(sc, '_nexus_req', mock_get_ct)
#         assert sc._get_sharepoint_tz() == 'America/Chicago'
#         monkeypatch.setattr(sc, '_nexus_req', mock_get_mt)
#         assert sc._get_sharepoint_tz() == 'America/Denver'
#         monkeypatch.setattr(sc, '_nexus_req', mock_get_pt)
#         assert sc._get_sharepoint_tz() == 'America/Los_Angeles'
#         monkeypatch.setattr(sc, '_nexus_req', mock_get_ht)
#         assert sc._get_sharepoint_tz() == 'Pacific/Honolulu'
