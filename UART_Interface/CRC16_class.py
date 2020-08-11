POLYNOMIAL = 0x1021
PRESET = 0x1D0F

class CRC16:
    '''
    usage:
    crc('123456789')
    crcb(0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39)
    '''
    def __init__(self):
        self._tab = [ self._initial(i) for i in range(256) ]

    def _initial(self,c):
        crc = 0
        c = c << 8
        for j in range(8):
            if (crc ^ c) & 0x8000:
                crc = (crc << 1) ^ POLYNOMIAL
            else:
                crc = crc << 1
            c = c << 1
        return crc

    def _update_crc(self, crc, c):
        cc = 0xff & c
        tmp = (crc >> 8) ^ cc
        crc = (crc << 8) ^ self._tab[tmp & 0xff]
        crc = crc & 0xffff
        return crc

    def crc(self, str):
        crc = PRESET
        for c in str:
            crc = self._update_crc(crc, ord(c))
            print crc
        return crc

    def crcb(self, i):
        crc = PRESET
        for c in i:
            crc = self._update_crc(crc, c)
        return crc
