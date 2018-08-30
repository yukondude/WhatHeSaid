#!/usr/bin/env python
# -*- coding: utf-8 -*- #

import os
import sys


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: pipenv run convert JEKYLL_POSTS_DIR PELICAN_POSTS_DIR", file=sys.stderr)
        sys.exit(-1)

    jekyll_dir = sys.argv[1]
    pelican_dir = sys.argv[2]

    for source_name in os.listdir(jekyll_dir):
        base_name = os.path.splitext(source_name)[0]

        from_path = os.path.join(jekyll_dir, source_name)
        to_path = os.path.join(pelican_dir, base_name + ".md")

        os.unlink(to_path)

        with open(from_path, 'r') as from_file:
            content = from_file.read()

        # Do stuff with header and content
        # Replace any self absolute URLs too!

        with open(to_path, 'w') as to_file:
            to_file.write(content)

        print(".", end="")

    print()
