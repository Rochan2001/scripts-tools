#!/usr/bin/env python3
#
# Extracts exceptions from log files.
#
# The idea here is that you can specify a regular expression that acts
# as an indicator that you've reached the beginning of a "block".  A
# "block" is a set of lines that should be treated as a group, such
# that a match against the group would print the entire group rather
# than just the matching line.  So this program takes two arguments,
# the first being the aforementioned regular expression, and the
# second being the regular expression that is used to match against
# groups.
#
# We also allow a couple of options, a "case independent" option and a
# match inversion option (the same as "grep -v").

import sys
import re
import os

global debugflag
debugflag = False

try:
    dbg = os.environ["debug"]
    if dbg != "0":
        debugflag = True
except KeyError:
    pass

def debug(args):
    global debugflag
    if debugflag:
        print(args)

debug("debugflag = %s" % debugflag)

def usage(name):
    print( '''
Usage: %s [-v] [-i] [-b <block beginning regex>] [-e <search regex> [-e <search regex>] ...] <search regex> [file ...]

Searches the specified files (or stdin if no files are specified) for
the specified regular expression.  The regular expression defines the
beginning of a 'block', which is a set of lines that are to be treated
as a unit for the purposes of output, can optionally be specified.  If
it is not specified, a default that should match the beginning of most
log file lines will be used.  A unit that matches the search regular
expression will be output in its entirety.  This is different from how
'grep' works, and makes it possible to do things like print entire
stack traces in a log when a match in the log is found.

Options:

    -v    Invert matches -- print blocks that do NOT match the search
          regex.

    -i    Perform a case insensitive search.  This applies to the
          search regex as well as the block regex.

    -l    Print file name and line number for matches.  Works only
          when files to search are supplied.  Inoperative when stdin
          is being searched.

    -b    Specify the regular expression defining the beginning of a
          block.  The default should match the beginning of most log
          lines.

    -e    Add the specified search regex to the list of searches that
          are to be performed.  This option may be used multiple times,
          but you must still specify a <search regex> after
          <block beginning regex> even if you use this option.  When
          this option is used, all specified patterns must match the
          block for the block to be considered as matching (when -v is
          specified, then a failure to match any of the specified
          patterns will cause the block to be output).  An artifact of
          how this is implemented is that the case insensitivity option
          will apply only to the "-e" options that follow it, NOT to
          the ones that precede it.  This means you can control which
          search expressions are case insensitive and which ones are
          case sensitive.  Note that the main <search regex> will always
          have the case sensitivity option applied to it if that option
          was specified, since it always appears after all options.

    -s    Insert the specified separator between results

    -n    Limit the number of matching blocks emitted to the number
          specified.  This is *per file*.

    -g    Start emitting matches at the specified block number (1 is 
          the first) in the file.  

The "-e" option can be confusing to use, but it exists because it can
become tiresome (not to mention error prone) to have to re-specify the
block beginning regex to each instance of this program in a pipeline.
It also makes it possible to specify a case sensitive search regex but
a case insensitive block beginning regex, just by using '' as the main
search regex (a blank regex matches everything):

    %s -e 'searchre' -i -b 'beginningre' '' file1 file2 ...
''' % (name, name) )
    print()


blockpattern = '^((.+:[0-9]+:)?([0-9]{4,4}-[0-9][0-9]-[0-9][0-9]( |--)[0-9][0-9][:-][0-9][0-9][:-][0-9][0-9]([,-][0-9]{3,3})?)|((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) [0-9][0-9] [0-9][0-9]:[0-9][0-9]:[0-9][0-9]))'

invertMatch = False

printFileName = False

searchregexes = []

flags = 0

separator = None

maxMatches = -1

startMatch = 1

debug("Args = %s" % sys.argv)

