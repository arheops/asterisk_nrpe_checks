#!/usr/bin/python3

import subprocess
import re
import os
import sys
from subprocess import PIPE, Popen
from enum import Enum


import argparse, sys
class NagiosResponseCode(Enum):
    OK = 0
    
    WARNING = 1
    CRITICAL= 2
    
    UNKNOWN = 3

class astChannelsCheck:
    sudo_cmd     = """/usr/sbin/sudo"""
    channels_cmd = """/usr/sbin/asterisk -rx "core show channels count" """
    channels_sample_output = """
    52 active channels
    26 active calls
    3069 calls processed
    """
    def init(self):
        self.return_code = NagiosResponseCode.UNKNOWN.value
        self.return_msg = NagiosResponseCode.UNKNOWN.name
        self.count = 0
    def getParser(self):
        parser = argparse.ArgumentParser()

        parser.add_argument("-w", help="warning treshold")
        parser.add_argument("-c", help="critical treshold")
        parser.add_argument("-C", help="Command: install, channels")
        return parser
    def getArgs(self):
        parser = self.getParser()
        self.args   = parser.parse_args()
        if self.args.C is None:
            print("Use with -h for help")
            sys.exit(3)
        warn_threshold = self.args.w
        if warn_threshold is None:
            warn_threshold = 100
        else:
            warn_threshold = int(warn_threshold)
        self.warn_threshold = warn_threshold
        critical_threshold = self.args.c
        if critical_threshold is None:
            critical_threshold = 1000
        else:
            critical_threshold = int(critical_threshold)
        self.critical_threshold= critical_threshold
    def getCommand(self):
        if self.args.C is None:
           return ''
        return self.args.C
    def makeInstall(self):
        os.system(f"""""echo 'nagios    ALL= NOPASSWD: {self.channels_cmd}'>>/etc/sudoers.d/nagios_asterisk""")
    def getChannels(self):
        self.count = 0
        return_string = ""
        try:
            with Popen(self.sudo_cmd+' '+self.channels_cmd, stdout=PIPE, stderr=None, shell=True) as process:
                output = process.communicate()[0].decode("utf-8")
                (channels, calls, proccessed_calls) = re.findall(r'\d+', output)
                count = int(channels)
                return_string = f"{channels} active channels {calls} active calls {proccessed_calls} calls processed"
                perfomance = f"'channels.active'={channels};{self.warn_threshold};{self.critical_threshold};;"
                perfomance +=f" 'calls.active'={calls};;;;"
                return_string+= ' | '+perfomance
                self.return_code = NagiosResponseCode.OK

        except subprocess.CalledProcessError as e:
            print("ERROR: Error running command:", e)
            self.return_code = NagiosResponseCode.UNKNOWN
        except Exception as e:
            print("ERROR: Error in code", e)
            self.return_code = NagiosResponseCode.UNKNOWN
        self.process_output(return_string)
    def process_output(self, return_string):
        if self.return_code == NagiosResponseCode.UNKNOWN:
            sys.exit(NagiosResponseCode.UNKNOWN.value)
        self.return_msg = NagiosResponseCode.UNKNOWN.name
        if self.count >= self.critical_threshold:
            self.return_code = NagiosResponseCode.CRITICAL.value
            self.return_msg  = NagiosResponseCode.CRITICAL.name
        elif (self.count >= self.warn_threshold):
            self.return_code = NagiosResponseCode.WARNING.value
            self.return_msg  = NagiosResponseCode.WARNING.name
        else:
            self.return_code = NagiosResponseCode.OK.value
            self.return_msg  = NagiosResponseCode.OK.name
        print(self.return_msg + ": " + return_string)
        sys.exit(self.return_code)
    def process(self):
        self.getArgs()
        if self.getCommand() == "install":
            self.makeInstall()
        elif self.getCommand() == "channels":
            self.getChannels()

if __name__ == "__main__":
    ast_chan = astChannelsCheck()
    ast_chan.process()