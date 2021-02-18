
$Env:nexusLIMS_user="username"
$Env:nexusLIMS_pass="password"
$Env:mmfnexus_path="/path/to/mounted/mmfnexus"
$Env:nexusLIMS_path="$PWD"
$Env:nexusLIMS_db_path="$Env:nexusLIMS_path\tests\files\nexuslims_db.sqlite"
$Env:nexusLIMS_test_db_path="$Env:nexusLIMS_path\tests\files\nexuslims_db.sqlite"
$Env:nexusLIMS_timezone="US/Eastern"

If ($args[0] -eq "test") {
	$Env:nexuslims_testing=1
	If (!(Test-Path $Env:nexusLIMS_test_db_path)) {
		echo "Env:nexusLIMS_test_db_path -> $Env:nexusLIMS_test_db_path not found. Creating one ..."
		python $Env:nexusLIMS_path\scripts\create_db.py
		Move-Item .\nexuslims_db.sqlite -Destination $Env:nexusLIMS_test_db_path
		if (!(Test-Path $Env:nexusLIMS_test_db_path)) {
			echo "FAIL to create test db!! Please check."
		}
	}
} Elseif ( ($args.Count -eq 0) -and (Test-Path Env:nexuslims_testing)) {
	Remove-Item Env:nexuslims_testing
}
