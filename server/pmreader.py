import serial
import time
import threading
import struct
import queue


class PMReader(threading.Thread):
    def __init__(self, port, queue):
        self.serial = serial.Serial(port)
        self.queue = queue
        self.polling = False
        threading.Thread.__init__(self)

    def close(self):
        self.polling = False
        self.serial.close()

    def run(self):
        self.polling = True
        while self.polling:
            old_byte = new_byte = b'\x00'

            while not (old_byte == b'\xaa' and new_byte == b'\xc0'):
                old_byte = new_byte
                new_byte = self.serial.read(1)

            package = self.serial.read(8)

            self.queue(self.readValues(package))

    def readValues(self, package):
        unpacked = struct.unpack('<HHxxBB', package)
        print("Package: {}. Unpacked: {}".format(package, unpacked))

        checksum = sum(package[:6]) & 255

        if checksum != package[6]:
            print("Checksums do not match. Calculated: {},  Recieved: {}".format(checksum, package[6]))
            return None, None
        if package[7] != 171:
            print("Recieved package did not end correctly.")
            return None, None

        pm_25 = unpacked[0] / 10
        pm_10 = unpacked[1] / 10
        return pm_25, pm_10

    def printValues(self):
        pm_25, pm_10 = sensor.readValues()
        print("PM2.5 value: {} μg/m^3, PM10 {} μg/m^3".format(pm_25, pm_10))


if __name__ == "__main__":
    myQueue = queue.Queue()
    try:
        sensor = pmsensor("COM4", myQueue)
        sensor.start()
        while True:
            if not myQueue.empty():
                pm_25, pm_10 = myQueue.get()
                print("PM2.5 value: {} μg/m^3, PM10 {} μg/m^3".format(pm_25, pm_10))
            time.sleep(0.8)

    except KeyboardInterrupt:
        print("Closing serial port...")
        sensor.close()