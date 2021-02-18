#!/bin/bash

export nexusLIMS_user='username'
export nexusLIMS_pass='password'
export mmfnexus_path='/path/to/mounted/mmfnexus'
export nexusLIMS_path=$PWD
export nexusLIMS_db_path=$nexusLIMS_path/tests/files/nexuslims_db.sqlite
export nexusLIMS_test_db_path=$nexusLIMS_path/tests/files/nexuslims_db.sqlite
export nexusLIMS_timezone='US/Eastern'

if [[ "$1" == "test" ]]; then
    export nexuslims_testing=1
    if [[ ! -f $nexusLIMS_test_db_path ]]; then
        echo "nexusLIMS_test_db_path -> $nexusLIMS_test_db_path not found. Creating one ..."
        python $nexusLIMS_path/scripts/create_db.py
        mv nexuslims_db.sqlite $nexusLIMS_test_db_path
        [[ -f $nexusLIMS_test_db_path ]] || echo "FAIL to create test db!! Please check."
    fi
elif [[ $# -eq 0 && -n $nexuslims_testing ]]; then
    unset nexuslims_testing
fi
