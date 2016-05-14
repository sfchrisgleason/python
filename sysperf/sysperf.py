#!/usr/bin/env python3


'''
#==================================================================================#
# AUTHOR: Chris Gleason                                                            #
# DATE:   7/1/2015                                                                 #
# Version:  1.0                                                                    #
# COMMENT: System Information Gathering - Written for Python 3                     #
#==================================================================================#
# Various functions to gather information on OSX and windows endpoints             #
#==================================================================================#

### DESCRIPTION ###

This script is a system information and performance information
gathering script. It will pull information regarding live stats
like memory and cpu as well as information like os version and
serial number.

It's designed to be cross platform between Windows and OSX but
some data just isn't available on both.

This is an informational script only. It is not designed to change
any information, although with a few tweaks it could be.

In the spirit of being easy to run, I've only applied funtions that
don't require root/admin priviledges to run, so that any average
user/process can use and utilize this.

I may eventually branch this and remove psutil, as it's not a standard
module and requires some work to install. I would like this script
to be runnable from a default python install across platforms, so
I may eventually completely isolate the OSX and windows functions
and remove the cross platform section, putting in some logic to make
it transparent to the user.

### FUTURE WORK ###

1) Figure out if dependencies exist and if not exit properly with an informative message
2) If you can elegantly install the dependencies.
3) Need to run as sudo to pull network info from psutil
4) Going to completely remove perf and sys arguments. Since we are utilizing subprocess.call so heavily,
   it makes sense to just isolate via platform then break it up from there. I may add (--disk, --cpu, etc)
   flags later, but for now I'll just consolidate into OS arguments.
5) Add an argument to suppress the long running tasks like du and iostat

### DEPENDENCIES ###

psutil

OSX

wget https://pypi.python.org/packages/source/p/psutil/psutil-3.1.0.tar.gz /tmp
tar -zxvf /tmp/psutil-3.1.0.tar.gz /tmp/
pip install /tmp/psutil-3.1.0/psutil

WINDOWS

https://pypi.python.org/packages/3.4/p/psutil/psutil-3.1.0.win32-py3.4.exe#md5=eb4504f7da8493a512a6f038a502a25c


'''

__version__ = "$Revision: 1.0"

################
# IMPORTS HERE #
################

import subprocess
import os
import platform
import sys
import argparse
import psutil
#import readline
#import time



###########################################
# ARGUMENTS AND SCRIPT RELATED ITEMS HERE #
###########################################


parser = argparse.ArgumentParser(description='Print system usage statistics and system information. \
    Default (no args) will determine OS and run all gather functions')
parser.add_argument('--ntfs' , 
    action='store_true' ,
    help='Gather Windows information')
parser.add_argument('--osx' , 
    action='store_true' ,
    help='Gather OSX information')
parser.add_argument('--quick' , 
    action='store_true' ,
    help='Suppress long running functions (du, iostat, cpu timing)')

args = parser.parse_args()


##############################################
# NON PLATFORM SPECIFIC FUNCTIONS START HERE #
##############################################

def noargs():

    '''
    This function uses sys.platform to determine OS version
    if the user doesn't define it in the command line switches
    '''

    if sys.platform == 'win32':
        print('Platform is NTFS/Windows!')
        runperf()
        runsys()
        runntfs()
    elif sys.platform == 'darwin':
        print('Platform is OSX!')
        runperf()
        runsys()
        runosx()
    else:
        print('Operating System not supported. Exiting!')
        exit(0)

def big_title(title):
    
    '''
    This function auto generates a title heading around your title text
    using the # symbol on the top and the bottom
    '''

    titlelen = len(title)    
    print('#' * titlelen)
    print(title)
    print('#' * titlelen)

def little_title(title):

    '''
    Thie function auto generates a title heading around your title text
    using the - symbol on the top and the bottom
    '''

    titlelen = len(title)    
    print('=' * titlelen)
    print(title)
    print('=' * titlelen)

def sub_title(title):

    '''
    This function auto generates a title heading under your title text
    using the - symbol to underline the title
    '''

    titlelen = len(title)
    print(title)
    print('.' * titlelen)
    


