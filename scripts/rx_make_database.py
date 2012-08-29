#!/usr/bin/env python

# Copyright (c) 2012, Regents of the University of California
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the University of California, Santa Cruz nor the
#    names of its contributors may be used to endorse or promote products
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.    

"""
For usage, run without arguments.
"""

__version__ = "0.2.3"

import sys

import dfxml

import os, sqlite3
import hashlib
import base64
from operator import itemgetter
import argparse
import traceback

#For endian conversions
import struct

SQL_CREATE_TABLE_IMAGEANNO = """
CREATE TABLE image_anno (
    image_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    sequence_name TEXT,
    sequence_prior_image INTEGER,
    last_clean_shutdown_time_hive TEXT,

    FOREIGN KEY(sequence_prior_image) REFERENCES image_anno(image_id)
);
"""

SQL_CREATE_TABLE_HIVEANALYSIS = """
CREATE TABLE hive_analysis (
    hive_id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_file TEXT,
    regxml_path TEXT,
    hive_file_path TEXT,
    hive_type TEXT,
    hive_sequence_name TEXT,
    mtime_file_system TEXT,
    mtime_latest_key TEXT,
    mtime_hive_root TEXT,
    mtime_earliest_key TEXT,
    atime_file_system TEXT,
    ctime_file_system TEXT,
    crtime_file_system TEXT,
    previous_hive_in_sequence INTEGER
);
"""

SQL_CREATE_TABLE_CELLANALYSIS = """
CREATE TABLE cell_analysis (
    hive_id INTEGER,
    cell_type TEXT,
    type TEXT,
    mtime TEXT,
    parent_key_mtime TEXT,
    metadata_first_offset INTEGER,
    data_offset INTEGER,
    value_checksum TEXT,
    metadata_length INTEGER,
    data_length INTEGER,
    previous_mtime TEXT,
    previous_parent_key_mtime TEXT,
    previous_metadata_first_offset INTEGER,
    previous_data_offset INTEGER,
    previous_metadata_length INTEGER,
    previous_data_length INTEGER,
    previous_value_checksum TEXT,
    name TEXT,
    full_path TEXT,

    FOREIGN KEY(hive_id) REFERENCES hive_analysis(hive_id)
);
"""

SQL_CREATE_INDEX_CELLANALYSIS_FULLPATH = """
CREATE INDEX full_paths ON cell_analysis (hive_id,full_path);
"""

SQL_CREATE_TABLE_HIVES_FAILED = """
CREATE TABLE hives_failed (
    hive_id INTEGER PRIMARY KEY,
    error_text TEXT
);
"""

def filetime_to_timestamp(ft):
    WINDOWS_TICK = 10000000
    SEC_TO_UNIX_EPOCH = 11644473600
    return int(ft / WINDOWS_TICK - SEC_TO_UNIX_EPOCH)

def dftime_from_filetime(ft):
    return dfxml.dftime(filetime_to_timestamp(ft))

