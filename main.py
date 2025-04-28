# bot.py
import sys

from classes.tracker import Tracker
from classes.load import Load


def start_tracker(p_log):
    """
    start the follow generator in the tracker class,
    and handle mob kills detected in log
    :return: none
    """

    # instantiate helper class
    tracker = Tracker(p_log)

    print(f"Death Tracker started.")

    log_lines = tracker.follow()

    for line in log_lines:
        # if an EQ mob kill is detected in log, parse out
        # the kill time and mob name, then pass to tracker
        # class to update database
        if 'Druzzil Ro tells the guild' in line:
            kill_time = tracker.parse_time(line)
            mob_name = tracker.parse_mob(line)
            
            tracker.update_kill_time(mob_name, kill_time)


if __name__ == "__main__":
    arg = ""

    if len(sys.argv) > 1:
        arg = sys.argv[1]

    load = Load(arg)

    start_tracker(load.get_log())


# test_kill = f"[Fri Apr 18 00:45:28 2025] Druzzil Ro tells the guild, 'Cauthorn of <Seekers of Souls> has killed Essedera in Temple of Veeshan!'"