def runperf():

    '''
    This function runs cross platform performance related tests
    '''

    title = 'PERFORMANCE TESTS RUNNING!'
    big_title(title)

    print ('''
    ''')

    title = 'CPU PERF INFO'
    little_title(title)

    print()
    print('CPU times at runtime are ', psutil.cpu_times())
    print()
    if quick:
        print('CPU Usage stats skipped!')
    else:
        print('CPU percent per CPU at runtime is ', psutil.cpu_percent(interval=5, percpu=True))
    print()
    print('''
    ''')

    title = 'MEMORY PERF INFO'
    little_title(title)

    print()
    print('Memory usage statistics are ', psutil.virtual_memory())
    print()
    print('''
    ''')

    title = 'DISK PERF INFO'
    little_title(title)

    print()
    if sys.platform == 'darwin':
        title = 'Disk usage is'
        sub_title(title)
        print(subprocess.call(['/bin/df', '-h']))

        title = 'OSX SP Storage Data Type'
        little_title(title)

        subprocess.call(['system_profiler SPStorageDataType'], shell=True)
        print()

        print()
        print()
        if quick:
            print('IOStat and Disk Usage tests skipped!')
        else:
            title = 'Disk IO statistics are'
            little_title(title)
            print(subprocess.call(['/usr/sbin/iostat', '-c10']))
            print()
            print('Be sure to ignore the first iostat line, as per best practices')
            print()
            title = 'Disk usage by directory is'
            little_title(title)
            print()
            subprocess.call(['du -hs /* --max-depth=1 2>/dev/null'], shell=True)
            print()
            print('Because this script isn\'t designed to run as root, it can\'t stat all files.')
            print('Permission Denied messages have been suppressed, but it should give an idea')
            print('as to which directories are the big ones...')
            print()
        print()
    if sys.platform == 'win32':
        sysdrive = os.environ['SystemDrive']
        title = 'Disk usage on the System Drive (',sysdrive,') is'
        little_title(title)
        subprocess.call(['fsutil', 'volume', 'diskfree', sysdrive])
 
    print()
    print('''
    ''')

    title = 'NETWORK PERF INFO'
    little_title(title)
    print()
    title = 'Network I/O stats '
    sub_title(title)
    print(psutil.net_io_counters(pernic=False))
    print()
    print()
    print()
    print()



def runsys():

    '''
    This function runs cross platform system information gathering
    '''

    title = 'SYSTEM INFORMATION GATHERING!'
    big_title(title)

    print ('''

    ''')
    
    title = 'Your OS is'
    little_title(title) 
    print(platform.system(), platform.release(), '-', platform.version())
    print()
    title = 'Your architecture is'
    little_title(title)
    print(platform.architecture())
    print()
    if sys.platform == 'darwin':
        title = 'Your system model is'
        little_title(title)
        subprocess.call(['sysctl', 'hw.model'])
    else:
        title = 'Your system model is'
        little_title(title)
        subprocess.call(['wmic', 'csproduct', 'get', 'vendor,', 'version'])
    print()
    title = '# of logical CPU\'s (Cores) are '
    little_title(title)
    print(psutil.cpu_count())
    print()
    title = 'Disk information is '
    little_title(title)
    print(psutil.disk_partitions(all=True))
    print() 
    if os == 'osx':
        print('Users on the system are:\n')
        subprocess.call(['who', '-a'])
    print()
    if os == 'ntfs':
        print('Users on the system are:\n')
        subprocess.call(['qwinsta'])
    print()
    title = 'Your network IP configuration is'
    little_title(title)
    print()
    if sys.platform == "darwin":
        subprocess.call(['ifconfig'])
    else:
        subprocess.call('ipconfig /all', shell=True)
    print()
 

######################################
# WINDOWS SPECIFIC THINGS START HERE #
######################################

def runntfs():

    '''
    This function runs the Windows specific gatherers
    '''

    #print('NTFS Tests running!')

    title = 'NTFS TESTS RUNNING!'
    little_title(title)

    title = 'Windows: Serial Number'
    little_title(title)

    print()
    subprocess.call(['wmic', 'bios', 'get', 'serialnumber'])
    print()

    title = 'Windows: Host Name'
    little_title(title)

    print()
    p1 = subprocess.Popen(['hostname'], stdout=subprocess.PIPE)
    output = p1.communicate()[0]
    print(output)
    print()

    title = 'Windows: Power Configuration'
    little_title(title)

    print()
    subprocess.call(['powercfg', '-q'])
    print()

    title = 'Windows: Full System Info Command'
    little_title(title)

    print()
    subprocess.call(['systeminfo'])
    print()

############################
# OSX SPECIFIC THINGS HERE #
############################


