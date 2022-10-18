import sys
import datetime
import time
import socket, struct, binascii, platform
from .drefs import DREFs
import numpy as np
from colorama import Fore


class XPlaneIpNotFound(Exception):
    args = "Could not find any running XPlane instance in network."


class XPlaneTimeout(Exception):
    args = "XPlane timeout."


class XPlaneVersionNotSupported(Exception):
    args = "XPlane version not supported."


# TODO: Be capable of storing variables in the PlyAircraft object that have not been created
# TODO: Manage values that the user requests and values that X-Plane sends
# TODO: csv to store the used DREFs and partially automanage them
# TODO: Stop requesting data from Xplane when simulation paused (reducing workload) -> We must be able to restore
#  previous requests (This must be stored)
# TODO: Plot multiple things on top of each other

class PlyAircraft:
    # The following is where X-Plane constantly casts the information required for connection
    CAST_IP = "239.255.1.1"
    CAST_PORT = 49707

    def __init__(self, freq=30):
        super(PlyAircraft, self).__init__()
        self._run = False

        with open('benchmark.csv', "w") as file:
            file.truncate()
            file.write('\n')

        print("Creating aircraft")

        # Open a UDP Socket to receive on Port 49000
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(3.0)

        self.findXplane()

        # list of requested datarefs with index number
        self.datarefidx = 0
        self.datarefs = {}
        self.my_vals = {}
        # values from xplane
        self.xplaneValues = {}
        self.defaultFreq = 30

        self.start_time = datetime.datetime.now()

    def _start(self):
        self.set(DREFs.override_aero, True)
        self.set(DREFs.override_torque, 1)
        self._run = 1

    def shut_down(self):
        self.set(DREFs.override_aero, 0)
        self.set(DREFs.override_aero, 0)
        self._run = 0

    def new(self, name, val=None):
        # TODO: Check if the variable already exists
        # TODO: Implement this as dictionary so they can be logged in separate file
        exec(f'self.{name} = {val}')

    @property
    def run(self):
        """ This property acts like a boolean but using integers to allow for additional modes:
        - 0 means aircraft is not running
        - 1 means aircraft is running normally
        - 2 means aircraft has crashed
        """
        return self._run

    @run.setter
    def run(self, value):
        if self.run == 2:
            print("Aircraft thread has crashed")

        elif value == 1:
            self._start()
            self._run = 1

        elif value == 0:
            self.shut_down()
            self._run = 0

    def get_all(self):
        out_dict = self.xplaneValues | self.my_vals
        out_dict['running'] = self.run

        return out_dict

    def get(self, dref):

        if dref not in self.get_all().keys():
            print(
                Fore.YELLOW + f"It is the first time {dref} is requested and it was not initialized. We are initializing it for you.\nNext time remmember to initialize the required DREFs at the start")
            print(Fore.YELLOW + "Note we will fetch all values to be able to return something")
            print(Fore.YELLOW + "This may raise issues in data logging")
            self.addFreqValue(dref, self.defaultFreq)
            self.update()

        return self.get_all()[dref]

    def __del__(self):
        # Tell X-Plane to stop sending data
        for i in range(len(self.datarefs)):
            self.addFreqValue(next(iter(self.datarefs.values())), freq=0)
        self.socket.close()

    def set(self, dataref, value):
        '''
        Write Dataref to XPlane
        DREF0+(4byte byte value)+dref_path+0+spaces to complete the whole message to 509 bytes
        DREF0+(4byte byte value of 1)+ sim/cockpit/switches/anti_ice_surf_heat_left+0+spaces to complete to 509 bytes
        '''

        cmd = b"DREF"
        dataref = dataref + '\x00'
        string = dataref.encode('utf-8')
        message = "".encode()
        if type(value) in [float, np.float64]:
            message = struct.pack("=5sf500s", cmd, float(value), string)
        elif type(value) == int:
            message = struct.pack("=5sf500s", cmd, value, string)
        elif type(value) == bool:
            message = struct.pack("=5sf500s", cmd, int(value), string)

        try:
            assert (len(message) == 509)
            self.socket.sendto(message, (self.conn["IP"], self.conn["Port"]))
            with open('benchmark.csv', 'a') as file:
                now = datetime.datetime.now()
                current_time = now.strftime("%H:%M:%S.%f")
                file.writelines(f"{current_time},{dataref},{value}\n")

        except AssertionError:
            print(Fore.RED + f"Assertion error on {dataref} with value {value} and datatype {type(value)}")
            self.run = 2

        self.my_vals[dataref] = value

    def update(self):
        try:
            # Receive packet
            data, addr = self.socket.recvfrom(
                1472)  # maximum bytes of an RREF answer X-Plane will send (Ethernet MTU - IP hdr - UDP hdr)
            # Decode Packet
            retvalues = {}
            # * Read the Header "RREFO".
            header = data[0:5]
            if (header != b"RREF,"):  # (was b"RREFO" for XPlane10)
                print("Unknown packet recieved: ", binascii.hexlify(data))
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

    def addFreqValue(self, dataref, freq=None):

        '''
        Configure XPlane to send the dataref with a certain frequency.
        You can disable a dataref by setting freq to 0.
        '''

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

    def findXplane(self):
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
            print("XPlane IP not found.")
            raise XPlaneIpNotFound()
        finally:
            sock.close()

        return self.conn

    def custom_xplane_conn(self):
        pass