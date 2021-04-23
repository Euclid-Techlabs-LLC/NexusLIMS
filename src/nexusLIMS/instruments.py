# This file has been co-edited by both Euclid Techlabs and NIST.
# For LICENSING information, please refer to the LICENSE file in the root directory of NexusLIMS
"""
**Attributes**

Attributes
----------
instrument_db : dict
    A dictionary of :py:class:`~nexusLIMS.instruments.Instrument` objects.

    Each object in this dictionary represents an instrument detected in the
    NexusLIMS remote database.
"""

from nexusLIMS.utils import is_subpath as _is_subpath
from nexusLIMS.utils import get_from_db
import os as _os
import nexusLIMS

CONFIG = nexusLIMS.get_config()


def get_instrument_db():
    """
    Connect to the NexusLIMS database and get a list of all the instruments
    contained within.

    Returns
    -------
    instrument_db : dict
        A dictionary of `Instrument` instances that describe all the
        instruments that were found in the ``instruments`` table of the
        NexusLIMS database
    """
    results, col_names = get_from_db("SELECT * from instruments")
    instr_db = {}
    for line in results:
        this_dict = {}
        for key, val in zip(col_names, line):
            this_dict[key] = val

        key = this_dict.pop('instrument_pid')
        this_dict['name'] = key
        instr_db[key] = Instrument(**this_dict)

    return instr_db


class Instrument:
    """
    A simple object to hold information about an instrument in the Microscopy
    Nexus facility, fetched from the external NexusLIMS database

    Parameters
    ----------
    api_url : str or None
        The calendar API url for this instrument
    calendar_name : str or None
        The "user-friendly" name of the calendar for this instrument as
        displayed on the sharepoint resource (e.g. "FEI Titan TEM")
    calendar_url : str or None
        The URL to this instrument's web-accessible calendar on the
        sharepoint resource
    location : str or None
        The physical location of this instrument (building and room number)
    name : str or None
        The unique identifier for an instrument in the Nexus Microscopy facility
    schema_name : str or None
        The name of instrument as defined in the Nexus Microscopy schema and
        displayed in the records
    property_tag : str or None
        The NIST property tag for this instrument
    filestore_path : str or None
        The path (relative to the Nexus facility root) on the central file
        storage where this instrument stores its data
    computer_name : str or None
        The name of the 'support PC' connected to this instrument
    computer_ip : str or None
        The REN IP address of the 'support PC' connected to this instrument
    computer_mount : str or None
        The full path where the files are saved on the 'support PC' for the
        instrument (e.g. 'M:/')
    """
    def __init__(self,
                 api_url=None,
                 calendar_name=None,
                 calendar_url=None,
                 location=None,
                 name=None,
                 schema_name=None,
                 property_tag=None,
                 filestore_path=None,
                 computer_ip=None,
                 computer_name=None,
                 computer_mount=None):
        """
        Create a new Instrument
        """
        self.api_url = api_url
        self.calendar_name = calendar_name
        self.calendar_url = calendar_url
        self.location = location
        self.name = name
        self.schema_name = schema_name
        self.property_tag = property_tag
        self.filestore_path = filestore_path
        self.computer_ip = computer_ip
        self.computer_name = computer_name
        self.computer_mount = computer_mount

    def __repr__(self):
        return f'Nexus Instrument: {self.name}\n' \
               f'API url:          {self.api_url}\n' \
               f'Calendar name:    {self.calendar_name}\n' \
               f'Calendar url:     {self.calendar_url}\n' \
               f'Schema name:      {self.schema_name}\n' \
               f'Location:         {self.location}\n' \
               f'Property tag:     {self.property_tag}\n' \
               f'Filestore path:   {self.filestore_path}\n' \
               f'Computer IP:      {self.computer_ip}\n' \
               f'Computer name:    {self.computer_name}\n' \
               f'Computer mount:   {self.computer_mount}\n'

    def __str__(self):
        return f'{self.name}' + f' in {self.location}' if self.location else ''


def get_instr_from_filepath(path):
    """
    Using the NexusLIMS database, get an instrument object by a given path.

    Parameters
    ----------
    path : str
        A path (relative or absolute) to a file saved in the central
        filestore that will be used to search for a matching instrument

    Returns
    -------
    instrument : Instrument or None
        An `_Instrument` instance matching the path, or None if no match was
        found

    Examples
    --------
    >>> inst = get_instr_from_filepath('/mnt/**REMOVED**_mmfnexus/Titan/**REMOVED**/' +
    ...                                '190628 - **REMOVED** Training/' +
    ...                                '6_28_2019 Box6 4S/4_330mm.dm3')
    >>> str(inst)
    '**REMOVED** in **REMOVED**'
    """
    for k, v in get_instrument_db().items():
        if _is_subpath(path, _os.path.join(CONFIG["mmfnexus_path"],
                                           v.filestore_path)):
            return v

    return None


def get_instr_from_calendar_name(cal_name):
    """
    Using the NexusLIMS database, get an instrument object by a calendar name.

    Parameters
    ----------
    cal_name : str
        A calendar name (e.g. "**REMOVED**") that will be used to search
        for a matching instrument in the ``api_url`` values

    Returns
    -------
    instrument : Instrument or None
        An `_Instrument` instance matching the path, or None if no match was found.

    Examples
    --------
    >>> inst = get_instr_from_calendar_name('JEOL_TEM_01')
    >>> str(inst)
    'JEOL_TEM_01 in Location_01'
    """
    # To-do: calendar_name in Instrument class and the database is currently set to be the same as
    # instrument_pid. This was inherited from the original NexusLIMS, but can be changed.
    # In the SQLite, instrument_pid and api_url have to be unique, but calendar_name does not.
    # If ones needs this function to do its job, then calendar_name needs to be unique,
    # but it can be different from instrument_pid
    for k, v in get_instrument_db().items():
        if cal_name == v.calendar_name:
            return v

    return None


def get_instr_from_api_url(url):
    """
    Using the NexusLIMS database, get an instrument object by a calendar API url.

    Parameters
    ----------
    url : str
        The **unique** API url for the instrument calendar.

    Returns
    -------
    instrument : Instrument or None
        An `_Instrument` instance matching the API url, or None if no match was found.

    Examples
    --------
    >>> inst = get_instr_from_api_url('URL_FOR_YOUR_INSTRUMENT_CALENDAR')
    >>> str(inst)
    'JEOL_TEM_01 in Location_01'
    """
    for k, v in get_instrument_db().items():
        if url == v.api_url:
            return v

    return None
