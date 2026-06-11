#!/usr/bin/env python3
"""Simple key logger simulation.

This script captures keystrokes entered in the terminal, writes them to a local file,
and then analyzes the file to demonstrate how logging data can expose sensitive input.

Use only in a controlled environment for learning. Do not use this script to capture
keystrokes from other users without consent.
"""

import os
import sys
import time
import termios
import tty

LOG_FILE = os.path.join(os.path.dirname(__file__), "keylog.txt")

SENSITIVE_KEYWORDS = [
    "password",
    "secret",
    "ssn",
    "credit",
    "card",
    "login",
    "pin",
    "otp",
]


def capture_keystrokes(log_file=LOG_FILE):
    """Capture keystrokes from the terminal and append them to a log file."""
    print("Key logger simulation started.")
    print("Type keys in this terminal. Press Ctrl-C to stop.")

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    with open(log_file, "a", encoding="utf-8") as file_handle:
        file_handle.write(f"\n--- Session started {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        file_handle.flush()

        try:
            tty.setraw(fd)
            while True:
                char = sys.stdin.read(1)
                if not char:
                    break

                if char == "\x03":
                    raise KeyboardInterrupt

                if char == "\r":
                    char = "\n"

                file_handle.write(char)
                file_handle.flush()
        except KeyboardInterrupt:
            print("\nKey logging stopped by user.")
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            file_handle.write(f"\n--- Session ended {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")

    return log_file


def analyze_log_file(log_file=LOG_FILE):
    """Analyze the log file and print a summary of potential risks."""
    if not os.path.exists(log_file):
        print(f"No log file found at {log_file}")
        return

    with open(log_file, "r", encoding="utf-8") as file_handle:
        content = file_handle.read()

    entry_count = len(content)
    line_count = content.count("\n")
    letters = sum(1 for ch in content if ch.isalpha())
    digits = sum(1 for ch in content if ch.isdigit())
    spaces = content.count(" ")
    keyword_hits = [kw for kw in SENSITIVE_KEYWORDS if kw in content.lower()]

    print("\nLog file analysis")
    print("------------------")
    print(f"Log file: {log_file}")
    print(f"Total characters captured: {entry_count}")
    print(f"Lines: {line_count}")
    print(f"Alphabetic characters: {letters}")
    print(f"Digits: {digits}")
    print(f"Spaces: {spaces}")

    if keyword_hits:
        print("Potential sensitive keywords detected:")
        for keyword in keyword_hits:
            print(f" - {keyword}")
    else:
        print("No explicit sensitive keywords detected by simple scan.")

    print("\nRisk analysis")
    print("-------------")
    print("Captured keystrokes can reveal passwords, PINs, private messages, and any personal data typed during the session.")
    print("Storing keystrokes in an unsecured file increases the risk that attackers or unauthorized users can read sensitive input.")
    print("Many systems and organizations classify keylogging as malware when it is used without user consent.")


def main():
    log_file = capture_keystrokes()
    analyze_log_file(log_file)


if __name__ == "__main__":
    main()
