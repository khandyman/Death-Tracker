import time
from datetime import datetime, timedelta
from classes.database import Database


class Tracker:
    """
    This class provides a generator for real time log file parsing
    and logic to calculate respawn times, scrape data from the Quarm
    database, and interact with the bot database
    """
    def __init__(self, log_file):
        self._database = Database()
        # log file path to track
        self._file_path = log_file
        self._file = open(self._file_path, 'r')

    def follow(self):
        """
        a generator function to read the last line of a
        log file, as it is written, and yield that line
        to the caller
        :yield: the line that was just written to the log
        """
        print(f"Monitoring log file located at:\n"
              f"{self._file_path}")

        # set cursor position to end of file
        self._file.seek(0,2)

        # infinite loop
        while True:
            line = self._file.readline()

            # if no line written, pause briefly, then rescan
            if not line:
                time.sleep(0.1)
                continue

            # if new line exists, yield it back to caller and
            # pause generator
            yield line

    def parse_time(self, line):
        """
        method to parse just the time data at the beginning
        of an EQ log file line
        :param line: string
        :return: string
        """
        # split the line into a list of words
        separates = line.split()

        # convert the month from abbreviated text to an int
        month_int = str(datetime.strptime(separates[1], "%b").month).zfill(2)

        # create a new string with specific formatting, using pre-defined
        # indexes in the separated list created above
        kill_time = f"{separates[4].strip("]")}-{month_int}-{separates[2]} {separates[3]}"

        return kill_time

    def parse_mob(self, line):
        """
        method to parse the mob name from an
        an EQ log file line
        :param line: string
        :return: string
        """
        # set the starting index
        mob_start = line.find(' killed ') + 8
        # set the ending index
        mob_end = line.find(' in ')

        # slice out the mob name, could be multiple words
        mob_name = line[mob_start:mob_end]

        return mob_name

    def update_kill_time(self, mob_name, kill_time):
        """
        edit the database entry for a mob with new kill and respawn times
        :param mob_name: string
        :param kill_time: string
        :return: formatted string
        """
        # kill_time = "Thu Apr 17 23:57:03 2025"        # an example of the incoming kill_time format

        # get the respawn time from the calculate respawn method
        respawn_time = self.calculate_respawn(mob_name, kill_time)

        # get the time zone of the PC the mule is logged in on
        time_zone = datetime.now().astimezone().tzname()

        # print to console, to indicate a new log file capture
        print(f"{mob_name} | {kill_time} | {respawn_time} | {time_zone}")

        # attempt to update the database, print success or
        # failure message to console
        if self._database.update_kill_time(mob_name, kill_time, respawn_time, time_zone):
            kill_message = f"```Database insert of kill time for {mob_name} succeeded.```"
        else:
            kill_message = f"```Database insert of kill time for {mob_name} failed.```"

        print(kill_message)

    def calculate_respawn(self, mob_name, kill_time):
        """
        add the respawn time for a mob to its latest kill time
        :param mob_name: string
        :param kill_time: datetime in string format
        :return:
        """
        # set the format of the datetime string
        format_string = "%Y-%m-%d %H:%M:%S"
        # convert it into an actual datetime object
        datetime_killtime = datetime.strptime(kill_time, format_string)

        # get the respawn time units of a mob from database
        mob_data = self._database.get_mob_data(mob_name)

        # convert to ints, for arithmetic
        delta_weeks = int(mob_data[0]['lockout_weeks'])
        delta_days = int(mob_data[0]['lockout_days'])
        delta_hours = int(mob_data[0]['lockout_hours'])
        delta_minutes = int(mob_data[0]['lockout_minutes'])

        # create a time delta object with the time units obtained from database
        add_time = timedelta(
            weeks=delta_weeks,
            days=delta_days,
            hours=delta_hours,
            minutes=delta_minutes
        )

        # add the time delta to the kill time
        respawn_time = datetime_killtime + add_time

        return respawn_time
