"""

"""
import pymysql


def connect_db():
    # Connect to the database
    conn = pymysql.connect(host='localhost',
                           user='root',
                           password='rule1-password',
                           db='rule1_test',
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)

    return conn


def get_valid_website_names(conn=connect_db()):
    sql = "SELECT website_table_name FROM table_map"

    valid_names = list()

    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)

            for row in cursor:
                # print(row.values(), "Unusual Expense (Income)" in row.values())
                valid_names.append(list(row.values())[0])

    finally:
        cursor.close()

    return valid_names

if __name__ == "__main__":
    pass

    connection = connect_db()

    print(get_valid_website_names())
