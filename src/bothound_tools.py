"""
Utility class that holds commonly used Bothound functions

"""
import numpy as np

import MySQLdb

from geoip import geolite2

class BothoundTools():
    def connect_to_db(self):
        """
        This connetcion to the db will live for the live time of the
        learn2bantools instance and will be used to save data back to the db
        """
        self.db = MySQLdb.connect(self.db_host, self.db_user, self.db_password)

        #Create cursor object to allow query execution
        self.cur = self.db.cursor(MySQLdb.cursors.DictCursor)
        sql = 'CREATE DATABASE IF NOT EXISTS ' + self.db_name
        self.cur.execute(sql)

	    #Connect directly to DB
        self.db = MySQLdb.connect(self.db_host, self.db_user, self.db_password, self.db_name)
        self.cur = self.db.cursor(MySQLdb.cursors.DictCursor)

        # ATTACKS table
        self.cur.execute("create table IF NOT EXISTS attacks (id INT NOT NULL AUTO_INCREMENT, "
        "comment LONGTEXT, "
        "PRIMARY KEY(id)) ENGINE=INNODB;")

       # INCIDENTS table
        self.cur.execute("create table IF NOT EXISTS incidents (id INT NOT NULL AUTO_INCREMENT, "
        "id_attack INT NOT NULL,"
        "start_timestamp DATETIME, "
        "stop_timestamp DATETIME, "
        "comment LONGTEXT, "
        "PRIMARY KEY(id), INDEX index_attack (id_attack), "
        "FOREIGN KEY (id_attack) REFERENCES attacks(id) ON DELETE CASCADE ) ENGINE=INNODB;")
        
        # SESSIONS table
        self.cur.execute("create table IF NOT EXISTS sessions (id INT NOT NULL AUTO_INCREMENT, "
        "id_incident INT NOT NULL, "
        "IP VARCHAR(45), "
        "request_interval FLOAT, "
        "ua_change_rate FLOAT, "
        "html2image_ratio FLOAT, "
        "variance_request_interval FLOAT, "
        "payload_average FLOAT, "
        "error_rate FLOAT, "
        "request_depth FLOAT, "
        "request_depth_std FLOAT, "
        "session_length FLOAT, "
        "percentage_cons_requests FLOAT,"
        "PRIMARY KEY(id), INDEX index_incicent (id_incident),  "    
        "FOREIGN KEY (id_incident) REFERENCES incidents(id) ON DELETE CASCADE ) ENGINE=INNODB;")

 
    def disconnect_from_db(self):
        """
        Close connection to the database
        """
        self.cur.close()
        self.db.close()

    def load_database_config(self, database_conf):        
        self.db_user = database_conf["user"]
        self.db_password = database_conf["password"]
        self.db_host = database_conf["host"]
        self.db_name = database_conf["name"]

    def random_slicer(self, data_size, train_portion=0.5):
        """
        Return two arrays with random true and false and complement of each
        other, used for slicing a set into trainig and testing

        INPUT:
            data_size: size of the array to return
            train_portion: between 0,1 indicate the portion for the True
                           entry
        """
        from random import random
        random_selector = [random() < train_portion for i in range(0, data_size)]
        complement_selector = np.logical_not(random_selector)

        return random_selector, complement_selector
    """
    This method requires installation of the following packages.
    It downloads the entire geo-location database, so its accessible offline. 
    pip install python-geoip
    pip install python-geoip-geolite2
    """
    def find_location(self, ip):
        match = geolite2.lookup(ip)
        return match.location
    
    def __init__(self, database_conf):
        #we would like people to able to use the tool object even
        #if they don't have a db so we have no reason to load this
        #config in the constructor
        self.load_database_config(database_conf)
        pass