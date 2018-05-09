from collections import defaultdict
import sys
import json
import boto3
import random
from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.row_event import (
    DeleteRowsEvent,
    UpdateRowsEvent,
    WriteRowsEvent,
    TableMapEvent
)
import datetime
import pymysql
import json

from daemonize import Daemonize
pid = "/tmp/stream_mysql_logs.pid"

def upload_to_s3( s3, file_name, data ):
    key = db_name + '/stream/' + file_name
    print "uploading to s3 " + key + "..."
    s3.Bucket(bucket_name).put_object(Key=key, Body=json.dumps([record for record in data if record is not None]))

def binlog_event_to_json(binlog_event):
    if isinstance(binlog_event, WriteRowsEvent):
        return {
            'table': binlog_event.table,
            'action': 'insert', 
            'records': map( lambda row: row["values"], binlog_event.rows ) 
        } 
    elif isinstance(binlog_event, UpdateRowsEvent):
        return {
            'table': binlog_event.table,
            'action': 'update', 
            'records': map( lambda row: row["after_values"], binlog_event.rows ) 
        } 
    elif isinstance(binlog_event, DeleteRowsEvent):
        return {
            'table': binlog_event.table,
            'action': 'delete', 
            'records': map( lambda row: row["values"], binlog_event.rows ) 
        } 
            
def s3_file_name( log_name, log_pos):
    return log_name + "-" + str(log_pos) + ".json"

##
# main streams the events into a buffer and empties it
def main():
    configuration = {'log_file': 'mysql-bin-changelog.004416', 'log_pos': 0}
    
    for config in open('configuration').read().split('\n'):
        config_k_v = config.split('=')
        configuration[config_k_v[0]] = config_k_v[1]

    MYSQL_SETTINGS = {
        "host": configuration['hostname'],
        "port": 3306,
        "user": configuration['username'],
        "password": configuration['password'],
        "database": configuration['database']
    }

    print configuration

    stream = BinLogStreamReader(
        connection_settings=MYSQL_SETTINGS,
        server_id=1234, 
        log_file=configuration['log_file'],
        log_pos=configuration['log_pos'],
        blocking=True,
        only_events=[WriteRowsEvent, UpdateRowsEvent, DeleteRowsEvent]
    )

    s3 = boto3.resource('s3')
    buffer_events = []
    buffer_max_size = 1
    
    cur_log_file = ''
    cur_log_pos = ''
    
    for binlog_event in stream:
        cur_log_file = stream.log_file
        cur_log_pos = stream.log_pos

        print "Processing " + cur_log_file + " at " + str(cur_log_pos)
        
        buffer_events.append( binlog_event )
        if len(buffer_events) == buffer_max_size:
            upload_to_s3( s3, s3_file_name(cur_log_file, cur_log_pos),  map(lambda binlog_event: binlog_event_to_json(binlog_event), buffer_events))
            buffer_events = []
                
    stream.close()
    if len(buffer) > 0:
        upload_to_s3( s3, s3_file_name(cur_log_file, cur_log_pos),  map(lambda binlog_event: binlog_event_to_json(binlog_event, table), buffer_events))

daemon = Daemonize(app="stream_mysql_logs", pid=pid, action=main)
daemon.start()
