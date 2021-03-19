.. _getting-started:

Getting Started with NexusLIMS
===============================

    `Last updated: March 17, 2021`

NexusLIMS runs with ``Python 3``, and requires the Python version to be newer
than **3.7**.

NexusLIMS is designed with an ultimate goal of being
platform-independent, but the deployment differs significantly on Windows
and on UNIX-based OS.

NexusLIMS relies on two major components to create records for
the microscope data: a GUI-based **logger** to create database entries for
the experimental sessions, and a **record builder** to do the "heavy-lifting"
part of building the records. Depending on the network structure of the
microscope facility, these two components can be run on separate computers,
or on the same one.

The requirements for running the two components are different, however, it is
highly recommended that the user emplys a ``conda`` environment to manage the
required packages by NexusLIMS::

    $ conda create -n NexusLIMS python=3.8
    $ conda activate NexusLIMS


Running the logger GUI
++++++++++++++++++++++
The logger GUI script relies on **nearly** no third-party Python packages in
order to minimize the impact on the speed of the computer running it. The
only required package for the logger GUI is ``tendo``:
`tendo <https://github.com/pycontribs/tendo>`__
(Although this might be changed in the future releases). To install all
required packages for the logger GUI, do::

    $ pip install -r GUI/requirements.txt

The system environment variables need to be set before the logger is run, so
it can query the database and get information about the instrument the
computer is controlling.

In the current NexusLIMS version, we are using Shell script (PowerShell for
Windows) to set up the environment variables, although this will very likely
be changed in the future::

    $ cd /path/to/nexuslims/
    $ source env.sh

(For UNIX-based OS), or::

    PS> cd C:\path\to\nexuslims\
    PS> .\env.ps1

on a Windows computer. Now the logger GUI can be run by::

    $ python /path/to/nexuslims/GUI/db_logger_gui.py

