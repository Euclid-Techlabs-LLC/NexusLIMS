-- Creator:       MySQL Workbench 8.0.18/ExportSQLite Plugin 0.1.0
-- Author:        Joshua Taillon
-- Caption:       NexusLIMS DB
-- Project:       Nexus Microscopy LIMS
-- Changed:       2019-12-06 14:30
-- Changed:       2019-10-31 16:50
-- Created:       2019-10-30 14:21
PRAGMA foreign_keys = ON;

-- Schema: nexuslims_db
--   A database to hold information about the instruments and sessions logged in the Nexus Microscopy Facility
ATTACH "nexuslims_db.sqlite" AS "nexuslims_db";
BEGIN;
CREATE TABLE "nexuslims_db"."instruments"(
  "instrument_pid" VARCHAR(100) PRIMARY KEY NOT NULL,-- The unique identifier for an instrument in the Nexus Microscopy facility
  "api_url" TEXT NOT NULL,-- The calendar API url for this instrument
  "calendar_name" TEXT NOT NULL,-- "The "user-friendly" name of the calendar for this instrument as displayed on the sharepoint resource (e.g. "FEI Titan TEM")"
  "calendar_url" TEXT NOT NULL,-- "The URL to this instrument's web-accessible calendar on the sharepoint resource"
  "location" VARCHAR(100) NOT NULL,-- The physical location of this instrument (building and room number)
  "schema_name" TEXT NOT NULL,-- The name of instrument as defined in the Nexus Microscopy schema and displayed in the records
  "property_tag" VARCHAR(20) NOT NULL,-- The NIST property tag for this instrument
  "filestore_path" TEXT NOT NULL,-- The path (relative to the Nexus facility root) on the central file storage where this instrument stores its data
  "computer_name" TEXT,-- "The name of the 'support PC' connected to this instrument"
  "computer_ip" VARCHAR(15),-- "The REN IP address of the 'support PC' connected to this instrument"
  "computer_mount" TEXT,-- "The full path where the files are saved on the 'support PC' for the instrument (e.g. 'M:/')"
  CONSTRAINT "instrument_pid_UNIQUE"
    UNIQUE("instrument_pid"),
  CONSTRAINT "api_url_UNIQUE"
    UNIQUE("api_url"),
  CONSTRAINT "property_tag_UNIQUE"
    UNIQUE("property_tag"),
  CONSTRAINT "filestore_path_UNIQUE"
    UNIQUE("filestore_path"),
  CONSTRAINT "computer_name_UNIQUE"
    UNIQUE("computer_name"),
  CONSTRAINT "computer_ip_UNIQUE"
    UNIQUE("computer_ip")
);
INSERT INTO "instruments"("instrument_pid","api_url","calendar_name","calendar_url","location","schema_name","property_tag","filestore_path","computer_name","computer_ip","computer_mount") VALUES('instrument_00', 'https://api_url/00', 'FEI HeliosDB',    'https://**REMOVED**/**REMOVED**/calendar.aspx',               '**REMOVED**', 'FEI Helios',      'property_tag_00', './Aphrodite', NULL, NULL, NULL);
INSERT INTO "instruments"("instrument_pid","api_url","calendar_name","calendar_url","location","schema_name","property_tag","filestore_path","computer_name","computer_ip","computer_mount") VALUES('instrument_01', 'https://api_url/01', 'FEI Quanta200',  'https://**REMOVED**/**REMOVED**/calendar.aspx',     '**REMOVED**', 'FEI Quanta200',              'property_tag_01', './Quanta',    'computer_name_01', NULL, 'M:/');
INSERT INTO "instruments"("instrument_pid","api_url","calendar_name","calendar_url","location","schema_name","property_tag","filestore_path","computer_name","computer_ip","computer_mount") VALUES('instrument_02', 'https://api_url/02', 'FEI Titan STEM', 'https://**REMOVED**/**REMOVED**/calendar.aspx',                 '**REMOVED**', 'FEI Titan STEM', 'property_tag_02', './643Titan',  'computer_name_02', NULL, 'X:/');
INSERT INTO "instruments"("instrument_pid","api_url","calendar_name","calendar_url","location","schema_name","property_tag","filestore_path","computer_name","computer_ip","computer_mount") VALUES('instrument_03', 'https://api_url/03', 'FEI Titan TEM',   'https://**REMOVED**/**REMOVED**/calendar.aspx',         '**REMOVED**', 'FEI Titan TEM',         'property_tag_03', './Titan',     'computer_name_03', NULL, 'M:/');
INSERT INTO "instruments"("instrument_pid","api_url","calendar_name","calendar_url","location","schema_name","property_tag","filestore_path","computer_name","computer_ip","computer_mount") VALUES('instrument_04', 'https://api_url/04', 'Hitachi S4700',  'https://**REMOVED**/**REMOVED**/calendar.aspx',     '**REMOVED**', 'Hitachi S4700',              'property_tag_04', './S4700', NULL, NULL, NULL);
INSERT INTO "instruments"("instrument_pid","api_url","calendar_name","calendar_url","location","schema_name","property_tag","filestore_path","computer_name","computer_ip","computer_mount") VALUES('instrument_05', 'https://api_url/05', 'Hitachi-S5500',  'https://**REMOVED**/**REMOVED**/calendar.aspx',                 '**REMOVED**', 'Hitachi S5500',  'property_tag_05', './S5500', NULL, NULL, NULL);
INSERT INTO "instruments"("instrument_pid","api_url","calendar_name","calendar_url","location","schema_name","property_tag","filestore_path","computer_name","computer_ip","computer_mount") VALUES('instrument_06', 'https://api_url/06', 'JEOL **REMOVED**',    'https://**REMOVED**/**REMOVED**/calendar.aspx',      '**REMOVED**', 'JEOL **REMOVED**',     'property_tag_06', './JEOL3010',  'computer_name_06', NULL, 'Z:/');
INSERT INTO "instruments"("instrument_pid","api_url","calendar_name","calendar_url","location","schema_name","property_tag","filestore_path","computer_name","computer_ip","computer_mount") VALUES('instrument_07', 'https://api_url/07', 'JEOL JSM7100',    'https://**REMOVED**/**REMOVED**/calendar.aspx',      '**REMOVED**', 'JEOL JSM7100',             'property_tag_07', './7100Jeol', NULL, NULL, NULL);
INSERT INTO "instruments"("instrument_pid","api_url","calendar_name","calendar_url","location","schema_name","property_tag","filestore_path","computer_name","computer_ip","computer_mount") VALUES('instrument_08', 'https://api_url/08', 'Philips CM30',    'https://**REMOVED**/**REMOVED**/calendar.aspx',      '**REMOVED**', 'Philips CM30',             'property_tag_08', './CM30', NULL, NULL, NULL);
INSERT INTO "instruments"("instrument_pid","api_url","calendar_name","calendar_url","location","schema_name","property_tag","filestore_path","computer_name","computer_ip","computer_mount") VALUES('instrument_09', 'https://api_url/09', 'Philips EM400',  'https://**REMOVED**/**REMOVED**/calendar.aspx',     '**REMOVED**', 'Philips EM400',              'property_tag_09', './EM400', NULL, NULL, NULL);
INSERT INTO "instruments"("instrument_pid","api_url","calendar_name","calendar_url","location","schema_name","property_tag","filestore_path","computer_name","computer_ip","computer_mount") VALUES('instrument_10', 'https://api_url/10', 'Surface test instrument', 'https://example.com/surface', '**REMOVED**', 'Surface test instrument',                 'property_tag_10', './test_surface', 'computer_name_10', NULL, 'M:/');


