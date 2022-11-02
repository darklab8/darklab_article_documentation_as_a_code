#!/usr/bin/env python3
# script requires installed `sudo apt install imagemagick`
import subprocess
import argparse
import secrets

parser = argparse.ArgumentParser()

parser.add_argument("image_path", type=str)
parser.add_argument("percentage_size", type=int, help="value from 1 to 100")
parser.add_argument("output_path", type=str, default=secrets.token_hex(1))


args = parser.parse_args()

subprocess.run(f"convert {args.image_path} -resize {args.percentage_size}% {args.output_path}")