#!/usr/bin/env python3

'''
#==================================================================================#
# AUTHOR: Chris Gleason                                                            #
# DATE:   1/12/2016                                                                #
# Version:  1.0                                                                    #
# COMMENT: NetScan deamon to monitor state changes for network nodes               #
#==================================================================================#
# Simple UDP/TCP Netscanner to monitor state changes on the network                #
#==================================================================================#

### DESCRIPTION/SYNOPSIS ###

This is a simple daemon that will allow you to scan a network range using ICMP, TCP or UDP and 
store the information in either memory or a file so that it can be referenced at a specific interval
for state changes. It will allow you to log alerts or email them out to a specific email. It will
also, eventually allow you to run it in the background, once I finish up the argparse variables...

### FUTURE WORK ###

1-14-2016 :

I am building this out as a basic ICMP scanner to store up and down states of specific
nodes. I plan to add functions to do TCP and UDP SYN scanning as well as allow for out and in files
to use to store and retrive state data. I also want to add functions for logging and emailing state
alerts. But the first order of business is to get basic ICMP scanning and state alerting to the
console.

2-19-2016 :

- Handle the following Exceptions: 
     * OSError: [Errno 65] No route to host
- Fix --host parameter from changing state if node is up or down. Get initial scan to not count.
- Fix email alerting so that it only sends out a single email per scan round.
- Fix formatting of output table so tabs are lined up.
- Add Validation for things like out and infile locations, IP Format, etc.
- Add argument varaibles so argument values can be passed at runtime and script can be run in the
backround.

4-4-2016 :

Add scan finish statistics, wether it crashes or user kills it with Ctrl+c, output scann settings
Number of times scanned and final version of DB with a close message.

5-7-2016 :

Add a quiet option, so if they actually want to demonize it it will stay quiet and won't dump active
data to the terminal. Then once killed or crashed it will print out the final state dict.

### REQUIREMENTS ###

Requires Python 3 and OSX to run. If you read the script carefully you could redesign for python 2
and for other platforms. The OSX specific subprocess calls and the subnet mask conversion are really
the only platform dependent code.

### NOTES ###

IPAddress module will do a lot of the heavy lifting with regards to calculating subnet nodes using a
CIDR (https://docs.python.org/3/howto/ipaddress.html)

Seems like the socket generator has a hard time keeping up if the scanner runs to fast to often. Not
sure if it's flood protection or the TCP stack coming unravelled. I haven't done any packet filtering to
see what's happening at the packet level except to make sure the original scnaner is indeed sending
raw ICMP, but I did find that if I set the time out too low and the scann frequency too low, that
eventually the scanner will halt with a no route to host error. I found the sweet spot is:

timeout > .05 seconds
frequency > 30 seconds

When running with these threshholds the scanner will run continuously with few issues. If you're
scanning larger networks, it may make sense to lower the timeout. I find it works fine at .01 but will
eventually fail if you scann to often, so set the frequency higher if you're scanning large subnets.

'''

__version__ = "$Revision: 1.0"

###########
# IMPORTS #
###########

import argparse
import subprocess
import os
import ipaddress
import sys
import time
import random
import select
import socket
import csv
import threading
import smtplib
from datetime import datetime

###########################################
# NON FUNCTION/CLASS SCRIPT RELATED STUFF #
###########################################

if os.geteuid() != 0:
        exit('''

This program creates and uses raw sockets which require root\n\
priviledges to run. Please run it as root in order to use it.

''')

if sys.platform != 'darwin':
    print ("This script was designed to run on OSX. Currently that is the only platform it will work on.")
    exit(0)

parser = argparse.ArgumentParser(description='\
    Network scanning daemon to check for node state changes via TCP/UDP/ICMP. \
    Default (no arguments) will run in the foreground using ICMP and broadcast\
    domain for discovery and will store state data in memory. Default (no arguments)\
    uses true ICMP, so it\'s not usually routed. If you "ping scan" with NMAP that rides\
    over TCP unless you specifically tell it to use the ICMP protocol, so if you are\
    trying to scan a remote subnet, use the --tcp flag.')

parser.add_argument('-t', '--tcp' ,
    action='store_true' ,
    help='Use TCP SYN scanning for discovery - NOT IMPLEMENTED YET')
parser.add_argument('-u', '--udp' ,
    action='store_true' ,
    help='Use UDP SYN scanning for discovery - NOT IMPLEMENTED YET')
