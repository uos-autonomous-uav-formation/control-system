__author__ = "Alvaro Sierra Castro"
__version__ = "1.0.0" # Using https://semver.org/ standard
__maintainer__ = "Alvaro Sierra Castro"
__credits__ = ["Andrea Da Ronch"]
__email__ = "asc1g19@soton.ac.uk"
__status__ = "Development"


import sys
import datetime
import time
import socket, struct, binascii, platform
from .drefs import DREFs
import numpy as np
from colorama import Fore


class XPlaneIpNotFound(Exception):
    args = "Could not find any running XPlane instance in network."


class InvalidPacketSize(Exception):
    args = "Packet size for {dref:s} is invalid. Size of data packet is {size:s} for a maximum of {max:s}"

    def __init__(self, **kwargs):
        """ Raise when too much data is being packet to send to X-Plane

        Message format "Packet size for {dref:s} is invalid. Size of data packet is {size:s} for a maximum of {max:s}"

        :param kargs: parameters for formatting.
        """

        super(InvalidPacketSize, self).__init__(self.args.format(**kwargs))


class XPlaneTimeout(Exception):
    args = "XPlane timeout"


class XPlaneVersionNotSupported(Exception):
    args = "XPlane version not supported"


# TODO: Be capable of storing variables in the PlyAircraft object that have not been created
# TODO: Manage values that the user requests and values that X-Plane sends
# TODO: csv to store the used DREFs and partially automanage them
# TODO: Stop requesting data from Xplane when simulation paused (reducing workload) -> We must be able to restore
#  previous requests (This must be stored)
# TODO: Plot multiple things on top of each other

