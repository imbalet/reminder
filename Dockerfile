FROM postgres:17.6

COPY ./initdb /docker-entrypoint-initdb.d/