parser.add_argument('-q', '--quiet' ,
    action='store_true' ,
    help='Use to demonize netscanner for background processing - NOT IMPLEMENTED YET')
parser.add_argument('-i', '--infile' ,
    action='store_true' ,
    help='Use an existing CSV file instead of scanning the network for initial discovery')
parser.add_argument('-o', '--outfile' ,
    action='store_true' ,
    help='Export stat data to a CSV file')
parser.add_argument('-c', '--cidr' ,
    action='store_true' ,
    help='Use a CIDR block to generate scan range instead of using the broadcast domain')
parser.add_argument('-H', '--host' ,
    action='store_true' ,
    help='Monitor the state of a single host')
parser.add_argument('-e', '--email' ,
    action='store_true' ,
    help='Use a gmail account to send state change alerts to a desired email as well as the console')
parser.add_argument('-l', '--logging' ,
    action='store_true' ,
    help='Log state changes to system logs as well as the console')

args = parser.parse_args()
ip = ""
nm = ""
dd_nm = ""
tout = .1
iface = ""
state_dict = {}
freq = ""
count = 0
rtt = ""
ofile = ""
alert_total = ""
totalruns = 0
t1 = datetime.now()

#############
# FUNCTIONS #
#############


def output_title(title):

    '''
    Function to auto-generate output headers and titles

    output=string
    '''

    titlelen = len(title)
    print('=' * titlelen)
    print(title)
    print('=' * titlelen)

def get_tout(a):

    '''
    Function to solicit timeout from the user
    '''

    global tout

    print()
    tout = input('What timeout would you like to use (in seconds and you can use decimal numbers): ')
    print()
    
    return tout

def get_net_size(netmask):
    
    '''
    Function that helps convert netmask and IP into CIDR block.
    This code was borrowed. I can tell that it turns the inegerized octet of the Hex NetMask
    into a binary number that is then pumped into zfill and stripped of zeros. How it
    actually converts this into a CIDR block I'm not entirely sure yet. I'll figure it out
    later.
    '''

    binary_str = ''
    for octet in netmask:
        binary_str += bin(int(octet))[2:].zfill(8)
    return str(len(binary_str.rstrip('0')))

def get_net_info():

    '''
    Function that pulls net info from the host converts it into subnet info, calculates hosts
    list and dumps it into an array

    output=strings and a dictionary
    '''

    global ip
    global cidr
    global dd_nm
    global iface
    global tout

    iface = input('What interface would you like to use: ')
    get_tout(tout)

    # Get IP from subprocess

    ipcmd = "ifconfig %s | grep netmask | awk {'print $2'}" % (iface)
    ip = subprocess.Popen(ipcmd , shell=True, stdout=subprocess.PIPE)
    ip = ip.stdout.read()
    ip = str(ip).strip('b').strip('\'').strip('\\n')

    # Get Netmask from subprocess

    nmcmd = "ifconfig %s | grep netmask | awk {'print $4'}" % (iface)
    nm = subprocess.Popen(nmcmd , shell=True, stdout=subprocess.PIPE)
    nm = nm.stdout.read()
    nm = str(nm).strip('b').strip('\'').strip('\\n')

    # Convert hexmask to dotted decimal

    i = nm
    prefix = i[0:2]
    first = i[2:4]
    second = i[4:6]
    third = i[6:8]
    forth = i[8:10]

    oct1 = "0x{}".format(first)
    oct2 = "0x{}".format(second)
    oct3 = "0x{}".format(third)
    oct4 = "0x{}".format(forth)

    oct1 = int(oct1, 0)
    oct2 = int(oct2, 0)
    oct3 = int(oct3, 0)
    oct4 = int(oct4, 0)

    dd_nm = ("" + str(oct1) + "." + str(oct2) + "." + str(oct3) + "." + str(oct4))
    dd_nm = str(dd_nm)

    # Convert IP and dotted decimal netmask to a CIDR block

    splitip = ip.split('.')
    splitnm = dd_nm.split('.')
    net_start = [str(int(splitip[x]) & int(splitnm[x]))
                 for x in range(0,4)]    
    cidr = str('.'.join(net_start) + '/' + get_net_size(splitnm))

    ### RETURNS ###

    return cidr
    return dd_nm
    return ip
    return iface
    return tout

