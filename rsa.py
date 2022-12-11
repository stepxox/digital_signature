import random
from math import floor, sqrt


def isPrime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, floor(sqrt(n))):
        if n % i == 0:
            return False
    return True


def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a


def inverseModulus(a, b):
    if a == 0:
        return b, 0, 1

    g, x1, y1 = inverseModulus(b % a, a)

    x = y1 - (b // a) * x1
    y = x1

    return g, x, y


minNumber = 1e6
maxNumber = 1e12


def getPrime():
    num = 0
    while not isPrime(num):
        num = random.randint(minNumber, maxNumber)
    return num


def getKeys():
    p = getPrime()
    q = getPrime()

    n = p * q
    phi = (p - 1) * (q - 1)

    e = random.randrange(1, phi)

    while gcd(e, phi) != 1:
        e = random.randrange(1, phi)

    d = inverseModulus(e, phi)[1]

    return (d, n), (e, n)


def encrypt(key, text):
    e, n = key
    cipher = []
    for char in text:
        a = ord(char)
        cipher.append(pow(a, e, n))
    return cipher


def decrypt(key, cipher):
    text = ""
    d, n = key
    for num in cipher:
        a = pow(num, d, n)
        text = text + str(chr(a))
    return text
