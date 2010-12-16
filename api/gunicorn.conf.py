proc_name = "capwords"
logfile = "logs/wsgi.log"
loglevel = "info"

after_fork=lambda server, worker: server.log.info(
                "Worker spawned (pid: %s)" % worker.pid)

before_fork=lambda server, worker: True

before_exec=lambda server: server.log.info("Forked child, reexecuting")
