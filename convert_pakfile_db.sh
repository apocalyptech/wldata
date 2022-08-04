#!/bin/bash
# vim: set expandtab tabstop=4 shiftwidth=4:

read -sp 'Enter wlpakfile pass: ' PASS
echo
echo "SQLite dump/conversion..."
echo
rm wlpakfile.sqlite3*
/usr/local/dv/virtualenv/mysql2sqlite/bin/mysql2sqlite -f wlpakfile.sqlite3 -d wlpakfile -u wlpakfile -h mcp -V -p ${PASS} && zip wlpakfile.sqlite3.zip wlpakfile.sqlite3 && rm wlpakfile.sqlite3 && ls -lh wlpakfile.sqlite3*
