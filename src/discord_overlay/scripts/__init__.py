import logging
import os
import signal
import sys
import click
import pathlib

from logging.handlers import RotatingFileHandler
from discord_overlay.app import App


# To manage CTRL+C from terminal
signal.signal(signal.SIGINT, signal.SIG_DFL)


if sys.platform == 'win32':
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('bashtian.fr.discord-overlay')


def set_logger(debug, log_file_path):
    create_logging_folder(log_file_path)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(filename)s:%(lineno)s - %(funcName)s()]: %(message)s"
    )

    ch = logging.StreamHandler()
    fh = RotatingFileHandler(
        filename=os.path.expandvars(fr'{log_file_path}'),
        maxBytes=10*1024*1024,
        backupCount=20
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    if debug:
        logger.setLevel(logging.DEBUG)
        fh.setLevel(logging.DEBUG)
        ch.setLevel(logging.DEBUG)

    logger.addHandler(fh)
    logger.addHandler(ch)


def create_logging_folder(log_file_path):
    try:
        log_dir = os.path.expandvars(log_file_path)
        os.makedirs(pathlib.Path(log_dir).parent)
    except FileExistsError:
        pass


@click.command()
@click.option("--debug", is_flag=True, default=False)
def main(debug=False):
    app_domain = "bashtian.fr"
    app_name = "discord-overlay"
    log_file_path = fr"%APPDATA%/{app_domain}/{app_name}.log"

    set_logger(debug, log_file_path)

    app = App(organization_domain=app_domain, name=app_name)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
