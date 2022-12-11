from numpy import array, uint8, uint64


def stringToByteArray(string):
    return array([ord(c) for c in string], dtype=uint8)


def byteArrayToHex(bytearray):
    bin_array = ["{0:0{1}x}".format(b, 2) for b in bytearray]
    return "".join(bin_array)


def hexToByteArray(hex):
    byte = [int(hex[i:i+2], 16) for i in range(0, len(hex)-1, 2)]
    if (len(hex) % 2):
        byte.append(int(hex[-1], 16))
    return array(byte, dtype=uint8)


def rotateLeft(x, y, max_bits=64):
    return uint64((int(x) << y) & (2**max_bits - 1) | (int(x) >> (max_bits - y)))


def rotateRight(x, y, max_bits=64):
    return ((int(x) >> y) | (int(x) << (max_bits - y) & (2 * max_bits - 1)))
