#  NIST Public License - 2019
#
#  This software was developed by employees of the National Institute of
#  Standards and Technology (NIST), an agency of the Federal Government
#  and is being made available as a public service. Pursuant to title 17
#  United States Code Section 105, works of NIST employees are not subject
#  to copyright protection in the United States.  This software may be
#  subject to foreign copyright.  Permission in the United States and in
#  foreign countries, to the extent that NIST may hold copyright, to use,
#  copy, modify, create derivative works, and distribute this software and
#  its documentation without fee is hereby granted on a non-exclusive basis,
#  provided that this notice and disclaimer of warranty appears in all copies.
#
#  THE SOFTWARE IS PROVIDED 'AS IS' WITHOUT ANY WARRANTY OF ANY KIND,
#  EITHER EXPRESSED, IMPLIED, OR STATUTORY, INCLUDING, BUT NOT LIMITED
#  TO, ANY WARRANTY THAT THE SOFTWARE WILL CONFORM TO SPECIFICATIONS, ANY
#  IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE,
#  AND FREEDOM FROM INFRINGEMENT, AND ANY WARRANTY THAT THE DOCUMENTATION
#  WILL CONFORM TO THE SOFTWARE, OR ANY WARRANTY THAT THE SOFTWARE WILL BE
#  ERROR FREE.  IN NO EVENT SHALL NIST BE LIABLE FOR ANY DAMAGES, INCLUDING,
#  BUT NOT LIMITED TO, DIRECT, INDIRECT, SPECIAL OR CONSEQUENTIAL DAMAGES,
#  ARISING OUT OF, RESULTING FROM, OR IN ANY WAY CONNECTED WITH THIS SOFTWARE,
#  WHETHER OR NOT BASED UPON WARRANTY, CONTRACT, TORT, OR OTHERWISE, WHETHER
#  OR NOT INJURY WAS SUSTAINED BY PERSONS OR PROPERTY OR OTHERWISE, AND
#  WHETHER OR NOT LOSS WAS SUSTAINED FROM, OR AROSE OUT OF THE RESULTS OF,
#  OR USE OF, THE SOFTWARE OR SERVICES PROVIDED HEREUNDER.
#
"""
**Attributes**

Attributes
----------
XSLT_PATH : str
    The path to ``cal_events_to_nx_record.xsl``, which is used to translate
    the calender event response XML to a format compatible with the Nexus Schema
"""

import os as _os
import logging as _logging
import pathlib as _pathlib
import shutil as _shutil
import sys as _sys
from uuid import uuid4 as _uuid4
from lxml import etree as _etree
from datetime import datetime as _datetime
from io import BytesIO as _bytesIO
import nexusLIMS.schemas.activity as _activity
from nexusLIMS.schemas.activity import AcquisitionActivity as _AcqAc
from nexusLIMS.schemas.activity import cluster_filelist_mtimes
from nexusLIMS.harvester import sharepoint_calendar as _sp_cal
from nexusLIMS.utils import parse_xml as _parse_xml
from nexusLIMS.utils import find_files_by_mtime as _find_files
from nexusLIMS.utils import gnu_find_files_by_mtime as _gnu_find_files
from nexusLIMS.extractors import extension_reader_map as _ext
from nexusLIMS.db.session_handler import get_sessions_to_build as _get_sessions
from nexusLIMS.cdcs import upload_record_files as _upload_record_files
from timeit import default_timer as _timer

_logger = _logging.getLogger(__name__)
XSLT_PATH = _os.path.join(_os.path.dirname(__file__),
                          "cal_events_to_nx_record.xsl")
XSD_PATH = _os.path.join(_os.path.dirname(_activity.__file__),
                         "nexus-experiment.xsd")


