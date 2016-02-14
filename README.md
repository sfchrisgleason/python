# python

## Python Scripts

### netscan.py

#### WARNINGS:

netscan.py uses raw sockets, which require root access. This coupled with the fact that it currently will scan your entire broadcast domain if you just arbitrarily run it without any options means that it's currently not in a state to be used by people who don't know what it does. Eventually I will make it so you have to specify all the options you want for it to run, but for now don't use it unless you read through the script and see exactly what it does.

#### Synopsis:

Netscan is an attempt to learn raw socket programming and brush up on some other techniques in Python 3. I've borrowed a bunch of code from all around and currently it is not even version 1. I've uploaded it here on the off chance that someone comes across it and has some input for me to make it less dangerous and cleaner.

It was developed on OSX, but could be easily ported to work on other platforms. As is it would work in general except for the default autodetection of the subnet mask, and other subprocess calls that are unique to OSX.

It will by default (if run with no options):

1. Detect your IP and Subnet Mask, and generate a CIDR block from that
2. Scan that CIDR block using ICMP raw sockets
3. Dump that info into a dictionary in memory to be tallied at a later time

There are a bunch of options which I'm developing one at a time. Currently I've only gotten a few done, and the full function of the scanner isn't complete. I'll update this readme once those are complete and will officially publish V1 once I've had someone sanity check it.