def process_regxml_callback_object(co, current_hive_id, prev_hive_id, cursor):
    """Insert a new record into the database."""
    rh = co.registry_handle
    #Ensure mtime extrema are rh properties
    if "mtime_earliest_key" not in dir(rh):
        rh.mtime_earliest_key = None
        rh.mtime_latest_key = None
    record_dict = {}
    
    #hive_id
    record_dict["hive_id"] = current_hive_id
    
    #cell_type
    #    Only 'key' or 'value'
    if isinstance(co, dfxml.registry_key_object):
        record_dict["cell_type"] = "key"
    elif isinstance(co, dfxml.registry_value_object):
        record_dict["cell_type"] = "value"
    else:
        raise ValueError("Unexpected callback object type: " + str(type(co)))

    #We shouldn't need to check for non-key/value types from here on out.

    #type
    #    "root" or None for keys, value type for values
    record_dict["type"] = co.type()
    
    #mtime
    #	Null for values
    #Extrema are recorded in rh
    if isinstance(co, dfxml.registry_key_object):
        mtime = co.mtime()
        record_dict["mtime"] = str(mtime)
        if rh.mtime_earliest_key is None or mtime < rh.mtime_earliest_key:
            rh.mtime_earliest_key = mtime
        if rh.mtime_latest_key is None or mtime > rh.mtime_latest_key:
            rh.mtime_latest_key = mtime
    else:
        record_dict["mtime"] = None

    #parent_key_mtime
    #	Should be null for only root
    if co.parent_key:
        record_dict["parent_key_mtime"] = str(co.parent_key.mtime())
    else:
        if isinstance(co, dfxml.registry_key_object):
            if not co.root():
                raise ValueError("Orphan key found:" + str(co))
        else:
            raise ValueError("Orphan value found:" + str(co))

    #metadata_first_offset
    brs = co.byte_runs()
    if brs != None and len(brs) > 0:
        record_dict["metadata_first_offset"] = brs[0].file_offset
    else:
        record_dict["metadata_first_offset"] = None

    #data_offset
    #   Only for values; will be last byte run
    record_dict["data_offset"] = None
    if isinstance(co, dfxml.registry_value_object):
        if brs != None and len(brs) > 1:
            record_dict["data_offset"] = int(brs[-1].file_offset)

    #value_checksum
    #	Null for keys
    record_dict["value_checksum"] = None
    value_data = None
    if isinstance(co, dfxml.registry_value_object):
        record_dict["value_checksum"] = co.md5()

    #metadata_length
    #	This won't make any difference until list space is added to the processing
    record_dict["metadata_length"] = None
    if len(brs) == 1:
        record_dict["metadata_length"] = brs[0].len
    elif len(brs) > 1:
        mdl = 0
        for br in brs[:-1]:
            mdl += int(br.len)
        record_dict["metadata_length"] = mdl

    #data_length
    #	Only for values
    record_dict["data_length"] = None
    if isinstance(co, dfxml.registry_value_object):
        data_length_by_br = None
        data_length_by_data = None
        if len(brs) > 1:
            data_length_by_br = int(brs[-1].len)
        if value_data:
            data_length_by_data = len(value_data)
        record_dict["data_length"] = data_length_by_data
        #TODO Correct the data length sanity-checking.  Won't always be possible, since the byte runs won't always reflect the data length.
        #(Fortunately, until this is fixed, it gives a nice progress mark in the error log.)
        #if data_length_by_br != data_length_by_data:
        #    sys.stderr.write("Warning: Encountered a data length discrepancy: hive_id %d, full_path '%s'" % (current_hive_id, co.full_path))
        #    if data_length_by_br != None:
        #        sys.stderr.write(", by_br=%d" % data_length_by_br)
        #    if data_length_by_data != None:
        #        sys.stderr.write(", by_data=%d" % data_length_by_data)
        #    sys.stderr.write(".\n")

    #name
    record_dict["name"] = co.name()

    #full_path
    record_dict["full_path"] = co.full_path()

    #Shutdown time?
    if co.full_path().endswith("\\Control\\Windows\\ShutdownTime"):
        #Shutdown time should only come from the system hive.
        is_system_hive = False
        for row in cursor.execute("SELECT hive_type FROM hive_analysis WHERE hive_id = ?;", (current_hive_id,)):
            is_system_hive = (row["hive_type"].lower() == "system")
        if is_system_hive:
            shutdown_filetime = struct.unpack('<Q', co.value_data)[0]
            rh.time_last_clean_shutdown = dftime_from_filetime(shutdown_filetime)
        else:
            #Well, that's interesting...
            sys.stderr.write("Warning: Odd data: Found a value whose in-hive path ends with '\\Control\\Windows\\ShutdownTime', but it's not in a system hive.  (In hive %d)\n" % current_hive_id)

    #Get prior image's data
    if prev_hive_id:
        cursor.execute("SELECT * FROM cell_analysis WHERE hive_id = ? AND full_path = ?", (prev_hive_id, record_dict["full_path"]))
        previous_rec = cursor.fetchone()
        if previous_rec:
            for c in ["mtime", "metadata_first_offset", "data_offset", "metadata_length", "data_length", "value_checksum", "parent_key_mtime"]:
                if previous_rec[c]:
                    record_dict["previous_" + c] = previous_rec[c]

    #Output
    insert_db(cursor, "cell_analysis", record_dict)
    #Committing on every key fairly well kills performance.  Implement a throttled committer if desired.

def update_db(connection, cursor, table_name, update_dict, id_field, id, commit):
    if len(update_dict.keys()) > 0:
        sql_update_columns = []
        sql_update_values = []
        for k in update_dict.keys():
            sql_update_columns.append(k)
            sql_update_values.append(update_dict[k])
        sql_update_values.append(id)
        sql_update_statement = "UPDATE " + table_name + " SET " + ", ".join(map(lambda x: x + " = ?", sql_update_columns)) + " WHERE " + id_field + " = ?"
        try:
            cursor.execute(sql_update_statement, tuple(sql_update_values))
        except:
            sys.stderr.write("Failed upate.\nStatement:\t" + sql_update_statement + "\nData:\t" + str(tuple(sql_update_values)) + "\n")
            raise
        if commit:
            connection.commit()

