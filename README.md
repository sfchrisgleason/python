# python

## Python Scripts

### netscan.py

##### Python 3.x

#### WARNINGS:

##### THIS SCRIPT WILL DETECT AND SCAN YOUR ENTIRE BROADCAST DOMAIN

If you kick it off, it will detect and scan your entire internal network. While this is a relatively innocuous script in comparison to what's out there, it could mean trouble for you if you are on a network you don't own. Not everyone takes kindly to broad network sweeps against their computers and network infrastructure.

netscan.py uses raw sockets, which require root access. Eventually I will make it so you have to specify all the options you want for it to run, but for now use caution and test the script on a safe network before using it elsewhere.

#### Synopsis:

Netscan is an attempt to learn raw socket programming and brush up on some other techniques in Python 3. I've borrowed a bunch of code from all around and currently it is not even version 1. I've uploaded it here on the off chance that someone comes across it and has some input for me to make it less dangerous and cleaner.

It was developed on OSX, but could be easily ported to work on other platforms. As is it would work in general except for the default autodetection of the subnet mask, and other subprocess calls that are unique to OSX.

It will by default (if run with no options):

1. Detect your IP and Subnet Mask, and generate a CIDR block from that
2. Scan that CIDR block using ICMP raw sockets
3. Dump that info into a dictionary in memory to be tallied at a later time

Below is the output of the helpfile.

usage: netscan.py [-h] [-t] [-q] [-i] [-o] [-c] [-H] [-e] [-l]

Network scanning daemon to check for node state changes via TCP/UDP/ICMP.
Default (no arguments) will run in the foreground using ICMP and broadcast
domain for discovery and will store state data in memory. Default (no
arguments) uses true ICMP, so it's not usually routed. If you "ping scan" with
NMAP that rides over TCP unless you specifically tell it to use the ICMP
protocol, so if you are trying to scan a remote subnet, use the --tcp flag.

optional arguments:

  -h, --help     show this help message and exit

  -t, --tcp      Use TCP SYN/ACK scanning for discovery

  -q, --quiet    Use to demonize netscanner for background processing - NOT
                 IMPLEMENTED YET

  -i, --infile   Use an existing CSV file instead of scanning the network for
                 initial discovery

  -o, --outfile  Export stat data to a CSV file

  -c, --cidr     Use a CIDR block to generate scan range instead of using the
                 broadcast domain

  -H, --host     Monitor the state of a single host

  -e, --email    Use a gmail account to send state change alerts to a desired
                 email as well as the console

  -l, --logging  Log state changes to system logs as well as the console

EXAMPLES:

> python3 netscan.py --cidr --outfile --logging

This will then prompt for user input for the CIDR block to use, the explicit path for the output file, scan using the default of ICMP and will automatically log to the local log 

> python3 netscan.py --host --tcp

This will then prompt for a specific host to scan, prompt for a TCP port to scan against, then determine the subnet, and scan it with TCP, outputting to the terminal.

==========================================

### civilwar.py

##### Python 3.x

This is a silly civil war game I created when I was learning the basics of Python.

Not much to it.

==========================================

### tictactoe.py

##### Python 3.x

This is another silly little game I made to get ton know python better.

Again, not much to it

==========================================

### sysperf.py

##### python 2.x (Though it does say python3 in the hash-bang it runs on python2)

This is a cross-platform performance and statistical gathering script I started a while back. it was an attempt to write something that might actually be useful to someone. It is by no means in any sort of polished form, but has some interesting stuff in it.

The one thing that I find particularly useful is the OSX defaults section that I feel like I'll use regularly if I'm every trying to parse large bits of system configuration. I asked about that out on the tubes and no one seemed to have a concise answer, so it's nice to have.

It uses arg parse so below is the output form the help file:

iusage: sysperf.py [-h] [--ntfs] [--osx] [--quick]

Print system usage statistics and system information. Default (no args) will

determine OS and run all gather functions

optional arguments:

  -h, --help  show this help message and exit

  --ntfs      Gather Windows information

  --osx       Gather OSX information

  --quick     Suppress long running functions (du, iostat, cpu timing)

==========================================

### shoretel_call_report.py

#### Python 2.x

This is a OSX/Linux script that will mount the Shoretel DVS server of your choice and scrape the logs for all CALL ID's associated with your search term and output them to the terminal along with the BYE code of each call.

It was put together pretty quickly and just uses sys.argv directly, so you have to use the arguments in a specific order for it to work.

Examples:

*python shoretel_call_report.py DvsAdminUsername TmsNcc-160811* IPBX-160811* 192.168.1.100 "Chris Gleason"*

This will invoke the script using DvsAdminUsername to authenticate to the DVS to mount the C$ admin share, and search any TmsNcc logs for the username Chris Gleason, then pull all call ID's associated with it from that log, get the BYE codes for those calls, then pull the call log for that CALL ID and output to the terminal.

