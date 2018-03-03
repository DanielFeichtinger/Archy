# debug.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

# This module offers debugging-related functionality to Archy in the form of debug message logging, web-based bug reporting, and so forth.

# The following "developer mode" flag determines whether certain features are enabled or disabled for development purposes--for instance, turning developer mode on disables web-based bug reporting, since a developer using Archy is going to run into numerous bugs while writing code and can just fix the bugs as they find them.

DEVELOPER_MODE = True

# --------------------------
# The Debug Log Class
# --------------------------

# The debug log class (and its supporting classes) offer a file object that is meant to redirect stdio and stderr into a debug log file, while also displaying their messages to the "original" stdin and stdout.

class _DebugLogFileProxy:
    def __init__(self, parent, number):
        self.softspace = 0
        self.parent = parent
        self.number = number

    def readline(self):
        return None

    def isatty(self):
        return 0

    def flush(self):
        self.parent._flush(self.number)

    def write(self, text):
        self.parent._write(self.number, text)

    def writelines(self, lines):
        self.parent._writelines(self.number, lines)

class DebugLog:
    def __init__(self, filename):
        self.debug_out = _DebugLogFileProxy(self, 0)
        self.debug_err = _DebugLogFileProxy(self, 1)
        self.filename = filename

        import threading
        self.semaphore = threading.Semaphore()

    def install(self):
        import sys

        self.file = open(self.filename, "a")
        self.chain_files = [None, None]
        self.chain_files[0] = sys.stdout
        self.chain_files[1] = sys.stderr
        sys.stdout = self.debug_out
        sys.stderr = self.debug_err

    def uninstall(self):
        import sys

        sys.stdout = self.chain_files[0]
        sys.stderr = self.chain_files[1]
        self.file.close()

    def _flush(self, number):
        self.semaphore.acquire()
        self.chain_files[number].flush()
        self.file.flush()
        self.semaphore.release()

    def _write(self, number, text):
        self.semaphore.acquire()
        self.chain_files[number].write(text)
        self.file.write(text)
        self.semaphore.release()

    def _writelines(self, number, lines):
        self.semaphore.acquire()
        self.chain_files[number].writelines(lines)
        self.file.writelines(lines)
        self.semaphore.release()

# --------------------------
# Module functions
# --------------------------

def _get_windows_version():
    import sys

    WINDOWS_VERSIONS = {
        0 : 'Win32s on Windows 3.1',
        1 : 'Windows 95/98/ME',
        2 : 'Windows NT',
        3 : 'Windows CE'
    }
    info = sys.getwindowsversion()
    info_str = "%s v%d.%d %s, build %d" % (
        WINDOWS_VERSIONS[info[3]], info[0], info[1],
        info[4], info[2])
    return info_str

# This function returns a string containing lots of useful information about the system the application is running on.

def get_system_info():
    import sys

    import version

    text = "System information:\n"
    text += "  Archy version: %s\n" % str(version.get_full_version())
    text += "  Command-line arguments: %s\n" % str(sys.argv)
    if sys.platform == 'win32':
        text += "  Platform: %s\n" % _get_windows_version()
    else:
        text += "  Platform: %s\n" % str(sys.platform)
    text += "  Python version: %s\n" % str(sys.version)
    return text

# This function reports a bug using Archy's web-based bug reporting mechanism.  If developer mode is on, however, it does nothing.

def report_bug(title, traceback_info):
    import urllib, webbrowser

    print traceback_info
    if DEVELOPER_MODE:
        return
    traceback_info = get_system_info() + "\n" + traceback_info
    query = {'title':title, 'traceback_info':traceback_info, 'type':'entry'}
    url = 'http://www.raskincenter.org/cgi-bin/bug_entry.cgi?' + urllib.urlencode(query)
    webbrowser.open(url)

# This function returns a printed version of the current traceback as a Python string.

def get_traceback():
    import traceback
    import cStringIO

    newStrFile = cStringIO.StringIO()
    traceback.print_exc(1000, newStrFile)
    return newStrFile.getvalue()

