FROM mongo:4.4.6

RUN echo "12345678" > "/tmp/key.file"
RUN chmod 600 /tmp/key.file
RUN chown 999:999 /tmp/key.file

CMD ["mongod", "--bind_ip_all", "--replSet", "rs0", "--keyFile", "/tmp/key.file", "--logpath", "/dev/null"]
