import numpy as np

import utils

hashLength = 64
rounds = 24
bytes = np.zeros(200, dtype=np.uint8)
texts = np.zeros(25, dtype=np.uint64)
index = 0
size = 72

constants = np.array([0x0000000000000001, 0x0000000000008082, 0x800000000000808a,
                      0x8000000080008000, 0x000000000000808b, 0x0000000080000001,
                      0x8000000080008081, 0x8000000000008009, 0x000000000000008a,
                      0x0000000000000088, 0x0000000080008009, 0x000000008000000a,
                      0x000000008000808b, 0x800000000000008b, 0x8000000000008089,
                      0x8000000000008003, 0x8000000000008002, 0x8000000000000080,
                      0x000000000000800a, 0x800000008000000a, 0x8000000080008081,
                      0x8000000000008080, 0x0000000080000001, 0x8000000080008008], dtype=np.uint64)

rotations = [1,  3,  6,  10, 15, 21, 28, 36, 45, 55, 2,  14,
             27, 41, 56, 8,  25, 43, 62, 18, 39, 61, 20, 44
             ]

piRotations = [
    10, 7,  11, 17, 18, 3, 5,  16, 8,  21, 24, 4,
    15, 23, 19, 13, 12, 2, 20, 14, 22, 9,  6,  1
]


def updateBytes():
    global bytes
    num = 0
    for w in texts:
        mask = np.uint64(0xFF)
        for i in range(8):
            bytes[num] = np.uint8(int(mask & w) >> (8 * i))
            num += 1
            mask = utils.rotateLeft(mask, 8)


def updateTexts():
    j = 0
    for i in range(0, len(bytes)-8, 8):
        byteList = bytes[i:i+8]
        text = np.uint64(0)
        for b in range(len(byteList)):
            text ^= (np.uint64(byteList[b] << 8*b))
        texts[j] = text
        j += 1


def computeKeccak(copiedTexts):
    out = [0 for _ in range(5)]

    for r in range(rounds):
        out = [copiedTexts[i] ^ copiedTexts[i+5] ^ copiedTexts[i+10] ^
               copiedTexts[i+15] ^ copiedTexts[i+20] for i in range(5)]

        for i in range(5):
            for j in range(0, 25, 5):
                copiedTexts[j+i] ^= (out[(i+4) % 5] ^
                                     utils.rotateLeft(out[(i+1) % 5], 1))

        current = copiedTexts[1]
        for i in range(24):
            out[0] = copiedTexts[piRotations[i]]
            copiedTexts[piRotations[i]] = utils.rotateLeft(
                current, rotations[i])
            current = out[0]

        for i in range(0, 25, 5):
            out = [copiedTexts[j + i] for j in range(5)]
            for j in range(5):
                copiedTexts[j + i] ^= np.uint64(int(~out[(j + 1) % 5])
                                                & int(out[(j + 2) % 5]))

        copiedTexts[0] ^= constants[r]

    updateBytes()


def update(data):
    global index, bytes
    j = index
    for i in range(len(data)):
        bytes[j] ^= data[i]
        j += 1
        if (j >= size):
            updateTexts()
            computeKeccak(texts)
            j = 0
    index = j


def initialize():
    global hashLength, rounds, bytes, texts, index, size
    hashLength = 64
    rounds = 24
    bytes = np.zeros(200, dtype=np.uint8)
    texts = np.zeros(25, dtype=np.uint64)
    index = 0
    size = 72


def compute():
    global bytes
    bytes[index] ^= 0x06
    bytes[size - 1] ^= 0x80
    updateTexts()
    computeKeccak(texts)
    hash = np.array([bytes[i] for i in range(hashLength)])
    return hash


def computeFromString(content):
    initialize()
    byteArray = np.array([c for c in content])
    update(byteArray)
    sha = compute()
    return utils.byteArrayToHex(sha)
