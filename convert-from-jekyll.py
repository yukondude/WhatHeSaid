#!/usr/bin/env python
# -*- coding: utf-8 -*- #

""" Convert Jekyll-formatted HTML and Markdown files in a given source directory into Pelican-formatted Markdown files
    in a given destination directory.
"""

import os
import re
import sys


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: pipenv run convert JEKYLL_SOURCE_DIR PELICAN_DESTINATION_DIR", file=sys.stderr)
        sys.exit(-1)

    jekyll_dir = sys.argv[1]
    pelican_dir = sys.argv[2]

    jekyll_re = re.compile(r"^---\n((.+\n)+)---\n((.*\n)+(.*)?)$")
    meta_keepers = {
        'title': "Title",
        'date': "Date",
        'tweet_id': "Tweet_id",
    }

    for from_filename in os.listdir(jekyll_dir):
        base_filename, extension = os.path.splitext(from_filename)

        if extension not in ('.md', '.html'):
            continue

        from_path = os.path.join(jekyll_dir, from_filename)
        to_path = os.path.join(pelican_dir, base_filename + ".md")

        try:
            os.unlink(to_path)
        except FileNotFoundError:
            pass

        with open(from_path, 'r') as from_file:
            content = from_file.read()

        # Do stuff with header and content
        # Replace any self absolute URLs too!
        jekyll_match = jekyll_re.match(content)

        if not jekyll_match:
            print(f"Unable to parse '{from_filename}' into header and body content.", file=sys.stderr)
            continue

        jekyll_header, jekyll_body = map(str.strip, jekyll_match.group(1, 3))
        jekyll_header_lines = jekyll_header.split("\n")

        pelican_header_lines = []

        for line in jekyll_header_lines:
            for keeper in meta_keepers.keys():
                if line.startswith(keeper + ":"):
                    pelican_header_lines.append(line.replace(keeper + ":", meta_keepers[keeper] + ":"))

        pelican_content = "\n".join(pelican_header_lines) + "\n\n" + jekyll_body

        with open(to_path, 'w') as to_file:
            to_file.write(pelican_content)
