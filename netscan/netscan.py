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
also allow you to either set the process up as a deamon or just run it as a process.

### FUTURE WORK ###

1-14-2016 - I am building this out as a basic ICMP scanner to store up and down states of specific
nodes. I plan to add functions to do TCP and UDP SYN scanning as well as allow for out and in files
to use to store and retrive state data. I also want to add functions for logging and emailing state
alerts. But the first order of business is to get basic ICMP scanning and state alerting to the
console.

2-19-2016 - Handle the following Exceptions: OSError: [Errno 65] No route to host
Fix --host parameter from changing state if node is up or down. Get initial scan to not count.
Add Validation for things like out and infile locations, IP Format, etc.
Fix email alerting so that it only sends out a single email per scan round.

### REQUIREMENTS ###

Requires Python 3 and OSX to run. If you read the script carefully you could redesign for python 2
and for other platforms. The OSX specific subprocess calls and the subnet mask conversion are really
the only platform dependent code.

### NOTES ###

IPAddress module will do a lot of the heavy lifting with regards to calculating subnet nodes using a
CIDR (https://docs.python.org/3/howto/ipaddress.html)

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

###########################################
# NON FUNCTION/CLASS SCRIPT RELATED STUFF #
###########################################


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
    global tout

    print()
    tout = input('What timeout would you like to use (in seconds and you can use decimal numbers): ')
    print()
    
    return tout

def get_net_size(netmask):
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
    timeout in the functions parameter declaration.
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

def initial_net_scan(a):

    '''
    Function takes cidr variable from get_net_info, creates a list of IP's
    then scans them all using the ping function
    '''

    global state_dict

    net4 = ipaddress.ip_network(a)
    print ()
    print ("Calculating network host list and scanning.")
    print ()
    print ("Please be patient, this may take some time:")
    print ()
    for x in net4.hosts():
        state_dict.update({x : [ping(str(x), float(tout)), 0]})

    return state_dict

def redundant_net_scan(a):

    '''
    Function takes the state_dict generated from the initial_net_scan function
    then scans the IP's again an calculates if the state has changed
    '''
    global count
    global state_dict
    global alert_total

    print ("Rescanning, this may take some time:")
    print ()
    alert_total = ""
    for x,y in a.items():
        print_ip = x
        rtt1 = y[0]
        rtt2 = ping(str(x), float(tout))
        if type(rtt1).__name__ == "float" and type(rtt2).__name__ == "NoneType"\
        or type(rtt1).__name__ == "NoneType" and type(rtt2).__name__ == "float":
            alert = "State changed for " + str(print_ip) + ". It went from " + str(rtt1) + " to " + str(rtt2) + "."
            print(alert)
            if args.email:
                email_alert(toaddrs, username, password, alert)
            if args.logging:
                log_alert(alert)
            count = y[1] + 1
            state_dict.update({x : [rtt2, count]})
            count = 0
            #alert_total+=str(alert)
        #if alert_total != '' and args.email:
            #email_alert(toaddrs, username, password, alert_total)
            
    return count
    return state_dict
    return alert_total


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
    writer = csv.writer(open(ofile, 'w'))
    for x,y in state_dict.items():
        writer.writerow([x, y[0], y[1]])

def email_alert(toaddrs, username, password, alert):

    fromaddr = 'netscanalert@chrisgleason.com'
    msg = alert
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username,password)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()

def log_alert(alert):

    subprocess.Popen("logger " + alert, shell=True, stdout=subprocess.PIPE)

############
# MAIN RUN #
############


if __name__ == "__main__":

    '''
    Main Code run
    '''

    if os.geteuid() != 0:
        exit('''

This program creates and uses raw sockets which require root\n\
priviledges to run. Please run it as root in order to use it.

''')

    try:

        title='Netscanner - Network state discovery and change alerter daemon'
        output_title(title)
        print()
        print('Hit Ctrl+C to kill the deamon if it\'s running in the foreground')
        print()

        print()
        freq = input('What frequency would you like the scanner to run (in seconds): ')
        print()

        #if not len(sys.argv) > 1\
        #or args.outfile and not len(sys.argv) > 2\
        #or not len(sys.argv) > 2 and args.email\:
        if args.cidr or args.infile:
            pass
        #or not c in args or not infile in args or not i args:
        else:
            get_net_info()

        if args.cidr:
            cidr = input('What CIDR block would you like to use (use X.X.X.X/XXX format) : ')
            get_tout(tout)
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
            host = input('What host would you like to scan (Use an IP in dotted decimal format X.X.X.X): ')
            get_tout(tout)
            rtt = ping(str(host), float(tout))
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
            redundant_net_scan(state_dict)
            print_dict(state_dict)
            if args.outfile:
                csv_writer(ofile)
            time.sleep(int(freq))

    except KeyboardInterrupt:
        print ("You pressed Ctrl+C")
        sys.exit()
