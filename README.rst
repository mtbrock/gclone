gclone
======
A Python 3 program for cloning github repositories.

Install
-------
``pip install --user gclone``

Usage
-----

Clone by full name::

  $ gclone mtbrock/gclone

Clone by partial name or keyword. gclone will provide a list of relevant github
repositories to choose from, sorted by 'stars'::

  $ gclone tmux

Pass options just like you would to ``git clone``::

  $ gclone --branch my-branch my-repo /path/to/my-dir
