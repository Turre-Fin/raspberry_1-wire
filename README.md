# raspberry_1-wire
Code for reading 1w-sensors, values to mysql or error log-file as sql-statements in case of DB connection error.
2020-03-23
    -(Temperature-sensor sql)INSERT INTO ow_sensodata (sensorID, timestamp, temperature, temphigh, templow) VALUES (...)
    -(dualCounter-sensor sql)INSERT INTO ow_sensodata (sensorID, timestamp, counterA, CounterB) VALUES (...)

    -At this time only reads sensor addresses starting as "10-"(Temperature sensors) and "1d-"(dual /-counters)
    -Writes sensor values straight into mysql-db. While no connection writes in log file which will be written into db before any new values are added when connection returns.
    
