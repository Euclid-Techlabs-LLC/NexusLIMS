Developer documentation
=======================

If you are interested in learning about how the NexusLIMS back-end works or
adding new features, these instructions should get you up and running with a
development environment that will allow you to modify how the code operates.

Development environment setup
-----------------------------

NexusLIMS(Euclid) uses ``conda`` as environment management tool. To set up
for development, we first install ``miniconda`` (a slimmed version of ``conda``).

   Get the miniconda installer from `here <https://docs.conda.io/en/latest/miniconda.html>`_,
   choose the latest Python3 version of your platform and archetecture.
   Install with double clicking if you download a installer, or ``bash <SCRIPT_NAME>``
   if you download a bash installation script.

   In the process, it will ask a few questions:

   Accept the license terms?
      yes

   Where to install?
      Default location is ``$HOME/miniconda3``, or whatever you prefer.

   Do you wish the installer to initialize Miniconda3
      yes

   . After these, open a new shell, you should be able to use ``conda``.

Next create an environment with ``conda``:

.. code::

   conda create -n ENV_NAME python=3.8 # replace ENV_NAME with something
                                       # you like, create an environment
                                       # with such name, and install Python
                                       # 3.8, which nexusLIMS(Euclid) depends
                                       # on (3.7 - 3.8).

To activate an environment, do:

.. code:: bash

   conda activate ENV_NAME # replace ENV_NAME with the concrete name you set.

to deactivate, do:

.. code:: bash

   conda deactivate

To delete an environment, do:

.. code:: bash

   conda env remove -n ENV_NAME

For more conda usage, please refer to conda usage guide.


Installation
------------

.. code:: bash

   conda activate ENV_NAME                                        # activate conda environment
   git clone https://github.com/YOUR_GITHUB_ACCOUNT/nexuslims.git # clone repository
   cd nexuslims
   pip install -e .                                               # install the package
   pip install -r docs/requirements.txt                           # install dev-related package

if ``python -c "import nexusLIMS"`` successfully executed (no error),
then ``nexusLIMS`` is installed correctly.


Set ``nexusLIMS`` environment variables
---------------------------------------

``nexusLIMS`` would require some environment variables set to run, an
example would be like::

   nexusLIMS_user='username'
   nexusLIMS_pass='password'
   mmfnexus_path='/path/to/mmfnexus/mount'
   nexusLIMS_path='/path/to/nexusLIMS/mount/mmfnexus'
   nexusLIMS_db_path='/path/to/nexusLIMS/nexuslims_db.sqlite'

to let shell know them, do:

.. code:: bash

   # linux/macOS
   source env.sh [test] # add `test` to set test flag

.. code:: powershell

   # Windows Powershell
   .\env.ps1 [test] # add `test` to set test flag

.. warning::
   Environment variables in ``env.sh/env.ps1`` may contain credentials, DO NOT
   let git track its changes to avoid information leak!


Building new records
--------------------

The most basic feature of the NexusLIMS back-end is to check the
:doc:`database <database>` for any logs (inserted by the
:doc:`Session Logger App <session_logger_app>`) with a status of
``'TO_BE_BUILT'``. This can be accomplished simply by running the
:py:mod:`~nexusLIMS.builder.record_builder` module directly via:

..  code-block:: bash

    $ pipenv run python -m nexusLIMS.builder.record_builder

This command will find any records that need to be built, build the .xml file,
and then upload it to the front-end CDCS instance.

Using other features of the library
-----------------------------------

Once you are in a python interpreter (such as ``python``, ``ipython``,
``jupyter``, etc.) from the ``pipenv`` environment, you can access the
code of this library through the ``nexusLIMS`` package if you want to do other
tasks, such as extracting metadata or building previews images, etc.

For example, to extract the metadata from a ``.tif`` file saved on the
FEI Quanta, run the following code using the
:py:func:`~nexusLIMS.extractors.quanta_tif.get_quanta_metadata` function:

.. code:: python

   from nexusLIMS.extractors.quanta_tif import get_quanta_metadata
   meta = get_quanta_metadata("path_to_file.tif")

The ``meta`` variable will then contain a dictionary with the extracted
metadata from the file.


Contributing
------------