def runosx():

    '''
    This function runs the OSX specific gatherers
    '''

    title = 'OSX SPECIFIC INFO GATHERING!'
    big_title(title)

    print()

    title = 'OSX Serial Number'
    little_title(title)

    print()
    #subprocess.call(['ioreg -l | grep IOPlatformSerialNumber | cut -d \'=\' -f2'], shell=True)
    p1 = subprocess.Popen(['ioreg -l | grep IOPlatformSerialNumber | cut -d \'=\' -f2'], shell=True, stdout=subprocess.PIPE)
    output = p1.communicate()[0]
    print(output)
    print()

    title = 'OSX Hostname Info'
    little_title(title)

    print()
    print('SCUTIL HOSTNAME set to: ')
    hostname = subprocess.call(['/usr/bin/env', 'scutil', '--get', 'HostName'])
    print()
    print('SCUTIL LOCALHOSTNAME set to: ')
    localhostname = subprocess.call(['/usr/bin/env', 'scutil', '--get', 'LocalHostName'])
    print()
    print('SCUTIL COMPUTERNAME set to: ')
    computername = subprocess.call(['/usr/bin/env', 'scutil', '--get', 'ComputerName'])
    print()

    title = 'OSX SP Software Data Type' 
    little_title(title)

    subprocess.call(['system_profiler SPSoftwareDataType'], shell=True)
    print()

    title = 'OSX Power Management Settings'
    little_title(title)

    print()
    subprocess.call(['system_profiler SPPowerDataType'], shell=True)
    print()

    title = 'OSX Sleep image size'
    little_title(title)

    print()
    subprocess.call(['ls', '-hal', '/Private/var/vm/sleepimage'])
    print()

    title = 'OSX System Defaults (Some of them)'
    little_title(title)

    '''
    
    I don't know much about defaults, so I output the ones I know could matter, but there are a ton that might matter to you.
    If you find that they aren't outputting, it's because they have not been set. In most cases the default is off
    Most of these were taken from:
    https://gist.github.com/brandonb927/3195465/
    https://github.com/mathiasbynens/dotfiles

    '''
 
    print()
    print()
    print('Resume is disabled system wide (0 = False and 1 = True)') 
    print('defaults read com.apple.systempreferences NSQuitAlwaysKeepsWindows -bool')
    resume = subprocess.call(['defaults', 'read', 'com.apple.systempreferences', 'NSQuitAlwaysKeepsWindows', '-bool'])
    print()
    print('Daily update check interval in days is: ')
    print('defaults read com.apple.SoftwareUpdate ScheduleFrequency -int')
    updates = subprocess.call(['defaults', 'read', 'com.apple.SoftwareUpdate', 'ScheduleFrequency', '-int']) 
    print()
    print('Is password required immediately after sleep or screensaver enabled? (0 = No and 1 = Yes)')
    print('defaults read com.apple.screensaver askForPassword -int')
    ss = subprocess.call(['defaults', 'read', 'com.apple.screensaver', 'askForPassword', '-int'])
    print()
    print('What is the default delay when turning on the ask for password? (in seconds)')
    print('defaults read com.apple.screensaver askForPasswordDelay -int')
    ssdelay = subprocess.call(['defaults', 'read', 'com.apple.screensaver', 'askForPasswordDelay', '-int'])
    print()
    print('Is show hidden files enabled? (May say YES/NO, but if set using defaults will say 0 = False and 1 = True)')
    print('defaults read com.apple.finder AppleShowAllFiles -bool')
    hidden = subprocess.call(['defaults', 'read', 'com.apple.finder', 'AppleShowAllFiles', '-bool'])
    print()

    title = "OSX Full List Of Defaults Domains"
    little_title(title)

    print()
    subprocess.call(['defaults domains | tr \',\' \'\\n\''], shell=True)
    print()

    title = 'OSX Current NVRAM Variable values'
    little_title(title)
 
    print()
    subprocess.call(['nvram', '-p'])
    print()
    
    title = "OSX # of open files and their processes"
    little_title(title)

    print()
    subprocess.call(['lsof | awk \'{print $1}\' | sort | uniq -c | sort'], shell=True)
    print()

    title = "OSX Other Hardware And Software Configuration"
    big_title(title)

    print()
    
    title = "OSX - Diskutil Partition Output"
    little_title(title)
    print()
    
    print()
    subprocess.call(['diskutil list'], shell=True)
    print()

    title = "OSX Full Disk Info Output - Based On Partitions"
    little_title(title)
    print()
    subprocess.call(['for i in `diskutil list | grep /dev`; do diskutil info $i; done'], shell=True)
    print()

#################
# MAIN CODE RUN #
#################


if __name__ == "__main__":
    if sys.platform == 'win32':
        os == 'ntfs'
    elif sys.platform == 'darwin':
        os == 'osx'

    if args.ntfs and args.osx:
        print ("You can't run both Windows and OSX flags on the same system!")
        exit(0)

    if args.ntfs and args.quick:
        print('You chose ntfs and quick flags!')
        quick=True
        runperf()
        runsys()
        runntfs()
    elif args.ntfs:
        print('You chose only the ntfs flag!')
        quick=False
        runperf()
        runsys()
        runntfs()
    elif args.osx and args.quick:
        print('You chose osx and quick flags!')
        quick=True
        runsys()
        runperf()
        runosx()
    elif args.osx:
        print('You chose only the osx flag!')
        quick=False
        runsys()
        runperf()
        runosx()
    else:
        print('You either chose no OS flags or the incorrect ones.')
        if args.quick:
            quick=True
            print('You chose the quick flag! Supressing long running tests!')
        else:
            quick=False
            print('Running all tests!')
        noargs()
    #if len(args) == 0:
    #    noargs()





