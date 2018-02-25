# Archy README

Archy from RaskinCenter.org WebArchive 

## Sections

* Organization of the Source Code
* Requirements for Compiling and Running Archy
* Compiling and Running Archy

## Organization of the Source Code

Here's the source tree and its directories, with a description of
each:

    / (root directory)

The root directory contains most of the source code for Archy, as
well as some extra files that Archy needs.

    /commands

This directory contains source code for Archy's built-in commands.

    /commands/aspell

This directory contains code needed by Archy's spell checker; it
currently contains a number of files specific to the Windows
version of Archy, including an entire GNU Aspell dictionary.
Hopefully some of this will be moved out of the source tree at
some point.

    /commands/tutorial

This directory contains all code implementing Archy's tutorials,
and also currently contains a number of large Ogg Vorbis files
containing the audio for the tutorials.  These large files may be
moved out of the source tree at some point.

    /fonts

This directory contains the default TrueType fonts that Archy
uses.

    /icons

This directory contains images used for the Archy application icon
on many platforms.  See the `README.txt` file in this directory for
more information.

    /keycaps

This directory contains pictures of keys used by Archy's default
initial document.

    /sdl-patches

This directory contains various patches written for the Simple
DirectMedia Layer (SDL) library to allow Archy to work properly on
some platforms.  See the `README.txt` file in this directory for
more information.

    /utest

This directory contains code of unit tests.
See the `README.txt` file in this directory for more information.
See below how to run unit tests.

    /windows_installer_files

This directory contains files needed for creating a
self-installing executable for Archy on the Windows platform.  See
the `README.txt` file in this directory for more information.

## Requirements for Compiling and Running Archy

To compile and run Archy, you'll need the following:

* REQUIRED - Python version 2.3 or above (http://www.python.org).

* REQUIRED - Pygame version 1.6 or above (http://www.pygame.org).

  Note that in order to run Pygame, you may need a number of
  prerequisites, depending on your specific platform.  Windows
  users can just download the executable installer, but other
  platforms (such as Linux) will need to make sure they have a
  number of prerequisites, such as SDL.  Although Archy doesn't
  currently use all of Pygame's optional dependencies, this may
  change in the near future, so you're better off installing all
  of them.

  If you have Brew, installing these dependencies on MacOS is
  simply:

        brew install python
        pip2 install pygame

  If you want to be absolutely frugal, however, the Pygame
  components with optional dependencies which Archy does not
  currently use are:

    * The pygame.surfarray module.  This means that you don't need
      Python's Numeric package.

* The pygame.movie module.  This means that you don't need
      the smpeg library.

* REQUIRED (Windows) - Archy's custom SDL library

  This is a custom version of the Simple Directmedia Layer,
  patched with some of the patches from the 'sdl_patches'
  directory of the source tree, which allows Archy to work
  properly on Windows platforms.  The custom SDL.dll is contained
  in the root directory of the Archy distribution; just copy it
  into the pygame folder (often found in a directory such as
  C:\Python23\lib\site-packages\pygame).

* REQUIRED (Windows) - Mark Hammond's Python for Windows
  Extensions (http://sourceforge.net/projects/pywin32/).

* OPTIONAL (Windows, Linux) - Psyco (http://psyco.sourceforge.net/)

  This library currently only works with platforms running on
  Intel x86 processors; if Archy detects its presence, it will use
  Psyco to accelerate a number of its processor-intensive
  functions, allowing it to run a good deal faster.

* OPTIONAL (non-Windows) - wxPython (http://www.wxpython.org/)

  Non-Windows platforms utilize wxPython to access the clipboard.
  If this library isn't present on a non-Windows system, Archy's
  COPY IN and COPY OUT commands won't work.

* OPTIONAL - GNU aspell (http://aspell.sourceforge.net/)

  Currently, the source tree includes the Windows version of this
  software (Windows users don't need to install it--Archy finds it
  automatically), and the source code doesn't actually support a
  non-Windows version yet.  This will be changed in the near
  future.  In any case, if the aspell library isn't found, Archy's
  spellchecking features will not work.

## Compiling and Running Archy

To run Archy, execute the script `archy.py` located in the root
directory of the Archy source tree.
Archy accepts following command-line options:

    -d, --developer-mode

disables web-based bug reporting, enables certain disabled by
default commands such as SIMULATE BUGGY COMMAND and SIMULATE CRASH.

Execute `utest.py` without parameters to run all Archy unit tests:

    python utest.py

To run a specific Archy unit test modules specify names of the modules
as parameter utest.py parameters separated by spaces.
For example:

    python utest.py utest.commands.quitTest utest.audioTest

### Additional Linux Notes

The Linux version of Archy is still in a somewhat rough and
experimental state, and as such users running Archy on Linux may
need to do some extra work.

In order to properly access the state of the caps lock key, Archy
currently needs to use the `xmodmap` utility.  See the file
`linux_specific.py` for more information on how this is done; you
may need to modify this file slightly to work on your system.
Before using Archy for the first time, you may want to execute the
following command from a shell prompt:

    xmodmap -pke > original_keybindings.txt

If Archy ever crashes or somehow leaves your keyboard in a state
in which the caps lock key doesn't work, you can fix things by
executing the following from a shell prompt:

    xmodmap original_keybindings.txt

