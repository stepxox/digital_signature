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
    
    # otevreni souboru s textem a ziskani dat (velikost, jmeno, typ, posledni uprava)
    def openFile(self, path, tp="rb"):
        file = open(path, tp)
        _, extension = os.path.splitext(path)
        self.typ_2.setText(str(extension))
        self.velikost_2.setText(str(os.path.getsize(path))+" B")
        self.soubor_2.setText(str(os.path.basename(file.name)))
        self.uprava_2.setText(str(datetime.datetime.fromtimestamp(os.path.getmtime(path))))
        self.cesta_2.setText(str(path))
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
        privKey = b64decode(privKey.replace(
            "RSA ", "")).decode("utf-8")
        
        d, n = privKey.split("@")
        signature = str(rsa.encrypt((int(d), int(n)), a))
        pathSigned, _ = QFileDialog.getSaveFileName(self,"Uloz podepsany soubor", "","Podepsany soubor (*.sign);;All Files (*)", options=options)
        sign = open(pathSigned, "w")
        sign.write("RSA_SHA3-512 ")
        sign.write(signature)
        sign.close()

        zipObject = zipfile.ZipFile("signed.zip", "w")
        zipObject.write(path,os.path.basename(path))
        zipObject.write(pathSigned,os.path.basename(pathSigned))
        zipObject.close()
        self.output.setText("Soubor byl uspesne podepsan")
        
    # overeni podpisu
    def verifySignature(self):
        
        options = QFileDialog.Options()
        
        path, _ = QFileDialog.getOpenFileName(self,"Vyber originalni soubor", "","Textovy soubor (*.txt);;All Files (*)", options=options)
        o = open(path, "r")
        a = o.read()
        o.close()
        
        a = hashlib.sha3_512()
        a = a.hexdigest()
        
        pathPub, _ = QFileDialog.getOpenFileName(self,"Vyber verejny klic", "","Verejny klic (*.pub);;All Files (*)", options=options)
        m = open(pathPub, "r")
        pathPub = m.read()
        m.close()
        
        pathSigned, _ = QFileDialog.getOpenFileName(self,"Vyber podepsany soubor", "","Podepsany soubor (*.sign);;All Files (*)", options=options)
        n = open(pathSigned, "r")
        signature = n.read()
        n.close()
        
        signature = b64decode(signature.replace(
            "RSA_SHA3-512 ", "")).decode("utf-8")

        publicKey = b64decode(pathPub.replace(
            "RSA ", "")).decode("utf-8")
    
        e, n = publicKey.split("@")
    
        jsonSignature = json.loads(signature)
        signature = str(rsa.decrypt((int(e), int(n)), jsonSignature))
        
        #isVerified = verifySignature(
        #   a, pathSigned[0], pathPub[0])
        if(a == signature):
            self.output.setText("Soubory byly uspesne porovnany, jsou stejne")
        else:
            self.output.setText("Soubory byly uspesne porovnany, nerovnaji se")
    
        
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