def build_record(instrument, dt_from, dt_to,
                 date=None,
                 user=None,
                 sample_id=None,
                 generate_previews=True):
    """
    Construct an XML document conforming to the NexusLIMS schema from a
    directory containing microscopy data files. For calendar parsing,
    currently no logic is implemented for a query that returns multiple records

    Parameters
    ----------
    instrument : :py:class:`~nexusLIMS.instruments.Instrument`
        One of the NexusLIMS instruments contained in the
        :py:attr:`~nexusLIMS.instruments.instrument_db` database.
        Controls what instrument calendar is used to get events.
    dt_from : datetime.datetime
        The starting timestamp that will be used to determine which files go
        in this record
    dt_to : datetime.datetime
        The ending timestamp used to determine the last point in time for
        which files should be associated with this record
    date : str or None
        A YYYY-MM-DD date string indicating the date from which events should
        be fetched (note: the start time of each entry is what will be
        compared - as in :py:func:`~.sharepoint_calendar.get_events`). If
        None, the date detected from the modified time of the folder will be
        used (which may or may not be correct, but given that the folders on
        CFS2E are read-only, should generally be able to be trusted).
    user : str or None
        A valid NIST username (the short format: e.g. "ear1"
***REMOVED***). Controls the results
        returned from the calendar - value is as specified in
        :py:func:`~.sharepoint_calendar.get_events`
    sample_id : str or None
        A unique identifier pointing to a sample identifier for data
        collected in this record. If None, a UUIDv4 will be generated
    generate_previews : bool
        Whether or not to create the preview thumbnail images

    Returns
    -------
    xml_record : str
        A formatted string containing a well-formed and valid XML document
        for the data contained in the provided path
    """

    xml_record = ''

    if sample_id is None:
        sample_id = str(_uuid4())

    # if an explicit date is not provided, use the start of the timespan
    if date is None:
        date = dt_from.strftime('%Y-%m-%d')

    # Insert XML prolog, XSLT reference, and namespaces.
    xml_record += "<?xml version=\"1.0\" encoding=\"UTF-8\"?> \n"
    # TODO: Header elements may be changed once integration into CDCS determined
    xml_record += "<?xml-stylesheet type=\"text/xsl\" href=\"\"?>\n"
    xml_record += "<nx:Experiment xmlns=\"\"\n"
    xml_record += "xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n"
    xml_record += "xmlns:nx=\"" \
                  "https://data.nist.gov/od/dm/nexus/experiment/v1.0\">\n"

    _logger.info(f"Getting calendar events with instrument: {instrument.name}, "
                 f"date: {date}, user: {user}")
    events_str = _sp_cal.get_events(instrument=instrument, date=date,
                                    user=user, wrap=True)
    # TODO: Account for results from multiple sessions? This should only
    #  happen if one user has multiple reservations on the same date. For now,
    #  assume the first record is the right one:
    # Apply XSLT to transform calendar events to single record format:
    output = _parse_xml(events_str, XSLT_PATH,
                        instrument_PID=instrument.name,
                        instrument_name=instrument.schema_name,
                        experiment_id=str(_uuid4()),
                        collaborator=None,
                        sample_id=sample_id)

    # No calendar events were found
    if str(output) == '':
        output = f'<title>Experiment on the {instrument.schema_name}' \
                 f' on {dt_from.strftime("%A %b. %d, %Y")}</title>\n' + \
                 '<id/>\n' + \
                 '<summary>\n' + \
                 f'    <instrument pid="{instrument.name}">' \
                 f'{instrument.schema_name}</instrument>\n' + \
                 '</summary>\n'

    xml_record += str(output)

    _logger.info(f"Building acquisition activities for timespan from "
                 f"{dt_from.isoformat()} to {dt_to.isoformat()}")
    aa_str, activities = build_acq_activities(instrument,
                                              dt_from, dt_to, sample_id,
                                              generate_previews)
    xml_record += aa_str

    xml_record += "</nx:Experiment>"  # Add closing tag for root element.

    return xml_record