def print_net_info(a, b, c):
    
    '''
    Test function to see what is being returned after each stage
    '''

    print ()

    title="NETWORK INFORMATION"
    output_title(title)

    global cidr
    global dd_nm
    global ip

    print ()
    print ("IP is " + b)
    print ("Netmask is " + c)
    print ("CIDR is " + a)

def chk(data):

    '''
    Function that validates data being sent to ping function
    '''

    x = sum(a + b * 256 for a, b in zip(data[::2], data[1::2] + b'\x00')) & 0xFFFFFFFF
    x = (x >> 16) + (x & 0xFFFF)
    x = (x >> 16) + (x & 0xFFFF)
    return (~x & 0xFFFF).to_bytes(2, 'little')

def ping(addr, timeout=tout):

    '''
    This Function creates a raw socket using ICMP, then connects to an address
    using that socket, recording the time it takes to return. You can specify
    timeout in the functions arguments. Currently uses user input.
    '''

    with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as conn:
        payload = random.randrange(0, 65536).to_bytes(2, 'big') + b'\x01\x00'
        packet  = b'\x08\x00' + b'\x00\x00' + payload
        packet  = b'\x08\x00' + chk(packet) + payload
        conn.connect((addr, 80))
        conn.sendall(packet)

        start = time.time()

        while select.select([conn], [], [], max(0, start + timeout - time.time()))[0]:
            packet    = conn.recv(1024)[20:]
            unchecked = packet[:2] + b'\0\0' + packet[4:]

            if packet == b'\0\0' + chk(unchecked) + payload:
                return time.time() - start


def tcp_scan(addr, port):

    '''
    Function for scanning with TCP
    '''
    global result

    #start = time.time()
    #while start - time.time() > timeout:
    s= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = s.connect_ex((addr, port))
    s.close()
    return result
    #    if result == 0:
    #        return time.time() - start


def initial_net_scan(a):

    '''
    Function takes cidr variable from get_net_info, creates a list of IP's
    then scans them all using the ping function
    '''

    global totalruns
    global state_dict

    net4 = ipaddress.ip_network(a)
    print ()
    print ("Calculating network host list and scanning.")
    print ()
    print ("Please be patient, this may take some time:")
    print ()
    if not (args.tcp) and not (args.udp):
        for x in net4.hosts():
            state_dict.update({x : [ping(str(x), float(tout)), 0]})
    if args.tcp:
        for x in net4.hosts():
            state_dict.update({x : [tcp_scan(str(x), int(port)), 0]})

    totalruns += 1

    return totalruns
    return state_dict

def redundant_net_scan(a, host, port):

    '''
    Function takes the state_dict generated from the initial_net_scan function
    then scans the IP's again an calculates if the state has changed
    '''

    global totalruns
    global count
    global state_dict
    global alert_total

    print ("Rescanning, this may take some time:")
    print ()
    alert_total = ""
    for x,y in a.items():
        print_ip = x
        rtt1 = y[0]
        if args.tcp:
            start = time.time()
            tcp_scan(str(host), int(port))
            if result != 0:
                rtt2 = None
            else:
                rtt2 = time.time() - start
            print ('TCP USED!')
        else:
            rtt2 = ping(str(x), float(tout))
            print ('ICMP USED')
        count = y[1]
        if type(rtt1).__name__ == "float" and type(rtt2).__name__ == "NoneType"\
        or type(rtt1).__name__ == "NoneType" and type(rtt2).__name__ == "float":
            alert = "State changed for " + str(print_ip) + ". It went from " + str(rtt1) + " to " + str(rtt2) + ".\n"
            alert_total+=alert
            count = y[1] + 1
            state_dict.update({x : [rtt2, count]})
            count = 0
        else:
            state_dict.update({x : [rtt2, count]})
            
    if args.logging:
        #print(alert_total)
        log_alert(alert_total)

    if args.email:
        email_alert(toaddrs, username, password, alert_total)

    print(alert_total)

    totalruns += 1

    return count
    return state_dict
    return alert_total
    return totalruns

def print_dict(sd):

    '''
    Prints out state dictionary in formatted output
    '''

    global state_dict

    for x,y in sd.items():
        print_ip = x
        print_rtt = y[0]
        print_count = y[1]
        print ("IP: " + str(print_ip) + "\t\tRTT: " + str(print_rtt) + "\t\t\tChange Count: " + str(print_count))

def csv_writer(ofile):

    '''
    Function to take State Dictionary and output to to CSV file
    '''

    writer = csv.writer(open(ofile, 'w'))
    for x,y in state_dict.items():
        writer.writerow([x, y[0], y[1]])

