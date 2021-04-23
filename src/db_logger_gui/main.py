import getpass
import json
import os
import pathlib
import shutil
import sys
import tkinter as tk

from db_logger_gui import MainApp, ScreenRes, check_singleton
from make_db_entry import DBSessionLogger


def validate_config(config):
    keys_non_null = [
        "database_name",
        "database_relpath",
        "networkdrive_hostname",
        "daq_relpath",
    ]

    for k in keys_non_null:
        if not config.get(k):
            raise ValueError(f"Config is NOT valid: entry `{k}` is not present or Null.")

    return True

def main():
    # check singleton
    try:
        sing = check_singleton()
    except OSError as e:
        root = tk.Tk()
        root.title('Error')
        message = "Only one instance of the NexusLIMS " + \
                  "Session Logger can be run at one time. " + \
                  "Please close the existing window if " + \
                  "you would like to start a new session " \
                  "and run the application again."
        if sys.platform == 'win32':
            message = message.replace('be run ', 'be run\n')
            message = message.replace('like to ', 'like to\n')
        root.withdraw()
        tk.messagebox.showerror(parent=root, title="Error", message=message)
        sys.exit(0)


    # config
    config_dir = os.path.join(pathlib.Path.home(), ".nexuslims", "gui")
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    config_fn = os.path.join(config_dir, "config.json")
    if not os.path.isfile(config_fn):
        # default config
        default_fn = os.path.abspath(__file__)
        default_fn = default_fn.replace(os.path.basename(__file__), "config.json")
        shutil.copy(default_fn, config_fn)

        msg = ("No config file found, the default config is copied to %s. "
               "Modify the configuration appropiately and run the application again.") % config_fn
        root = tk.Tk()
        root.title("Error")
        root.withdraw()
        tk.messagebox.showerror(parent=root, title="Error", message=msg)
        sys.exit(0)

    try:
        config = json.loads(open(config_fn).read())
        validate_config(config)
    except Exception as e:
        root = tk.Tk()
        root.title("Error")
        root.withdraw()
        tk.messagebox.showerror(parent=root, title="Error", message=str(e))
        sys.exit(0)

    # user
    login = getpass.getuser()

    dbdl = DBSessionLogger(config=config, user=login, verbosity=2)
    sres = ScreenRes(dbdl)

    root = MainApp(dbdl, screen_res=sres)
    root.protocol("WM_DELETE_WINDOW", root.on_closing)
    root.mainloop()



if __name__ == "__main__":
    main()