def build_acq_activities(instrument, dt_from, dt_to,
                         sample_id, generate_previews):
    """
    Build an XML string representation of each AcquisitionActivity for a
    single microscopy session. This includes setup parameters and metadata
    associated with each dataset obtained during a microscopy session. Unique
    AcquisitionActivities are delimited via clustering of file collection
    time to detect "long" breaks during a session.

    Parameters
    ----------
    instrument : :py:class:`~nexusLIMS.instruments.Instrument`
        One of the NexusLIMS instruments contained in the
        :py:attr:`~nexusLIMS.instruments.instrument_db` database.
        Controls what instrument calendar is used to get events.
    dt_from : datetime.datetime
        The starting timestamp that will be used to determine which files go
        in this record
    dt_to : datetime.datetime
        The ending timestamp used to determine the last point in time for
        which files should be associated with this record
    sample_id : str
        An identifier for the sample from which data was collected
    generate_previews : bool
        Whether or not to create the preview thumbnail images

    Returns
    -------
    acq_activities : str
        A string representing the XML output for each AcquisitionActivity
        associated with a given reservation/experiment on a microscope.

    activities : :obj:`list` of :obj:`~nexusLIMS.schemas.activity.AcquisitionActivity`:
        The list of :py:class:`~nexusLIMS.schemas.activity.AcquisitionActivity`
        objects generated for the record
    """

    _logger = _logging.getLogger(__name__)
    _logger.setLevel(_logging.INFO)

    _logging.getLogger('hyperspy.io_plugins.digital_micrograph').setLevel(
        _logging.WARNING)

    start_timer = _timer()
    path = _os.path.abspath(_os.path.join(_os.environ['mmfnexus_path'],
                                          instrument.filestore_path))
    _logger.info(f'Starting new file-finding in {path}')
    try:
        files = _gnu_find_files(path, dt_from, dt_to)
    except (NotImplementedError, RuntimeError) as e:
        _logger.warning(f'GNU find returned error: {e}\nFalling back to pure '
                        f'Python implementation')
        files = _find_files(path, dt_from, dt_to)

    # remove all files but those supported by nexusLIMS.extractors
    files = [f for f in files if _os.path.splitext(f)[1].strip('.') in
             _ext.keys()]

    end_timer = _timer()
    _logger.info(f'Found {len(files)} files in'
                 f' {end_timer - start_timer:.2f} seconds')

    # return a string indicating no files found if none were found
    if len(files) == 0:
        raise FileNotFoundError('No files found in this time range')

    # get the timestamp boundaries of acquisition activities
    aa_bounds = cluster_filelist_mtimes(files)

    # add the last file's modification time to the boundaries list to make
    # the loop below easier to process
    aa_bounds.append(_os.path.getmtime(files[-1]))

    activities = [None] * len(aa_bounds)

    i = 0
    aa_idx = 0
    while i < len(files):
        f = files[i]
        mtime = _os.path.getmtime(f)

        # check this file's mtime, if it is less than this iteration's value
        # in the AA bounds, then it belongs to this iteration's AA
        # if not, then we should move to the next activity
        if mtime <= aa_bounds[aa_idx]:
            # if current activity index is None, we need to start a new AA:
            if activities[aa_idx] is None:
                start_time = _datetime.fromtimestamp(mtime)
                activities[aa_idx] = _AcqAc(start=start_time)

            # add this file to the AA
            _logger.info(
                f'Adding file {i} '
                f'{f.replace(_os.environ["mmfnexus_path"], "").strip("/")} '
                f'to activity {aa_idx}')
            activities[aa_idx].add_file(f, generate_previews)
            # assume this file is the last one in the activity (this will be
            # true on the last iteration where mtime is <= to the
            # aa_bounds value)
            activities[aa_idx].end = _datetime.fromtimestamp(mtime)
            i += 1
        else:
            # this file's mtime is after the boundary and is thus part of the
            # next activity, so increment AA counter and reprocess file (do
            # not increment i)
            aa_idx += 1

    acq_activities_str = ''
    _logger.info('Finished detecting activities')
    for i, a in enumerate(activities):
        # aa_logger = _logging.getLogger('nexusLIMS.schemas.activity')
        # aa_logger.setLevel(_logging.ERROR)
        _logger.info(f'Activity {i}: storing setup parameters')
        a.store_setup_params()
        _logger.info(f'Activity {i}: storing unique metadata values')
        a.store_unique_metadata()

        acq_activities_str += a.as_xml(i, sample_id,
                                       indent_level=1, print_xml=False)

    return acq_activities_str, activities


def dump_record(instrument,
                dt_from,
                dt_to,
                filename=None,
                date=None,
                user=None,
                generate_previews=True):
    """
    Writes an XML record composed of information pulled from the Sharepoint
    calendar as well as metadata extracted from the microscope data (e.g. dm3
    files).

    Parameters
    ----------
    instrument : :py:class:`~nexusLIMS.instruments.Instrument`
        One of the NexusLIMS instruments contained in the
        :py:attr:`~nexusLIMS.instruments.instrument_db` database.
        Controls what instrument calendar is used to get events.
    dt_from : datetime.datetime
        The starting timestamp that will be used to determine which files go
        in this record
    dt_to : datetime.datetime
        The ending timestamp used to determine the last point in time for
        which files should be associated with this record
    filename : None or str
        The filename of the dumped xml file to write. If None, a default name
        will be generated from the other parameters
    date : str
        A string which corresponds to the event date from which events are going
        to be fetched from
    user : str
        A string which corresponds to the NIST user who performed the
        microscopy experiment
    generate_previews : bool
        Whether or not to create the preview thumbnail images

    Returns
    -------
    filename : str
        The name of the created record that was returned
    """
    if filename is None:
        filename = 'compiled_record' + \
                   (f'_{instrument.name}' if instrument else '') + \
                   (f'_{date}' if date else dt_from.strftime('_%Y-%m-%d')) + \
                   (f'_{user}' if user else '') + '.xml'
    _pathlib.Path(_os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)
    with open(filename, 'w') as f:
        text = build_record(instrument, dt_from, dt_to,
                            date=date, user=user,
                            generate_previews=generate_previews)
        f.write(text)
    return filename