def insert_db(cursor, table_name, update_dict):
    if len(update_dict.keys()) > 0:
        sql_insert_columns = []
        sql_insert_values = []
        for k in update_dict.keys():
            sql_insert_columns.append(k)
            sql_insert_values.append(update_dict[k])
        sql_insert_statement = "INSERT INTO " + table_name + "(" + ",".join(sql_insert_columns) + ") VALUES(" + ",".join("?" * len(sql_insert_columns)) + ");"
        try:
            cursor.execute(sql_insert_statement, tuple(sql_insert_values))
        except:
            sys.stderr.write("Failed insertion.\nStatement:\t" + sql_insert_statement + "\nData:\t" + str(tuple(sql_insert_values)) + "\n")
            raise

def hive_type_from_path(dfxml_hive_path, collapse_names=True):
    """
    collapse_names=True -> Correct the hive type for "User" accounts.
    We should end up with only these path prefixes for ntuser.dat and
    usrclass.dat (modulo capitalization):
        Administrator/
        All Users/
        Non-default user/
        Default user/
        Default/
        LocalService/
        NetworkService/
        Repair/
        SystemProfile/
    
    Other hives' types are just the basename.
    """
    dfxml_hive_path_parts = dfxml_hive_path.split("/")
    names_to_preserve = ["administrator", "all users", "default user", "default", "localservice", "networkservice", "repair", "systemprofile"]
    name_mask = "Non-default user"
    if dfxml_hive_path_parts[-1].lower() == "ntuser.dat":
        if len(dfxml_hive_path_parts) >= 2:
            if collapse_names and not dfxml_hive_path_parts[-2].lower() in names_to_preserve:
                hive_type = "/".join([name_mask, dfxml_hive_path_parts[-1]])
            else:
                hive_type = "/".join(dfxml_hive_path_parts[-2:])
        else:
            sys.stderr.write("Warning: Can't properly categorize hive from ntuser.dat hive's file-system path:\t%s\n" % (dfxml_hive_path,))
            hive_type = dfxml_hive_path_parts[-1]
    elif dfxml_hive_path_parts[-1].lower() == "usrclass.dat":
        if len(dfxml_hive_path_parts) >= 6:
            if collapse_names and not dfxml_hive_path_parts[-6].lower() in names_to_preserve:
                hive_type = "/".join([name_mask, dfxml_hive_path_parts[-1]])
            else:
                hive_type = "/".join([dfxml_hive_path_parts[-6], dfxml_hive_path_parts[-1]])
        else:
            sys.stderr.write("Warning: Can't properly categorize hive from usrclass.dat hive's file-system path:\t%s\n" % (dfxml_hive_path,))
            hive_type = dfxml_hive_path_parts[-1]
    else:
        hive_type = dfxml_hive_path_parts[-1]
    return hive_type

