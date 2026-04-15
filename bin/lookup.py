#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import json

runPath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(runPath, ".."))
from lib.cpeguesser import CPEGuesser

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find potential CPE names from a list of keyword(s) and return a JSON of the results"
    )
    parser.add_argument(
        "word",
        metavar="WORD",
        type=str,
        nargs="+",
        help="One or more keyword(s) to lookup",
    )
    parser.add_argument(
        "--unique",
        action="store_true",
        help="Return the best CPE matching the keywords given",
        default=False,
    )
    parser.add_argument(
        "--part",
        choices=sorted(CPEGuesser.VALID_CPE_PARTS),
        help="Optional CPE part filter: a (application), h (hardware), o (operating system)",
    )
    args = parser.parse_args()

    cpeGuesser = CPEGuesser()
    r = cpeGuesser.guessCpe(args.word, part=args.part)
    if not args.unique:
        print(json.dumps(r))
    else:
        try:
            r = r[:1][0][1]
        except:
            r = []
        print(json.dumps(r))
