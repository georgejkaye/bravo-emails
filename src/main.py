#!/usr/bin/python3

from config import GENERATE, load_config, ANNOUNCE, REMINDER, ABSTRACT
from scraper import get_next_talk
from emails import write_email, send_email
from debug import debug
from bot import post_to_discord
import datetime
import sys


def find_talk_and_send_email(config, seminar, mode):

    if mode == ANNOUNCE or mode == GENERATE:
        template = "announce.txt"
    elif mode == REMINDER:
        template = "reminder.txt"

    next_talk = get_next_talk(config, seminar)

    if next_talk is not None:
        email = write_email(config, seminar, template, next_talk)
        if mode == GENERATE:
            print(email)
        else:
            send_email(config, next_talk, seminar, email, mode)
            post_to_discord(config, next_talk, seminar, mode)
    else:
        debug(config, f"{seminar.name}: No upcoming talk")


def check_abstract(config, seminar):
    next_talk = get_next_talk(config, seminar)

    if next_talk is not None:
        template = "abstract.txt"
        email = write_email(config, seminar, template, next_talk)

        send_email(config, next_talk, seminar, email, ABSTRACT)
    else:
        debug(config, f"{seminar.name}: No upcoming talk")


def main(config_file, log_file):

    today = datetime.datetime.today()

    config = load_config(config_file, log_file)

    for seminar in config.seminars:

        if today.weekday() == seminar.announce.day:
            mode = ANNOUNCE
            time = seminar.announce.time
        elif today.weekday() == seminar.reminder.day:
            mode = REMINDER
            time = seminar.reminder.time
        elif today.weekday() == seminar.abstract.day:
            mode = ABSTRACT
            time = seminar.abstract.time
        else:
            debug(
                config, f"{seminar.name}: Not the right day to send an email")
            continue
        # Parse the time from the config
        time = datetime.datetime.strptime(time, "%H:%M")
        # We can't be too precise as it might take a few seconds to load the script
        if today.hour == time.hour and today.min == time.min:
            if mode == ABSTRACT:
                check_abstract(config, seminar)
            else:
                find_talk_and_send_email(config, seminar, mode)
        else:
            debug(
                config, f"{seminar.name}: Not the right time to send an email")
            continue


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main.py <config file> <log file>")
        exit(1)
    main(sys.argv[1], sys.argv[2])
