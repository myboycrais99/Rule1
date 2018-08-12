"""
This is used to generate the stock property tables given an input file that
specifies the table name in valid sql syntax, a description of the table, and
the data type of the data to be entered.

CAUTION: THIS ONLY NEEDS TO BE RUN WHEN FIRST GENERATING THE DATABASE
"""

import numpy as np
import pymysql.cursors
import pymysql

run = False
if run:
    # read in table names, comment, and data type
    file = "rule1_tables.csv"
    table = np.genfromtxt(file, dtype="S32", delimiter="\t")

    # Connect to the database
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='rule1-password',
                                 db='rule1_test',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            for tmp in table:
                table_name = str(tmp[0].decode("windows-1252"))
                comment = str(tmp[1].decode("windows-1252"))
                val_type = str(tmp[2].decode("windows-1252"))

                idx_name = "fk_stock_{}_idx".format(table_name)
                fk_name = "fk_stock_{}".format(table_name)

                sql = (
                "CREATE TABLE `rule1_test`.`{}` (`id` INT(11) UNIQUE NOT NULL "
                "AUTO_INCREMENT,`stock_id` INT(11) NOT NULL, "
                "`year` INT(4) NOT NULL, `val` {} NOT NULL, PRIMARY KEY (`id`), "
                "INDEX `{}` (`stock_id` ASC),"
                "CONSTRAINT `{}` FOREIGN KEY (`stock_id`) "
                "REFERENCES `rule1_test`.`stocks` (`id`)"
                " ON DELETE NO ACTION ON UPDATE NO ACTION) COMMENT = '{}';"
                "").format(table_name, val_type, idx_name, fk_name, comment)

                cursor.execute(sql)
        connection.commit()

    finally:
        connection.close()
