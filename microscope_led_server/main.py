#!/usr/bin/python

import server
import wiringpi


__author__ = 'DNAPhone S.r.l.'


if __name__ == "__main__":

    wiringpi.wiringPiSetupGpio()

    server_thread = server.SocketServer(True)
    server_thread.start()
