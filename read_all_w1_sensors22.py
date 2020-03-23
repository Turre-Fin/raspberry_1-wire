import mysql.connector
import glob, time
from datetime import datetime
import smtplib
import os

db_user = "owfsScript"
db_passwd = "Rasse123!!!"
db_host = "192.168.153.10"
db_db = "ow_results"

#Fetch sensor ID's into db
Fetch_IDs = False

#Set debug [False | True]
DEBUG = True

#Reading interval in seconds
w1_read_interval = 10

#Set temperature_scale [C | F]
temperature_scale = 'C'


#Email alert settings (Not yet in use in this file)
"""
EMAIL_ALERT = False
GMAIL_USER = 'testuser@gmail.com'
GMAIL_PASS = ''
SMTP_SERVER = ''
SMTP_PORT = 587
recipient = ''

device_name_for_email_alert = 'Rastemppi'
"""


def read_1w_sensors():
    basedir = '/sys/bus/w1/devices/'
    device_folder = glob.glob(basedir + '??-*')
    Number_Of_sensors = len(device_folder)
    item_counter = 0

    """if Fetch_IDs:
        sql = "TRUNCATE sensorid"
        write_mysql(sql)
        while item_counter < len(device_folder):
            sql = INSERT INTO sensorid (sensorID) VALUES 
            values = device_folder[item_counter][len(basedir):]
            write_mysql(sql + "(" + values + ")")
            item_counter = item_counter+1
        item_counter = 0"""

    while item_counter < Number_Of_sensors:
        raw_data = read_raw_data(device_folder[item_counter])

#Temperature sensor data fetch (2rows)
        if device_folder[item_counter][len(basedir):][0:3] == "10-":
            sql = """INSERT INTO sensordata (sensorID,timestamp,temperature,temphigh,templow) VALUES """
            values = read_temp(device_folder[item_counter], basedir, raw_data)

#Counter sensor data fetch (4rows)
        if device_folder[item_counter][len(basedir):][0:3] == "1d-":
            sql = """INSERT INTO sensordata (sensorID,timestamp,counterA,counterB) VALUES """
            values = read_counter(device_folder[item_counter], basedir, raw_data)

        write_mysql(sql + "(" + values + ")")
        item_counter = item_counter+1


def read_raw_data(device_folder):
    device_file = device_folder + '/w1_slave'
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp(device_folder,basedir, raw_data):
    d = datetime.now()
    timestamp = "{:%Y-%m-%d %H:%M:%S}".format(d)
    temp_c = 0
    temphigh = 35.1
    templow = 16.1

    if len(raw_data) == 2:

        #while lines[0].strip()[-3:] !='YES':
        time.sleep(0.2)
        #lines = read_raw_data()
        equals_pos = raw_data[1].find('t=')
        if equals_pos != -1:
            temp_string = raw_data[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0

    return_string = "'" + device_folder[len(basedir):] + "','" + timestamp + "'," + str(temp_c) + "," + str(temphigh) +"," + str(templow)
    if temperature_scale == 'F':
        return_string = "'" + device_folder[len(basedir):] + "','" + timestamp + "'," + str(temp_f) + "," + str(temphigh) +"," + str(templow)

    return return_string


def read_counter(device_folder,basedir, raw_data):
    d = datetime.now()
    timestamp = "{:%Y-%m-%d %H:%M:%S}".format(d)
    raw_data
    counter_string = [0,0,0,0]

    if len(raw_data) == 4:

        equals_pos = raw_data[0].find('crc=YES c=')
        if equals_pos != -1:
            counter_string[0] = raw_data[0][equals_pos+10:-1]
        equals_pos = raw_data[1].find('crc=YES c=')
        if equals_pos != -1:
            counter_string[1] = raw_data[1][equals_pos+10:-1]
        equals_pos = raw_data[2].find('crc=YES c=')
        if equals_pos != -1:
            counter_string[2] = raw_data[2][equals_pos+10:-1]
        equals_pos = raw_data[3].find('crc=YES c=')
        if equals_pos != -1:
            counter_string[3] = raw_data[3][equals_pos+10:-1]

    return_string = "'" + device_folder[len(basedir):] + "','" + timestamp + "'," + str(counter_string[2]) + "," + str(counter_string[3])
    return return_string


def write_mysql(sql):
    error_log_file = '/home/pi/mysql_error_data_log'


    if os.path.exists(error_log_file):
        write_log_temp_on_mysql_error(error_log_file, sql)

    else:
        try:
            db = mysql.connector.connect(user=db_user, passwd=db_passwd, host=db_host, database=db_db)
            cursor = db.cursor()
            cursor.execute(sql)
            db.commit()
            cursor.close()
            db.close()
            if DEBUG:
                print("Normal mode")

        except:
            if DEBUG:
                print("No db connection")
            write_log_temp_on_mysql_error(error_log_file, sql)


def write_log_temp_on_mysql_error(error_log_file, sensor_data):
    error_file_line_counter = 0


    f = open(error_log_file, "a+t")
    f.write(sensor_data + '\n')
    f.close()
    if DEBUG:
        print("Writing into the error_log_file")

    try:
        if os.path.exists(error_log_file):
            f = open(error_log_file, 'r+t')
            error_lines = f.readlines()
            f.close()

            db = mysql.connector.connect(user=db_user, passwd=db_passwd, host=db_host, database=db_db)
            cursor = db.cursor()

            while error_file_line_counter < len(error_lines):
                sql = error_lines[error_file_line_counter]

                if DEBUG:
                    print("Writing error_log_file into DB")

                cursor.execute(sql)
                db.commit()

                if error_file_line_counter == len(error_lines)-1:
                    os.remove(error_log_file)
                    if DEBUG:
                        print("Failsafe end")
                error_file_line_counter = error_file_line_counter + 1

            cursor.close()
            db.close()

    except:
        pass


def send_alert_email():
    pass
    """try:
         subject = device_name_for_email_alert' in trouble'
         text = 'Cannot deliver sensor data reliably'
         smtpserver = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
         smtpserver.ehlo()
         smtpserver.starttls()
         smtpserver.ehlo
         smtpserver.login(GMAIL_USER, GMAIL_PASS)
         header = 'To:' + recipient + '\n' +'From:' + GMAIL_USER + '\n' + 'Subject:' + subject + '\n'
         msg = header + '\n' + text + '\n\n'
         smtpserver.sendmail(GMAIL_USER, recipient, msg)
         smtpserver.close()
    except:
        pass"""


while True:

    read_1w_sensors()
    time.sleep(w1_read_interval)
