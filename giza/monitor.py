'''Code extracted from pserve.py & adapted to implement auto-reload with gevent
'''
import os
import sys
import time
import gevent
import traceback
import subprocess

RELOAD_KEY = '_PYTHON_RELOADER_SHOULD_RUN'

def install_supervisor(poll_interval, extra_files=None):
    if RELOAD_KEY in os.environ:
        # We are in the (monitored) subprocess, so we will launch a monitor
        # greenlet and return as usual.
        mon = Monitor(poll_interval=poll_interval)
        if extra_files is None:
            extra_files = []
        mon.extra_files.extend(extra_files)
        gevent.spawn(mon.periodic_reload)
    else:
        # We are in the supervisor (original) process, so we will launch the
        # (monitored) subprocess over and over again as long as the return code
        # is 3 (which the monitor raises). This code never
        # returns.
        new_environ = dict(os.environ)
        new_environ[RELOAD_KEY] = '1'
        args = [sys.executable] + sys.argv
        while True:
            proc = subprocess.Popen(args, env=new_environ)
            exit_code = proc.wait()
            if exit_code != 3:
                os._exit(exit_code)
    
class Monitor(object): # pragma: no cover
    """
    A file monitor and server restarter.

    Use this like:

    ..code-block:: Python

        install_reloader()

    Then make sure your server is installed with a shell script like::

        err=3
        while test "$err" -eq 3 ; do
            python server.py
            err="$?"
        done

    or is run from this .bat file (if you use Windows)::

        @echo off
        :repeat
            python server.py
        if %errorlevel% == 3 goto repeat

    or run a monitoring process in Python (``pserve --reload`` does
    this).  

    """
    instances = []
    global_extra_files = []
    global_file_callbacks = []

    def __init__(self, poll_interval):
        self.module_mtimes = {}
        self.keep_running = True
        self.poll_interval = poll_interval
        self.extra_files = list(self.global_extra_files)
        self.instances.append(self)
        self.file_callbacks = list(self.global_file_callbacks)

    def _exit(self):
        # use os._exit() here and not sys.exit() since within a
        # thread sys.exit() just closes the given thread and
        # won't kill the process; note os._exit does not call
        # any atexit callbacks, nor does it do finally blocks,
        # flush open files, etc.  In otherwords, it is rude.
        os._exit(3)

    def periodic_reload(self):
        while True:
            if not self.check_reload():
                self._exit()
                break
            time.sleep(self.poll_interval)

    def check_reload(self):
        filenames = list(self.extra_files)
        for file_callback in self.file_callbacks:
            try:
                filenames.extend(file_callback())
            except:
                print(
                    "Error calling reloader callback %r:" % file_callback)
                traceback.print_exc()
        for module in sys.modules.values():
            try:
                filename = module.__file__
            except (AttributeError, ImportError):
                continue
            if filename is not None:
                filenames.append(filename)
        for filename in filenames:
            try:
                stat = os.stat(filename)
                if stat:
                    mtime = stat.st_mtime
                else:
                    mtime = 0
            except (OSError, IOError):
                continue
            if filename.endswith('.pyc') and os.path.exists(filename[:-1]):
                mtime = max(os.stat(filename[:-1]).st_mtime, mtime)
            if not filename in self.module_mtimes:
                self.module_mtimes[filename] = mtime
            elif self.module_mtimes[filename] < mtime:
                print("%s changed; reloading..." % filename)
                return False
        return True