class Simulator:
    # The following is where X-Plane constantly casts the information required for connection
    CAST_IP = "239.255.1.1"
    CAST_PORT = 49707
    MAX_PACKET_SIZE = 509

    def __init__(self, freq=30):
        super(Simulator, self).__init__()
        self._run = False

        # Open a UDP Socket to receive on Port 49000
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(3.0)

        self._find_xplane()

        # list of requested datarefs with index number
        self.datarefidx = 0
        self.datarefs = {}
        self.my_vals = {}
        # values from xplane
        self.xplaneValues = {}
        self.defaultFreq = 30

        self.start_time = datetime.datetime.now()

    # def _start(self):
    #     self.set(DREFs.override_aero, True)
    #     self.set(DREFs.override_torque, 1)
    #     self._run = 1
    #
    # def shut_down(self):
    #     self.set(DREFs.override_aero, 0)
    #     self.set(DREFs.override_aero, 0)
    #     self._run = 0

    def new(self, name, val=None):
        # TODO: Check if the variable already exists
        # TODO: Implement this as dictionary so they can be logged in separate file
        exec(f'self.{name} = {val}')

    # @property
    # def run(self):
    #     """ This property acts like a boolean but using integers to allow for additional modes:
    #     - 0 means the connection is not running
    #     - 1 means the connection is running normally
    #     - 2 means the connection has crashed
    #     """
    #     return self._run
    #
    # @run.setter
    # def run(self, value):
    #     if self.run == 2:
    #         print("Aircraft thread has crashed")
    #
    #     elif value == 1:
    #         self._start()
    #         self._run = 1
    #
    #     elif value == 0:
    #         self.shut_down()
    #         self._run = 0

    def get_all(self):
        out_dict = self.xplaneValues | self.my_vals
        out_dict['running'] = self.run

        return out_dict

    def get(self, dref):

        if dref not in self.get_all().keys():
            # print(
            #     Fore.YELLOW + f"It is the first time {dref} is requested and it was not initialized. We are initializing it for you.\nNext time remmember to initialize the required DREFs at the start")
            # print(Fore.YELLOW + "Note we will fetch all values to be able to return something")
            # print(Fore.YELLOW + "This may raise issues in data logging")
            self.add_freq_value(dref, self.defaultFreq)
            self.update()

        return self.get_all()[dref]

    def __del__(self):
        # Tell X-Plane to stop sending data
        for i in range(len(self.datarefs)):
            self.add_freq_value(next(iter(self.datarefs.values())), freq=0)
        self.socket.close()

    def set(self, dataref, value):
        """ Set a value on X-Plane.

        See https://developer.x-plane.com/datarefs/ for available DREFs.


        :param dataref: Data-ref of the variable to be set. Must be in the form of sim/operation/override/override_torque_forces
        :param value: The value to set the dref to. Watch for datatypes.
        :return:
        """

        cmd = b"DREF"
        dataref = dataref + '\x00'
        string = dataref.encode('utf-8')
        message = "".encode()

        message = struct.pack("=5sf500s", cmd, float(value), string)

        # Check packet size
        if len(message) == self.MAX_PACKET_SIZE:
            raise InvalidPacketSize(dref=dataref, size=len(message), max=self.MAX_PACKET_SIZE)

        else:
            self.socket.sendto(message, (self.conn["IP"], self.conn["Port"]))

        self.my_vals[dataref] = value

    def update(self):
        try:
            # Receive packet
            data, addr = self.socket.recvfrom(1472)  # maximum bytes of an RREF answer X-Plane will send (Ethernet MTU - IP hdr - UDP hdr)
            # Decode Packet
            retvalues = {}
            # * Read the Header "RREFO".
            header = data[0:5]
            if (header != b"RREF,"):  # (was b"RREFO" for XPlane10)
                print(Fore.YELLOW + "Unknown packet recieved: ", binascii.hexlify(data))
            else:
                # * We get 8 bytes for every dataref sent:
                #   An integer for idx and the float value.
                values = data[5:]
                lenvalue = 8
                numvalues = int(len(values) / lenvalue)
                for i in range(0, numvalues):
                    singledata = data[(5 + lenvalue * i):(5 + lenvalue * (i + 1))]
                    (idx, value) = struct.unpack("<if", singledata)
                    if idx in self.datarefs.keys():
                        # convert -0.0 values to positive 0.0
                        if value < 0.0 and value > -0.001:
                            value = 0.0
                        retvalues[self.datarefs[idx]] = value
            self.xplaneValues.update(retvalues)
        except:
            raise XPlaneTimeout
        return self.xplaneValues

    def add_freq_value(self, dataref: str, freq: int=None) -> None:
        """ Configure X-Plane to send the data-ref at a specific frequency. To update the data, Simulator.update() must be called

        To disable a dataref set its frequency to 0.

        :param dataref: Dataref of data we are interested in
        :param freq: Frequency (in Hz) at which data is sent from the flight s`imulator to the additional app
        :return: None
        """

        idx = -9999

        if freq == None:
            freq = self.defaultFreq

        if dataref in self.datarefs.values():
            idx = list(self.datarefs.keys())[list(self.datarefs.values()).index(dataref)]
            if freq == 0:
                if dataref in self.xplaneValues.keys():
                    del self.xplaneValues[dataref]
                del self.datarefs[idx]
        else:
            idx = self.datarefidx
            self.datarefs[self.datarefidx] = dataref
            self.datarefidx += 1

        cmd = b"RREF\x00"
        string = dataref.encode()
        message = struct.pack("<5sii400s", cmd, freq, idx, string)
        assert (len(message) == 413)
        self.socket.sendto(message, (self.conn["IP"], self.conn["Port"]))

        if self.datarefidx % 100 == 0:
            time.sleep(0.2)

    def _find_xplane(self):
        '''
        Find the IP of XPlane Host in Network.
        It takes the first one it can find.
        '''

        self.conn = {}

        # open socket for multicast group.
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if platform.system() == "Windows":
            sock.bind(('', self.CAST_PORT))
        else:
            sock.bind((self.CAST_IP, self.CAST_PORT))
        mreq = struct.pack("=4sl", socket.inet_aton(self.CAST_IP), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        sock.settimeout(3.0)

        # receive data
        try:
            packet, sender = sock.recvfrom(1472)
            print("XPlane Beacon: ", packet.hex())

            # decode data
            # * Header
            header = packet[0:5]
            if header != b"BECN\x00":
                print("Unknown packet from " + sender[0])
                print(str(len(packet)) + " bytes")
                print(packet)
                print(binascii.hexlify(packet))

            else:
                # * Data
                data = packet[5:21]
                (
                    beacon_major_version,  # 1 at the time of X-Plane 10.40
                    beacon_minor_version,  # 1 at the time of X-Plane 10.40
                    application_host_id,  # 1 for X-Plane, 2 for PlaneMaker
                    xplane_version_number,  # 104014 for X-Plane 10.40b14
                    role,  # 1 for master, 2 for extern visual, 3 for IOS
                    port,  # port number X-Plane is listening on
                ) = struct.unpack("<BBiiIH", data)
                hostname = packet[21:-1]  # the hostname of the computer
                hostname = hostname[0:hostname.find(0)]
                if beacon_major_version == 1 \
                        and beacon_minor_version <= 2 \
                        and application_host_id == 1:
                    self.conn["IP"] = sender[0]
                    self.conn["Port"] = port
                    self.conn["hostname"] = hostname.decode()
                    self.conn["XPlaneVersion"] = xplane_version_number
                    self.conn["role"] = role

                    # print("XPlane Beacon Version: {}.{}.{}".format(beacon_major_version, beacon_minor_version,
                    #                                                application_host_id))
                    print(Fore.GREEN + f"X-Plane was found on {self.conn['IP']}")
                    print(self.conn)

                else:
                    print(Fore.RED + "XPlane Beacon Version not supported: {}.{}.{}".format(beacon_major_version,
                                                                                            beacon_minor_version,
                                                                                            application_host_id))
                    raise XPlaneVersionNotSupported()

        except socket.timeout:
            raise XPlaneIpNotFound()
        finally:
            sock.close()

        return self.conn

    def custom_xplane_conn(self):
        pass