CREATE TABLE "nexuslims_db"."session_log"(
  "id_session_log" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, -- the auto-incrementing primary key identifier for this table (just a generic number)
  "session_identifier" VARCHAR(36) NOT NULL,-- A UUID4 (36-character string) that is consistent among a single record's "START", "END", and "RECORD_GENERATION" events
  "instrument" VARCHAR(100) NOT NULL,-- The instrument associated with this session (foreign key reference to the 'instruments' table)
  "timestamp" DATETIME NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f', 'now', 'localtime')),-- The date and time of the logged event
  "event_type" TEXT NOT NULL CHECK("event_type" IN('START', 'END', 'RECORD_GENERATION')),-- The type of log for this session either "START" or "END"
  "record_status" TEXT NOT NULL CHECK("record_status" IN('COMPLETED', 'WAITING_FOR_END', 'TO_BE_BUILT', 'ERROR', 'NO_FILES_FOUND')) DEFAULT 'WAITING_FOR_END',-- The status of the record associated with this session. One of 'WAITING_FOR_END' (has a start event, but no end event), 'TO_BE_BUILT' (session has ended, but record not yet built), 'COMPLETED' (record has been built successfully), 'ERROR' (some error happened during record generation), or 'NO_FILES_FOUND' (record generation occurred, but no files matched time span)
  "user" VARCHAR(50),-- The NIST "short style" username associated with this session (if known)
  CONSTRAINT "id_session_log_UNIQUE"
    UNIQUE("id_session_log"),
  CONSTRAINT "fk_instrument"
    FOREIGN KEY("instrument")
    REFERENCES "instruments"("instrument_pid")
    ON DELETE CASCADE
    ON UPDATE CASCADE
);
CREATE INDEX "nexuslims_db"."session_log.fk_instrument_idx" ON "session_log" ("instrument");
COMMIT;