argstart = 1
while (argstart < len(sys.argv) and len(sys.argv[argstart]) > 0 and sys.argv[argstart][0] == '-'):
    if sys.argv[argstart] == '-v':
        invertMatch = True
    if sys.argv[argstart] == '-l':
        printFileName = True
    if sys.argv[argstart] == '-i':
        flags = re.IGNORECASE
    if sys.argv[argstart] == '-e':
        argstart = argstart + 1
        searchregexes.append(re.compile(sys.argv[argstart], flags))
    if sys.argv[argstart] == '-b':
        argstart = argstart + 1
        blockpattern = sys.argv[argstart]
        debug("Block pattern now '%s'" % blockpattern)
    if sys.argv[argstart] == '-s':
        argstart = argstart + 1
        separator = sys.argv[argstart]
        debug("Separator now '%s'" % separator)
    if sys.argv[argstart] == '-n':
        argstart = argstart + 1
        maxMatches = int(sys.argv[argstart])
        debug("Max matches now %d" % maxMatches)
    if sys.argv[argstart] == '-g':
        argstart = argstart + 1
        startMatch = int(sys.argv[argstart])
        debug("Start block now %d" % startMatch)
    argstart = argstart + 1

try:
    blockre = re.compile(blockpattern, flags)
    searchregexes.append(re.compile(sys.argv[argstart], flags))
except IndexError:
    usage(sys.argv[0])
    sys.exit(1)

def searchBlockOnce(block, regex, invert):
    # Here, if we get a match on any line in the block, the block
    # is considered to match and we return True immediately (False
    # if inverted).  Reaching the end means, of course, that we
    # failed to find any matching lines, so we return False (True
    # if inverted).
    for l in block:
        if regex.search(l):
            # Yeah, yeah.  We could just "return not invert" here,
            # but that wouldn't be as clear.
            if invert:
                return False
            else:
                return True
    if invert:
        return True
    else:
        return False

def searchBlock(block, regexes, invert):
    # Here, we want *all* regexes to match.  If any one fails, then
    # the entire thing fails and we return False immediately (or
    # True if inverted).  If we get to the end, then it means that
    # all regexes have matched, so we return True, or False if
    # inverted.
    for r in regexes:
        if not searchBlockOnce(block, r, False):
            if invert:
                return True
            else:
                return False
    if invert:
        return False
    else:
        return True

def printBlock(block, fileName = None, lineNum = None):
    for l in block:
        if fileName != None:
            sys.stdout.write(fileName + ":")
            if lineNum != None:
                sys.stdout.write("%d:" % (lineNum))
                lineNum = lineNum + 1
        sys.stdout.write(l)
    if separator != None:
        sys.stdout.write(separator + "\n")

def processFH(filehandle, fileName = None):
    global blockre

    block = []
    gotHit = False
    foundEnd = False
    lineNum = 0
    numMatchingBlocks = 0
    numPrinted = 0
    l = filehandle.readline()
    while(l != ''):
        lineNum = lineNum + 1
        if blockre.search(l):
            if len(block) != 0:
                if searchBlock(block, searchregexes, invertMatch):
                    debug("numMatchingBlocks = %d, maxMatches = %d, startMatch = %d" %
                          (numMatchingBlocks, maxMatches, startMatch))
                    if (numMatchingBlocks >= startMatch - 1):
                        printBlock(block, fileName, lineNum)
                        numPrinted = numPrinted + 1
                    numMatchingBlocks = numMatchingBlocks + 1
                    if (maxMatches > 0 and numPrinted >= maxMatches):
                        return
                block = []
        block.append(l)
        l = filehandle.readline()
    if len(block) != 0 and searchBlock(block, searchregexes, invertMatch) and \
       numMatchingBlocks >= startMatch - 1 and (maxMatches < 0 or numPrinted < maxMatches):
        printBlock(block, fileName, lineNum)

try:
    if len(sys.argv) > argstart + 1:
        for f in sys.argv[argstart + 1:]:
            fh = open(f, 'r')
            if printFileName:
                processFH(fh, f)
            else:
                processFH(fh)
    else:
        processFH(sys.stdin)
except IOError as e:
    # Errno 32 is "Broken Pipe".  Re-raise the exception on anything
    # else.  This avoids getting a stacktrace when the only thing one
    # did is close the reading program (e.g., if you pipe the output
    # to "more" or something, and exit before this program has had a
    # chance to finish writing).
    if e.errno != 32:
        raise