To contribute, please
`fork <https://gitlab.nist.gov/gitlab/nexuslims/NexusMicroscopyLIMS/forks/new>`_
the repository, develop your addition on a
`feature branch <https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow>`_
within your forked repo, and submit a
`merge request <https://gitlab.nist.gov/gitlab/nexuslims/NexusMicroscopyLIMS/merge_requests>`_
to the
`master <https://gitlab.nist.gov/gitlab/nexuslims/NexusMicroscopyLIMS/tree/master>`_
branch to have it included in the project. Contributing to the package
requires that every line of code is covered by a test case. This project uses
testing through the `pytest <https://docs.pytest.org/en/latest/>`_ library,
and features that do not pass the test cases or decrease coverage will not be
accepted until suitable tests are included (see the |testsLink|_ directory
for examples) and that the coverage of any new features is 100%.
To get this information, you can use an IDE that includes coverage tracking
(such as `PyCharm <https://www.jetbrains.com/pycharm/>`_) or include the
``--cov`` flag when running the tests. To test the preview image generation,
the ``--mpl`` option should also be provided, together with the path to
the `"reference"` images that are tested against. For example:

.. code:: bash

   $ cd <path_to_repo>
   $ pipenv run pytest nexuslims/nexusLIMS/tests --cov=nexuslims/nexusLIMS \
        --cov-report term --mpl --mpl-baseline-path=nexuslims/nexusLIMS/tests/files/figs

   # ============================= test session starts ==============================
   # platform linux -- Python 3.7.5, pytest-5.3.5, py-1.8.1, pluggy-0.13.1
   # Matplotlib: 3.1.3
   # Freetype: 2.6.1
   # rootdir: nexuslims/nexusLIMS/tests, inifile: pytest.ini
   # plugins: mpl-0.11, cov-2.8.1, sugar-0.9.2
   # collected 104 items
   #
   # nexuslims/nexusLIMS/tests/test_calendar_handling.py .............................. [ 28%]
   # nexuslims/nexusLIMS/tests/test_extractors.py ..................................... [ 64%]
   # nexuslims/nexusLIMS/tests/test_instruments.py .....                                [ 69%]
   # nexuslims/nexusLIMS/tests/test_records.py ......................                   [ 90%]
   # nexuslims/nexusLIMS/tests/test_utils.py .........                                  [ 99%]
   # nexuslims/nexusLIMS/tests/test_version.py .                                        [100%]
   #
   # ----------- coverage: platform linux, python 3.7.5-final-0 ---------------------
   # Name                                                         Stmts   Miss  Cover
   # --------------------------------------------------------------------------------
   # nexuslims/nexusLIMS/__init__.py                             8      0   100%
   # nexuslims/nexusLIMS/_urls.py                                3      0   100%
   # nexuslims/nexusLIMS/builder/__init__.py                     0      0   100%
   # nexuslims/nexusLIMS/builder/record_builder.py             149      0   100%
   # nexuslims/nexusLIMS/cdcs.py                                69      0   100%
   # nexuslims/nexusLIMS/db/__init__.py                         10      0   100%
   # nexuslims/nexusLIMS/db/session_handler.py                  72      0   100%
   # nexuslims/nexusLIMS/extractors/__init__.py                 65      0   100%
   # nexuslims/nexusLIMS/extractors/digital_micrograph.py      421      0   100%
   # nexuslims/nexusLIMS/extractors/fei_emi.py                   0      0   100%
   # nexuslims/nexusLIMS/extractors/quanta_tif.py              197      0   100%
   # nexuslims/nexusLIMS/extractors/thumbnail_generator.py     329      0   100%
   # nexuslims/nexusLIMS/harvester/__init__.py                   0      0   100%
   # nexuslims/nexusLIMS/harvester/sharepoint_calendar.py      108      0   100%
   # nexuslims/nexusLIMS/instruments.py                         44      0   100%
   # nexuslims/nexusLIMS/schemas/__init__.py                     0      0   100%
   # nexuslims/nexusLIMS/schemas/activity.py                   151      0   100%
   # test_calendar_handling.py                                      154      0   100%
   # test_extractors.py                                             379      0   100%
   # test_instruments.py                                             27      0   100%
   # test_records.py                                                181      0   100%
   # test_utils.py                                                   61      0   100%
   # test_version.py                                                  5      0   100%
   # utils.py                                                         7      0   100%
   # nexuslims/nexusLIMS/utils.py                              135      0   100%
   # nexuslims/nexusLIMS/version.py                              2      0   100%
   # --------------------------------------------------------------------------------
   # TOTAL                                                         2577      0   100%
