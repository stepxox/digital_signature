import datetime
import hashlib
import json
import os
import zipfile
from base64 import b64decode, b64encode
import rsa
# import sha
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5 import QtGui, uic
 
qtCreatorFile = "kantor_ui.ui" # Enter file here.
 
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
 
class MyApp(QMainWindow, Ui_MainWindow):
        
    # encoding z ascii na utf-8
    def ghstrc(self, t):
        return str(b64encode(t.encode("ascii")).decode("utf-8"))
    
    # ulozeni privatniho a public klice .priv a .pub
    def saveKeys(self):
        privateKey, publicKey = rsa.getKeys()
        options = QFileDialog.Options()
        path, _ = QFileDialog.getSaveFileName(self,"Uloz privatni klic", "privKey","Privatni klic (*.priv);;All Files (*)", options=options)
        
        priv = open(path, "w")
        priv.write("RSA ")
        priv.write(self.ghstrc("".join([str(privateKey[0]), "@", str(privateKey[1])])))
        priv.close()
    
        pubKey, _ = QFileDialog.getSaveFileName(self,"Uloz verejny klic", "pubKey","Verejny klic (*.pub);;All Files (*)", options=options)
        pub = open(pubKey, "w")
        pub.write("RSA ")
        pub.write(self.ghstrc("".join([str(publicKey[0]), "@", str(publicKey[1])])))
        pub.close()
        
        self.output.setText("Klice byly vygenerovany")
        
    
    # ulozeni podpisu .sign file 
    
    # otevreni souboru s textem a ziskani dat (velikost, jmeno, typ, posledni uprava)
    def openFile(self, path, tp="rb"):
        file = open(path, tp)
        _, extension = os.path.splitext(path)
        self.typ_2.setText(str(extension))
        self.velikost_2.setText(str(os.path.getsize(path))+" B")
        self.soubor_2.setText(str(os.path.basename(file.name)))
        self.uprava_2.setText(str(datetime.datetime.fromtimestamp(os.path.getmtime(path))))
        self.cesta_2.setText(str(path))
        # content = file.read()
        file.close()
        
    # nacteni originalniho souboru a vytvoreni podpisu .sign file
    def sign(self):
        options = QFileDialog.Options()
        path, _ = QFileDialog.getOpenFileName(self,"Vyber originalni soubor", "","Textovy soubor (*.txt);;All Files (*)", options=options)
        self.openFile(path, tp="rb")
        file = open(path, "rb")
        a = file.read()
        file.close()
        a = hashlib.sha3_512()
        a = a.hexdigest()
        pathPriv, _ = QFileDialog.getOpenFileName(self,"Vyber privatni klic", "","Privatni klic (*.priv);;All Files (*)", options=options)
        m = open(pathPriv, "r")
        privKey = m.read()
        m.close()
        privKey = b64decode(privKey.replace("RSA ", "")).decode("utf-8")
        d, n = privKey.split("@")
        encrypted = str(rsa.encrypt((int(d), int(n)), a))
        pathSigned, _ = QFileDialog.getSaveFileName(self,"Uloz podepsany soubor", "","Podepsany soubor (*.sign);;All Files (*)", options=options)
        #signatureList = rsa.encrypt(privKey, a)
        #jsonSignature = json.dumps(signatureList)
        #signature = self.ghstrc(jsonSignature)
        #self.saveSignature(signatureFileName, signature)
        sign = open(pathSigned, "w")
        sign.write("RSA_SHA3-512 ")
        sign.write(encrypted)
        sign.close()

        zipObject = zipfile.ZipFile("signed.zip", "w")
        zipObject.write(path,os.path.basename(path))
        zipObject.write(pathSigned,os.path.basename(pathSigned))
        zipObject.close()
        self.output.SetText("Soubor byl uspesne podepsan")
        
    # overeni podpisu
    def verifySignature(self, computedHex, signature: str, publicKey: str):
        options = QFileDialog.Options()
        path, _ = QFileDialog.getOpenFileName(self,"Vyber originalni soubor", "","Textovy soubor (*.txt);;All Files (*)", options=options)
        file = open(path, "rb")
        a = file.read()
        file.close()
        a = hashlib.sha3_512()
        a = a.hexdigest()
        pathPriv, _ = QFileDialog.getOpenFileName(self,"Vyber privatni klic", "","Textovy soubor (*.priv);;All Files (*)", options=options)
        path3, _ = QFileDialog.getOpenFileName(self,"Vyber originalni soubor", "","Textovy soubor (*.txt);;All Files (*)", options=options)
        signature = b64decode(signature.replace(
            "RSA_SHA3-512 ", "")).decode("utf-8")
    
        publicKey = b64decode(publicKey.replace(
            "RSA ", "")).decode("utf-8")
    
        p1, p2 = publicKey.split("@")
    
        jsonSignature = json.loads(signature)
        decrypted = rsa.decrypt((int(p1), int(p2)), jsonSignature)
    
        return computedHex == decrypted
    
    
    def main(self):
        # ulozeni promennych podle souboru
        # content, basename, extension, size, updatetime = self.openFile("soubor.txt")
        # signatureFileName = basename + ".sign"
        # zipFileName = basename + ".zip"
    
        # print("--------")
        # print("Soubor:", basename)
        # print("Typ:", extension)
        # print("Velikost:", size, "bajtů")
        # print("Upraveno:", updatetime)
        
        # ziskani a ulozeni priv a pub klice
        # privateKey, publicKey = rsa.getKeys()
        # self.saveKeys(privateKey, publicKey)
    
        a = hashlib.sha3_512()
        a = a.hexdigest()
        # a.update(content)
        
        # ziskani hashe
        # self.computedHex = a(content)
        # print("Hex souboru:", computedHex)
        # print("--------")
    
        # ziskani a ulozeni podpisu .sign soubor
        signatureList = rsa.encrypt(privateKey, a)
        jsonSignature = json.dumps(signatureList)
        signature = self.ghstrc(jsonSignature)
    
        self.saveSignature(signatureFileName, signature)
    
        # zazipovani
        zipObject = zipfile.ZipFile(zipFileName, "w")
        zipObject.write(basename)
        zipObject.write(signatureFileName)
        zipObject.close()
    
        # os.remove(signatureFileName)
        
        # porovnani souboru
    
        signatureFile = self.openFile(signatureFileName, "r")
        publicKeyFile = self.openFile("key.pub", "r")
    
        isVerified = self.verifySignature(
            a, signatureFile[0], publicKeyFile[0])
        print("Je overeni ok?:", isVerified)
        
    def __init__(self):
         QMainWindow.__init__(self)
         Ui_MainWindow.__init__(self)
         self.setupUi(self)
         self.generate.clicked.connect(self.saveKeys)
         self.load.clicked.connect(self.sign)
         self.verify.clicked.connect(self.verifySignature)
         


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