def main():
    parser = argparse.ArgumentParser(prog="rx_make_database.py", description="Convert RegXML files from disk sequences to a single SQLite database of Registry cells.")
    parser.add_argument("successful_regxml_list", action="store", help="The regxml list should only have regxml files from successfully completed producing processes (such as hivexml checked with xmllint).  Files should be given as absolute paths.")
    parser.add_argument("hive_meta_list", action="store", help="The hive meta list should have absolute paths to RegXML files, with each line containing a hive file absolute path, the hive's full in-image path as given in DFXML, and its maccr times (in that order).")
    parser.add_argument("output_database_file", action="store", help="Outut database must not exist.")
    parser.add_argument("--drive_sequence_listing", required=False, action="store", help="The drive sequence listing should have one line per drive image, and the following line being either the next image taken of that drive, or a blank line to indicate the drive's timeline is complete.  A sequence line should have two tab-delimited fields, first the image name, second the name of the image sequence.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")
    args = parser.parse_args()
    if os.path.exists(args.output_database_file):
        parser.print_help()
        exit(1)
    
    #Identify disk image sequences
    """Key: image base name.  Value: immediately-preceding image."""
    image_sequence_priors = {}
    """Key: image base name.  Value: Line number in the sequence file."""
    image_sequence_numbers = {}
    """Key: image base name.  Value: image sequence name."""
    image_sequence_names = {}
    working_with_priors = False

    #Populate disk image sequence index if optional parameter is passed
    if args.drive_sequence_listing is not None:
        working_with_priors = True
        image_sequences = [[]]

        sequence_file = open(args.drive_sequence_listing, "r")
        for (line_no, line) in enumerate(sequence_file):
            line_cleaned = line.strip()
            if line_cleaned == "":
                image_sequences.append([])
            else:
                line_parts = line_cleaned.split("\t")
                image_sequences[-1].append(line_parts[0])
                image_sequence_numbers[line_parts[0]] = line_no
                if len(line_parts) > 1:
                    image_sequence_names[line_parts[0]] = line_parts[1]
        sequence_file.close()
        for image_sequence in image_sequences:
            last_image = None
            for image in image_sequence:
                image_sequence_priors[image] = last_image
                last_image = image

    #Produce a list of the RegXML files that completed
    #List does double-duty as a map from a regxml file to the hive file from which it was derived.
    successful_regxmls = {}
    successful_regxml_file = open(args.successful_regxml_list, "r")
    for line in successful_regxml_file:
        cleaned_line_parts = line.strip().split("\t")
        if len(cleaned_line_parts) == 2:
            hive_path = cleaned_line_parts[0]
            xml_path = cleaned_line_parts[1]
        elif len(cleaned_line_parts) == 0:
            continue
        else:
            raise Exception("Unexpected number of line components when reading hive-regxml mapping:\nrepr(line) = " + repr(line))
        successful_regxmls[hive_path] = xml_path
    if args.verbose:
        print("Successful hive file-RegXML pairs:")
        print("\n".join([(k,successful_regxmls[k]) for k in successful_regxmls]))

    #Produce a list of the images to use
    work_list_unordered = []

    image_list_file = open(args.hive_meta_list, "r")
    for line in image_list_file:
        cleaned_line = line.strip()
        if cleaned_line != "":
            hive_dump_path, image_file, dfxml_hive_path, hive_mtime, hive_atime, hive_ctime, hive_crtime = cleaned_line.split("\t")
            if hive_dump_path in successful_regxmls:
                regxml_path = successful_regxmls[hive_dump_path]
                if working_with_priors:
                    #We want all the input drives to have a prior image or None explicitly specified.  So, don't use .get().
                    prior_image = image_sequence_priors[image_file]
                else:
                    prior_image = None
                work_list_unordered.append({"regxml_path":regxml_path, "dfxml_hive_path":dfxml_hive_path, "image_file":image_file, "prior_image":prior_image, "mtime":hive_mtime, "atime":hive_atime, "ctime":hive_ctime, "crtime":hive_crtime, "image_sequence_number":image_sequence_numbers.get(image_file)})
    image_list_file.close()
    #Order by manifest listing.
    if working_with_priors:
        work_list = sorted(work_list_unordered, key=itemgetter("image_sequence_number"))
    else:
        #Ingest order will do fine in the single-image case.
        work_list = work_list_unordered
    if args.verbose:
        print("In-order work list we are processing:")
        print("\n".join(map(str, work_list)))

    #Begin the SQL database
    conn = sqlite3.connect(args.output_database_file)
    conn.isolation_level = "EXCLUSIVE"
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    #Begin the SQL tables
    cursor.execute(SQL_CREATE_TABLE_IMAGEANNO)
    cursor.execute(SQL_CREATE_TABLE_HIVEANALYSIS)
    cursor.execute(SQL_CREATE_TABLE_HIVES_FAILED)
    cursor.execute(SQL_CREATE_TABLE_CELLANALYSIS)
    cursor.execute(SQL_CREATE_INDEX_CELLANALYSIS_FULLPATH)

    #Populate
    for work_order in work_list:
        current_image_id = None
        #Maybe make a new image record
        cursor.execute("SELECT * FROM image_anno WHERE name = ?", (work_order["image_file"],))
        for row in cursor:
            current_image_id = row["image_id"]
            break
        if current_image_id == None:
            #Create new record
            image_anno_new_record = {}

            #image name
            image_anno_new_record["name"] = work_order["image_file"]

            #image sequence name
            image_anno_new_record["sequence_name"] = image_sequence_names.get(image_anno_new_record["name"])

            #image sequence prior
            cursor.execute("SELECT image_id FROM image_anno WHERE name = ?", (work_order["prior_image"],))
            for row in cursor:
                image_anno_new_record["sequence_prior_image"] = row["image_id"]
                break

            #Insert
            insert_db(cursor, "image_anno", image_anno_new_record)
            conn.commit()

            #Fetch fresh id
            for row in cursor.execute("SELECT * FROM image_anno WHERE rowid = ?;", (cursor.lastrowid,)):
                current_image_id = row["image_id"]

        #Make a new hive record
        dfxml_hive_path = work_order["dfxml_hive_path"]
        hive_type = hive_type_from_path(dfxml_hive_path, True)
        hive_sequence_name = hive_type_from_path(dfxml_hive_path, False)
        cursor.execute(
            "INSERT INTO hive_analysis(image_file, regxml_path, hive_file_path, hive_type, hive_sequence_name, mtime_file_system, atime_file_system, ctime_file_system, crtime_file_system) VALUES (?,?,?,?,?,?,?,?,?);",
            (work_order["image_file"], work_order["regxml_path"], dfxml_hive_path, hive_type, hive_sequence_name, work_order["mtime"], work_order["atime"], work_order["ctime"], work_order["crtime"])
        )
        conn.commit()
        
        #Get hive id
        current_hive_id = None
        cursor.execute("SELECT * FROM hive_analysis WHERE rowid = ?;", (cursor.lastrowid,))
        current_rec = cursor.fetchone()
        current_hive_id = current_rec["hive_id"]
        if current_hive_id == None:
            raise ValueError("Couldn't get last hive_id, somehow.")

        #Get previous hive in sequence
        previous_hive_id = None
        if working_with_priors:
            #Note we're not using .get() - we want an error raised if we have a broken sequence.
            previous_image_file = image_sequence_priors[work_order["image_file"]]
            for r in cursor.execute("SELECT hive_id FROM hive_analysis WHERE image_file = ? AND hive_file_path = ?", (previous_image_file, work_order["dfxml_hive_path"])):
                previous_hive_id = r["hive_id"]
            cursor.execute("UPDATE hive_analysis SET previous_hive_in_sequence = ? WHERE hive_id = ?;", (previous_hive_id, current_hive_id))

        #Commit updates for hive_analysis
        conn.commit()

        #Process the RegXML into cell records, capturing notes on failure
        reader = None
        try:
            reader = dfxml.read_regxml(xmlfile=open(work_order["regxml_path"], "rb"), callback=lambda co: process_regxml_callback_object(co, current_hive_id, previous_hive_id, cursor))
        except:
            sql_insert_failure = "INSERT INTO hives_failed(hive_id, error_text) VALUES (?, ?);"
            cursor.execute(sql_insert_failure, (current_hive_id, traceback.format_exc()))
        conn.commit() #Ensure the last updates made it in

        #Update the hive and image records with the necessarily-computed times
        if reader is not None:
            image_updates = {}
            hive_column_value_updates = {}
            hive_column_value_updates["mtime_hive_root"] = str(reader.registry_object.mtime())
            if "mtime_latest_key" in dir(reader.registry_object):
                hive_column_value_updates["mtime_latest_key"] = str(reader.registry_object.mtime_latest_key)
            if "mtime_earliest_key" in dir(reader.registry_object):
                hive_column_value_updates["mtime_earliest_key"] = str(reader.registry_object.mtime_earliest_key)
            if "time_last_clean_shutdown" in dir(reader.registry_object):
                image_updates["last_clean_shutdown_time_hive"] = str(reader.registry_object.time_last_clean_shutdown)

            #Update tables
            update_db(conn, cursor, "hive_analysis", hive_column_value_updates, "hive_id", current_hive_id, True)
            update_db(conn, cursor, "image_anno", image_updates, "image_id", current_image_id, True)
        sys.stderr.write("Note:  Just finished with hive %d.\n" % current_hive_id)

    #TODO Also add to the where clause that this should not run on Vista systems.  This means digging for that key that notes where the system type is, I know Carvey noted it...

    #Now we have data...but possibly too much.
    cursor.execute("SELECT COUNT(*) FROM cell_analysis WHERE hive_id IN (SELECT hive_id FROM hives_failed);")
    row = cursor.fetchone()
    if row[0] > 0:
        sys.stderr.write("Note:  Deleting %d rows from cell_analysis due to processing for hives failing.\n" % row[0])
    cursor.execute("DELETE FROM cell_analysis WHERE hive_id IN (SELECT hive_id FROM hives_failed);")

    #Now it's just right.
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
