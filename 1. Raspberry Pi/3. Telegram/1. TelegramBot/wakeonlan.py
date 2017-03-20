import logging
import os
import paramiko
import socket
import struct
import threading
import time

LOGGER = logging.getLogger(__name__)
server_mac = 'ee:b7:b8:74:0c:c6'
Debug = True

class WakeOnLan(object):

    def __init__(self, BROADCAST_IP='255.255.255.255', DEFAULT_PORT=9):
        self.BROADCAST_IP = BROADCAST_IP
        self.DEFAULT_PORT = DEFAULT_PORT

    def create_magic_packet(self, macaddress):
        """
        Create a magic packet which can be used for wake on lan using the
        mac address given as a parameter.

        Keyword arguments:
        :arg macaddress: the mac address that should be parsed into a magic
                         packet.

        """
        if len(macaddress) == 12:
            pass
        elif len(macaddress) == 17:
            sep = macaddress[2]
            macaddress = macaddress.replace(sep, '')
        else:
            msg = 'Incorrect MAC address format'
            LOGGER.error(msg)
            raise ValueError(msg)

        # Pad the synchronization stream
        data = b'FFFFFFFFFFFF' + (macaddress * 20).encode()
        send_data = b''

        # Split up the hex values in pack
        for i in range(0, len(data), 2):
            send_data += struct.pack(b'B', int(data[i: i + 2], 16))
        return send_data

    def send_magic_packet(self, *macs, **kwargs):
        """
        Wakes the computer with the given mac address if wake on lan is
        enabled on that host.

        Keyword arguments:
        :arguments macs: One or more macaddresses of machines to wake.
        :key ip_address: the ip address of the host to send the magic packet
                         to (default "255.255.255.255")
        :key port: the port of the host to send the magic packet to
                   (default 9)

        """
        packets = []
        ip = kwargs.pop('ip_address', self.BROADCAST_IP)
        port = kwargs.pop('port', self.DEFAULT_PORT)
        for k in kwargs:
            msg = ('send_magic_packet() got an unexpected keyword '
                            'argument {!r}'.format(k))
            LOGGER.error(msg)
            raise TypeError(msg)

        for mac in macs:
            packet = self.create_magic_packet(mac)
            packets.append(packet)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        try:
            sock.connect((ip, port))
            for packet in packets:
                sock.send(packet)
        except Exception:
            print 'Failed to connect'
        else:
            sock.close()
            return True


class GetAdaFruit(threading.Thread):

    def __init__(self, IP='192.168.1.10', Username='media'):
        threading.Thread.__init__(self)
        self.IP = IP
        self.Username = Username
        self.wakeonlan = WakeOnLan()
        self.Ran = False
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.client.connect(self.IP, username=self.Username)
        except Exception:
            msg = 'Failed to connect to host'
            LOGGER.exception(msg)

    def run(self):
        count = 0
        while True:
            count += 1
            time.sleep(10)
            try:
                reply = aio.receive_next(adafruit_feed)
            except RequestError:
                msg = 'Received nothing from Adafruit feed.'
                if Debug: print msg
                LOGGER.exception(msg)
            else:
                if reply.value.encode('utf-8') in ['SwitchOn', 'SystemOn']:
                    if not self.Ran:
                        msg = 'Wake-On-Lan Activated at %s' %time.ctime()
                        LOGGER.info(msg)
                        if Debug: print msg
                        try:
                            self.wakeonlan.send_magic_packet(server_mac)
                            reply.delete(adafruit_feed, reply.id)
                            self.Ran = True
                        except:
                            pass
                    elif count == 5:
                        count = 0
                        self.Ran = False
                elif reply.value.encode('utf-8') in ['SwitchOff', 'SystemOff']:
                    # ssh to server and execute sudo switchoff, Nopasswd for sudo
                    msg = 'System has been switched Off at %s' %time.ctime()
                    if Debug: print msg
                    LOGGER.info(msg)
                    try:
                        _stdin, _stdout, _stderr = self.client.exec_command('sudo shutdown -P now')
                        reply.delete(adafruit_feed, reply.id)
                    except Exception:
                        msg = 'Failed to switch off server, going brutal.'
                        os.system('/usr/bin/ssh {}@{} \'sudo /sbin/shutdown -P now\' '.format(
                            self.IP, self.Username))
                        LOGGER.exception(msg)
                        if Debug: print msg
                    finally:
                        self.client.close()
                else:
                    if Debug: print str(reply)

Start = GetAdaFruit()
Start.start()
