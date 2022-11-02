#!/usr/bin/env python3
import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("hash")

args = parser.parse_args()

subprocess.run(f'find . -name "*{args.hash}*"', shell=True, check=True)
