#! /bin/sh

backup-rsync.py --include rsync-development-include.txt --exclude rsync-development-exclude.txt --delete
backup-rsync.py --include rsync-archive-include.txt
