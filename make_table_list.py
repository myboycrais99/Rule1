"""


CAUTION: THIS ONLY NEEDS TO BE RUN WHEN FIRST GENERATING THE DATABASE
"""

import numpy as np
import pymysql

def make_table_list(connection, table):
    try:
        with connection.cursor() as cursor:
            for tmp in table:
                sql = ("INSERT INTO `rule1_test`.`table_names` (`name`) "
                      "VALUES ('{}');").format(tmp[0].decode('utf8'))
                cursor.execute(sql)
        connection.commit()

    finally:
        print("success")
        connection.close()


def make_table_map(connection, table):
    try:
        with connection.cursor() as cursor:
            for tmp in table:
                sql = (
                "INSERT INTO table_map SET website_table_name = '{}', "
                "table_name_id = (SELECT id FROM table_names WHERE "
                "name = '{}')"
                "").format(tmp[1].decode("utf8"),
                           tmp[0].decode("utf8"))

                cursor.execute(sql)
        connection.commit()

    finally:
        print("success")
        connection.close()

run = True
if run:
    # read in table names, comment, and data type
    file = "mapping.csv"
    table = np.genfromtxt(file, dtype="S60", delimiter="\t")

    for i, val in enumerate(table):
        val[0].decode('utf8')
        try:
            val[1].decode('utf8')
        except UnicodeDecodeError:
            print(val[1])
            table[i][1] = val[1].decode("windows-1252").replace("\u2013", "-")

    print(table)

    # Connect to the database
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='rule1-password',
                                 db='rule1_test',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    make_table_list(connection, table)

    # make_table_map(connection, table)
