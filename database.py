from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from os import environ


class Database:
    """
    This class provides all database interaction
    """

    def __init__(self):
        load_dotenv()

        # obtain database parameters securely as environment variables
        self._MYSQL_USER = environ.get('MYSQL_USER')
        self._MYSQL_PASSWORD = environ.get('MYSQL_PASSWORD')
        self._MYSQL_HOST = environ.get('MYSQL_HOST')
        self._MYSQL_DB = environ.get('MYSQL_DB')

        # set connection string
        self._params = f"mysql+pymysql://{self._MYSQL_USER}:{self._MYSQL_PASSWORD}@{self._MYSQL_HOST}/{self._MYSQL_DB}?charset=utf8mb4"

    def get_mob_data(self, mob_name):
        """
        obtain all fields of a mob's database entry
        :param mob_name: string
        :return: results of the select query, in list form
        """
        query = f"SELECT * FROM sos_bot.respawns WHERE mob_name = '{mob_name}'"

        return self.execute_read(query)

    def update_kill_time(self, mob_name, kill_time, respawn_time, time_zone):
        """
        edit database entry for a given mob with new kill time,
        respawn time, and time zone
        :param mob_name: string
        :param kill_time: datetime in string format
        :param respawn_time: datetime in string format
        :param time_zone: string
        :return: results of the update query, in list form
        """

        mob_name = self.format_quotes(mob_name)

        query = (
            f"UPDATE sos_bot.respawns SET kill_time = '{kill_time}', respawn_time = '{respawn_time}', "
            f"time_zone = '{time_zone}' WHERE mob_name = '{mob_name}'"
        )

        return self.execute_update(query)

    ################# UTILITY METHODS #################
    def create_engine(self):
        """
        create a new engine object upon request, to prevent
        MySQL server from timing out
        :return: SQL alchemy engine object
        """
        # create the query engine
        return create_engine(self._params)

    def execute_read(self, query):
        """
        Send a read query to database engine
        :query: the formatted query string to send
        to database engine
        :return: results of the operation, in list form
        """
        records_list = []

        # open a connection to database, dynamically close
        # it when with block closes
        with self.create_engine().connect() as conn:
            result = conn.execute(text(query))

            # get query results and, line by line,
            # convert to dict entries; add each
            # dict to list
            for row in result.all():
                row_to_dict = row._asdict()
                records_list.append(row_to_dict)

            conn.close()

        return records_list

    def execute_update(self, query):
        """
        Send an update query to database engine
        :query: the formatted query string to send
        to database engine
        :return: int, representing the results of the operation
        """
        # open a connection to database, dynamically close
        # it when with block closes
        with self.create_engine().connect() as conn:
            # get a count of rows affected, to act as
            # indicator of success or failure
            result = conn.execute(text(query)).rowcount
            conn.commit()

            conn.close()

        return result

    def format_quotes(self, mob_name):
        quote_index = mob_name.find("'")

        if quote_index != -1:
            temp_string = mob_name
            mob_name = temp_string[:quote_index] + "'" + temp_string[quote_index:]

        return mob_name
