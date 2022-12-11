import datetime
import hashlib
import json
import os
import zipfile
from base64 import b64decode, b64encode

import rsa
import sha

# encoding z ascii na utf-8
def ghstrc(t):
    return str(b64encode(t.encode("ascii")).decode("utf-8"))

# ulozeni privatniho a public klice .priv a .pub
def saveKeys(privateKey, publicKey):
    priv = open("key.priv", "w")
    priv.write("RSA ")
    priv.write(ghstrc("".join([str(privateKey[0]), "@", str(privateKey[1])])))
    priv.close()

    pub = open("key.pub", "w")
    pub.write("RSA ")
    pub.write(ghstrc("".join([str(publicKey[0]), "@", str(publicKey[1])])))
    pub.close()

# ulozeni podpisu .sign file 
def saveSignature(signatureFile, signature):
    sign = open(signatureFile, "w")
    sign.write("RSA_SHA3-512 ")
    sign.write(signature)
    sign.close()

# otevreni souboru s textem a ziskani dat (velikost,jmeno, typ, posledni uprava)
def openFile(path, tp="rb"):
    file = open(path, tp)
    _, extension = os.path.splitext(path)
    size = os.path.getsize(path)
    basename = os.path.basename(file.name)
    updatetime = datetime.datetime.fromtimestamp(os.path.getmtime(path))
    content = file.read()
    file.close()
    return content, basename, extension, size, updatetime

# overeni
def verifySignature(computedHex, signature: str, publicKey: str):
    signature = b64decode(signature.replace(
        "RSA_SHA3-512 ", "")).decode("utf-8")

    publicKey = b64decode(publicKey.replace(
        "RSA ", "")).decode("utf-8")

    p1, p2 = publicKey.split("@")

    jsonSignature = json.loads(signature)
    decrypted = rsa.decrypt((int(p1), int(p2)), jsonSignature)

    return computedHex == decrypted


def main():
    # ulozeni promennych podle souboru
    content, basename, extension, size, updatetime = openFile("soubor.txt")
    signatureFileName = basename + ".sign"
    zipFileName = basename + ".zip"

    print("--------")
    print("Soubor:", basename)
    print("Typ:", extension)
    print("Velikost:", size, "bajtů")
    print("Upraveno:", updatetime)
    
    # ziskani a ulozeni priv a pub klice
    privateKey, publicKey = rsa.getKeys()
    saveKeys(privateKey, publicKey)

    # a = hashlib.sha3_512()
    # a.update(content)
    # a.digest()
    
    # ziskani hashe
    computedHex = sha.computeFromString(content)
    print("Hex souboru:", computedHex)
    print("--------")

    # ziskani a ulozeni podpisu .sign soubor
    signatureList = rsa.encrypt(privateKey, computedHex)
    jsonSignature = json.dumps(signatureList)
    signature = ghstrc(jsonSignature)

    saveSignature(signatureFileName, signature)

    # zazipovani
    zipObject = zipfile.ZipFile(zipFileName, "w")
    zipObject.write(basename)
    zipObject.write(signatureFileName)
    zipObject.close()

    # os.remove(signatureFileName)
    
    # porovnani souboru
    input("Uprav obsah souboru a pokracuj...")

    fileAfter = openFile(basename)
    computedHex = sha.computeFromString(fileAfter[0])

    signatureFile = openFile(signatureFileName, "r")
    publicKeyFile = openFile("key.pub", "r")

    isVerified = verifySignature(
        computedHex, signatureFile[0], publicKeyFile[0])
    print("Je overeni ok?:", isVerified)

    input("Uprav soubor na puvodni obsah a pokracuj...")

    fileAfter = openFile(basename)
    computedHex = sha.computeFromString(fileAfter[0])

    signatureFile = openFile(signatureFileName, "r")
    publicKeyFile = openFile("key.pub", "r")

    isVerified = verifySignature(
        computedHex, signatureFile[0], publicKeyFile[0])
    print("Je overeni ok?:", isVerified)


if __name__ == "__main__":
    main()