def email_alert(toaddrs, username, password, alerti_total):

    '''
    Function to send state change list to designated email
    '''

    fromaddr = 'netscanalert@chrisgleason.com'
    msg = alert_total
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username,password)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()

def log_alert(alert):

    '''
    Function to take state change list and log in syslog
    '''

    subprocess.Popen("logger " + alert, shell=True, stdout=subprocess.PIPE)

############
# MAIN RUN #
############


if __name__ == "__main__":

    '''
    Main Code run
    '''


    try:

        title='Netscanner - Network state discovery and change alerter daemon'
        output_title(title)
        print()
        print('Hit Ctrl+C to kill the deamon if it\'s running in the foreground')
        print()

        print()
        freq = input('What frequency would you like the scanner to run (in seconds): ')
        print()

        get_tout(tout)

        if args.tcp or args.udp:
            port = input('What port would you like to use to scan against? : ')
            print ()

        if args.cidr or args.infile or args.host:
            pass
        else:
            get_net_info()

        if args.cidr:
            cidr = input('What CIDR block would you like to use (use X.X.X.X/XXX format) : ')
            #get_tout(tout)
            print ()
            print ('You chose CIDR block: ' + cidr)

        if args.infile:
            ifile = input('Please specify the explicit path to the file you want to import: ')
            reader = csv.reader(open(ifile, 'r'))
            state_dict = {}
            for row in reader:
                ip, rtt, count = row
                if rtt == '':
                    rtt = 'None'
                state_dict[ip] = [rtt, count]

        if args.outfile:
            ofile = input('Please specify the explicit path to the file you want to export the data to: ')

        if args.host:
            global host
            host = input('What host would you like to scan (Use an IP in dotted decimal format X.X.X.X): ')
            if not (args.tcp) and not (args.udp):
                rtt = ping(str(host), float(tout))
                state_dict.update({host : [rtt, count]})
            if args.tcp:
                start = time.time()
                tcp_scan(str(host), int(port))
                if result != 0:
                   rtt = None
                else:
                   rtt = time.time() - start
                state_dict.update({host : [rtt, count]})
            cidr = host + "/32"

        if args.email:
            toaddrs  = input('What email are you sending alerts to: ')
            username = input('What is your gmail username: ')
            password = input('What is your gmail password (you may need an application specific password): ')

        if args.cidr or args.infile:
            pass
        else:
            print_net_info(cidr, ip, dd_nm)

        print ()
        input('Press Enter to start the scan')
        if not args.infile:
            os.system('clear')
            initial_net_scan(cidr)
            print_dict(state_dict)
            if args.outfile:
                csv_writer(ofile)
            time.sleep(int(freq))


        while True:
            os.system('clear')
            redundant_net_scan(state_dict, host, port)
            print_dict(state_dict)
            if args.outfile:
                csv_writer(ofile)
            time.sleep(int(freq))

    except KeyboardInterrupt:
        t2 = datetime.now()
        timetotal = t2 - t1
        print ()
        print ("===================================================================================")
        print ()
        print_dict(state_dict)
        print ()
        print ("===================================================================================")
        print ()
        print ("You pressed Ctrl+C")
        print ()
        print ("Your scan ran through " + str(totalruns) + " cycles, every " + str(freq) + " seconds.")
        print ()
        print ("The scan ran for a total of " + str(timetotal))
        print ()
        print ("The final data set is above:")
        sys.exit()

    except OSError as e:
        t2 = datetime.now()
        timetotal = t2 - t1
        print ()
        print ('Script crashed')
        print ('Dumping state dict')
        print ()
        print ('====================================================================================')
        print ()
        print_dict(state_dict)
        print ()
        print ('====================================================================================')
        print ()
        print ('There was an OS Error exception, most likely a no route to host. for now, I\'m just')
        print ('dumping the last version of the state dictionary and exiting.')
        print ()
        print ("Your scan ran through " + str(totalruns) + " cycles, every " + str(freq) + " seconds.")
        print ()
        print ("The scan ran for a total of " + str(timetotal))
        print ()
        print ('If you\'re seeing this error a lot, try changing the frequency to at least 30 seconds, and')
        print ('set the timeout to at least .1 for a trial. If it stops, you can tune it down. If it keeps')
        print ('failing, then you should increase both thresholds until it stops')