def validate_record(xml_filename):
    """
    Validate an .xml record against the Nexus schema

    Parameters
    ----------
    xml_filename : str or io.StringIO or io.BytesIO
        The path to the xml file to be validated (can also be a file-like
        object like StringIO or BytesIO)

    Returns
    -------
    validates : bool
        Whether or not the record validates against the Nexus schema
    """
    xsd_doc = _etree.parse(XSD_PATH)
    xml_schema = _etree.XMLSchema(xsd_doc)
    xml_doc = _etree.parse(xml_filename)
    validates = xml_schema.validate(xml_doc)
    return validates


def build_new_session_records():
    """
    Fetches new records that need to be built from the database (using
    :py:func:`~nexusLIMS.db.session_handler.get_sessions_to_build`), builds
    those records using
    :py:func:`build_record` (saving to the NexusLIMS folder), and returns a
    list of resulting .xml files to be uploaded to CDCS.

    Returns
    -------
    xml_files : list
        A list of record files that were successfully built and saved to
        centralized storage
    """
    # get the list of sessions with 'WAITING_TO_BE_BUILT' status
    sessions = _get_sessions()
    if not sessions:
        _sys.exit("No 'WAITING_TO_BE_BUILT' sessions were found. Exiting.")
    xml_files = []
    # loop through the sessions
    for s in sessions:
        try:
            s.insert_record_generation_event()
            record_text = build_record(instrument=s.instrument,
                                       dt_from=s.dt_from, dt_to=s.dt_to)
        except (FileNotFoundError, Exception) as e:
            if isinstance(e, FileNotFoundError):
                # if no files were found for this session log, mark it as so in
                # the database
                path = _os.path.join(_os.environ['mmfnexus_path'],
                                     s.instrument.filestore_path)
                _logger.warning(f'No files found in '
                                f'{_os.path.abspath(path)} between '
                                f'{s.dt_from.isoformat()} and '
                                f'{s.dt_to.isoformat()}')
                _logger.warning(f'Marking {s.session_identifier} as '
                                f'"NO_FILES_FOUND"')
                s.update_session_status('NO_FILES_FOUND')
            else:
                _logger.error(f'Could not generate record text: {e}')
                _logger.error(f'Marking {s.session_identifier} as "ERROR"')
                s.update_session_status('ERROR')
        else:
            if validate_record(_bytesIO(bytes(record_text, 'UTF-8'))):
                _logger.info(f'Validated newly generated record')
                # generate filename for saved record and make sure path exists
                basename = f'{s.dt_from.strftime("%Y-%m-%d")}_' \
                           f'{s.instrument.name}_' \
                           f'{s.session_identifier.split("-")[0]}.xml'
                filename = _os.path.join(_os.environ['nexusLIMS_path'], '..',
                                         'records', basename)
                filename = _os.path.abspath(filename)
                _pathlib.Path(_os.path.dirname(filename)).mkdir(parents=True,
                                                                exist_ok=True)
                # write the record to disk and append to list of files generated
                with open(filename, 'w') as f:
                    f.write(record_text)
                _logger.info(f'Wrote record to {filename}')
                xml_files.append(filename)
                # Mark this session as completed in the database
                _logger.info(f'Marking {s.session_identifier} as "COMPLETED"')
                s.update_session_status('COMPLETED')
            else:
                _logger.error(f'Marking {s.session_identifier} as "ERROR"')
                _logger.error(f'Could not validate record, did not write to '
                              f'disk')
                s.update_session_status('ERROR')

    return xml_files


def process_new_records():
    """
    Using :py:meth:`build_new_session_records()`, process new records,
    save them to disk, and upload them to the NexusLIMS CDCS instance.
    """
    xml_files = build_new_session_records()
    files_uploaded, record_ids = _upload_record_files(xml_files)
    for f in files_uploaded:
        uploaded_dir = _os.path.abspath(_os.path.join(_os.path.dirname(f),
                                                      'uploaded'))
        _pathlib.Path(uploaded_dir).mkdir(parents=True, exist_ok=True)

        _shutil.copy2(f, uploaded_dir)
        _os.remove(f)
    files_not_uploaded = [f for f in xml_files if f not in files_uploaded]

    if len(files_not_uploaded) > 0:
        _logger.error(f'Some record files were not uploaded: '
                      f'{files_not_uploaded}')


if __name__ == '__main__':
    """
    If running as a module, process new records 
    """
    process_new_records()   # pragma: no cover