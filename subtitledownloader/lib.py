import logging
import logging.handlers


def setup_log(name, level=logging.INFO,
              log_file=False, console_output=True):
    # Setup log and set defaul level
    log = logging.getLogger(name)
    logging.basicConfig(level=logging.WARNING,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    log.setLevel(level)

    # Log to file
    if log_file:
        logfile_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=1048576, backupCount=5)
        logfile_handler.formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
        log.addHandler(logfile_handler)

    # Output to console
    log.propagate = console_output

    return log
