import json
import socket
import LED_control
import sys
import subprocess
import threading
from thread import start_new_thread
import logging


__author__ = 'DNAPhone S.r.l.'


logging.basicConfig()
log = logging.getLogger("logger")
log.setLevel(logging.DEBUG)

HOST = ''
PORT = 1027

TERMINATION_STRING = '{}'  # The client sends it to end the communication


class SocketServer(threading.Thread):

    def __init__(self, running):
        threading.Thread.__init__(self)
        self.running = running

        global s

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    def run(self):

        # Bind socket to local host and port
        try:
            s.bind((HOST, PORT))
        except socket.error as msg:
            log.error("Bind failed. Error Code : %s . Message: %s" % (str(msg[0]), msg[1]))
            sys.exit()

        # Start listening on the socket
        s.listen(10)

        # Connection handler running on a new thread
        def client_thread(conn, client_ip):

            while True:

                try:

                    data = conn.recv(1024)

                    if not (
                        data.rstrip() == TERMINATION_STRING):  # Removing \r\n from the end of data with rstrip

                        try:
                            j = json.loads(data.rstrip())

                            if 'type' in j and j['type'] == 'Command':

                                if 'attributes' in j:

                                    command_attributes = j['attributes'][0]

                                    if 'value' in command_attributes and 'name' in command_attributes:

                                        if command_attributes['value'] == 'CHANGE_MICROSCOPE_LED_BRIGHTNESS':

                                            led_brightness = command_attributes['led_brightness']

                                            # Change the brightness of the microscope led
                                            led_brightness = 1024 - int(led_brightness)
                                            LED_control.change_led_status('ON', int(led_brightness))

                                            reply = '{"contextResponses": [{"contextElement": {"type": "Answer","isPattern": "false","id": "appCommands","attributes": [{"name": "CHANGE_MICROSCOPE_LED_BRIGHTNESS","type": "string","value": ""}]},"statusCode": {"code": "200","reasonPhrase": "OK"}}]}\n'

                                        elif command_attributes['value'] == 'TURN_OFF':

                                            reply = '{"contextResponses": [{"contextElement": {"type": "Answer","isPattern": "false","id": "appCommands","attributes": [{"name": "TURN_OFF","type": "string","value": ""}]},"statusCode": {"code": "200","reasonPhrase": "OK"}}]}\n'

                                            conn.sendall(reply)

                                            subprocess.call(["sudo", "shutdown", "-h", "now"])

                                        else:
                                            conn.sendall('{"contextResponses": [{"contextElement": {"type": "Answer","isPattern": "false","id": "appCommands","attributes": [{"name": "JSON_ERROR","type": "string","value": ""}]},"statusCode": {"code": "400","reasonPhrase": "Unknown command"}}]}\n')
                                            log.error("Unknown command")
                                            break

                                        conn.sendall(reply)
                                        log.debug('Sent reply %s to %s' % (reply, client_ip))

                                    else:
                                        conn.sendall('{"contextResponses": [{"contextElement": {"type": "Answer","isPattern": "false","id": "appCommands","attributes": [{"name": "JSON_ERROR","type": "string","value": ""}]},"statusCode": {"code": "400","reasonPhrase": "JSON error: name element missing"}}]}\n')
                                        log.error("The message does not include the name element")
                                        break

                                else:
                                    conn.sendall('{"contextResponses": [{"contextElement": {"type": "Answer","isPattern": "false","id": "appCommands","attributes": [{"name": "JSON_ERROR","type": "string","value": ""}]},"statusCode": {"code": "400","reasonPhrase": "JSON error: attributes element missing"}}]}\n')
                                    log.error("The message does not include the attributes element")
                                    break

                            else:
                                conn.sendall('{"contextResponses": [{"contextElement": {"type": "Answer","isPattern": "false","id": "appCommands","attributes": [{"name": "JSON_ERROR","type": "string","value": ""}]},"statusCode": {"code": "400","reasonPhrase": "JSON error: type element missing"}}]}\n')
                                log.error("The message does not include the type element")
                                break

                        except ValueError:
                            conn.sendall('{"contextResponses": [{"contextElement": {"type": "Answer","isPattern": "false","id": "appCommands","attributes": [{"name": "JSON_ERROR","type": "string","value": ""}]},"statusCode": {"code": "400","reasonPhrase": "JSON decoding error"}}]}\n')
                            log.error("An error occurred during json decoding")
                            break

                    else:
                        break

                except socket.error:
                    log.error("Connection closed by the client")
                    break

            conn.close()
            log.error("Connection closed")

        accepted_connections = 0

        while self.running:
            log.debug('Waiting for a new connection...')
            connection, client_address = s.accept()
            log.debug('Connected with %s : %s' % (client_address[0], str(client_address[1])))

            accepted_connections += 1

            log.debug('Accepted %d connections' % accepted_connections)

            start_new_thread(client_thread, (connection, client_address[0]))

        s.close()
        log.debug('Server stopped')
