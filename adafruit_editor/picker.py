# SPDX-FileCopyrightText: 2023 Jeff Epler for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import os

from . import dang as curses

always = ["code.py", "boot.py", "settings.toml", "boot_out.txt"]
good_extensions = [".py", ".toml", ".txt", ".json"]


def os_exists(filename):
    try:
        os.stat(filename)
        return True
    except OSError:
        return False


def isdir(filename):
    return os.stat(filename)[0] & 0o40_000


def has_good_extension(filename):
    for g in good_extensions:
        if filename.endswith(g):
            return True
    return False


def picker(stdscr, options, notes=(), start_idx=0):
    stdscr.erase()
    stdscr.addstr(curses.LINES - 1, 0, "Enter: select | ^C: quit")
    window_end = max(curses.LINES - 2, start_idx)
    window_start = window_end - (curses.LINES - 2)
    for row, option in enumerate(options):
        if row < len(notes) and (note := notes[row]):
            option = f"{option} {note}"

        if window_start <= row and row <= window_end:
            stdscr.addstr(row, 3, option)

    old_winidx = None
    idx = start_idx
    old_idx = idx
    window_idx = min(idx, window_end)
    while True:
        if window_idx != old_winidx:
            if old_winidx is not None:
                stdscr.addstr(old_winidx, 0, "  ")
            stdscr.addstr(window_idx, 0, "=>")
            old_winidx = window_idx

        k = stdscr.getkey()

        if k == "KEY_DOWN":
            idx = min(idx + 1, len(options) - 1)
            if window_idx >= curses.LINES - 2:
                if idx != old_idx:
                    stdscr.addstr(window_idx, 0, "  ")
                    stdscr.move(curses.LINES,0)
                    print(end=f'\033[2K\033D')
                    stdscr.addstr(curses.LINES - 1, 0, "Enter: select | ^C: quit")
                    if idx < len(notes) and (note := notes[idx]):
                        option = f"{options[idx]} {note}"
                    else:
                        option = options[idx]
                    stdscr.addstr(window_idx, 3, option)
                    stdscr.addstr(window_idx, 0, "=>")
            else:
                window_idx = window_idx + 1
            old_idx = idx
        elif k == "KEY_UP":
            idx = max(idx - 1, 0)
            if window_idx <= 0:
                if idx != old_idx:
                    stdscr.addstr(window_idx, 0, "  ")
                    stdscr.move(0,0)
                    print(end=f'\033M')
                    stdscr.addstr(curses.LINES - 1, 0, "Enter: select | ^C: quit")
                    if idx < len(notes) and (note := notes[idx]):
                        option = f"{options[idx]} {note}"
                    else:
                        option = options[idx]
                    stdscr.addstr(window_idx, 3, option)
                    stdscr.addstr(window_idx, 0, "=>")
            else:
                window_idx = window_idx - 1
            old_idx = idx
        elif k == "\n":
            return options[idx]


def pick_file():
    options = always[:] + sorted(
        (
            g
            for g in os.listdir(".")
            if g not in always and not isdir(g) and not g.startswith(".")
        ),
        key=lambda filename: (not has_good_extension(filename), filename),
    )
    notes = [None if os_exists(filename) else "(NEW)" for filename in options]
    return curses.wrapper(picker, options, notes)
