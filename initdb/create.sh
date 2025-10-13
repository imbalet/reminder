#!/bin/bash
set -e

IFS=','
for db in $POSTGRES_DATABASES; do
echo "  -> $db"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE "$db";
EOSQL
  done

unset IFS