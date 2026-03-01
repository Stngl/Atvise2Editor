import os
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QListWidgetItem
sys.path.insert(0, "..")
import xml.etree.ElementTree as ET
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.styles import get_style_by_name
from pygments.formatters import HtmlFormatter
import subprocess
from xml.dom import minidom
from opcua.crypto import uacrypto



try:
    from IPython import embed
except ImportError:
    import code

    def embed():
        vars = globals()
        vars.update(locals())
        shell = code.InteractiveConsole(vars)
        shell.interact()


from opcua import Client
from opcua import ua

from Atvise import Ui_MainWindow


def load_security_config():
    """Load OPC UA security settings from environment variables."""
    cert_path = os.getenv("ATVISE_OPCUA_CERT_PATH")
    key_path = os.getenv("ATVISE_OPCUA_KEY_PATH")
    policy = os.getenv("ATVISE_OPCUA_SECURITY_POLICY", "Basic256Sha256")
    mode = os.getenv("ATVISE_OPCUA_SECURITY_MODE", "SignAndEncrypt")

    if not cert_path and not key_path:
        return None

    if not cert_path or not key_path:
        raise ValueError("ATVISE_OPCUA_CERT_PATH and ATVISE_OPCUA_KEY_PATH must both be set")

    cert_file = os.path.abspath(cert_path)
    key_file = os.path.abspath(key_path)

    if not os.path.exists(cert_file):
        raise FileNotFoundError("Configured certificate file does not exist: {}".format(cert_file))
    if not os.path.exists(key_file):
        raise FileNotFoundError("Configured private key file does not exist: {}".format(key_file))

    return "{},{},{},{}".format(policy, mode, cert_file, key_file)


class ViewFormatter():
    def format(self,value):
            script = self.getScript(value)
            print("test")
            if script:
                HtmlFormatter(style='paraiso-dark').style
                lexer = get_lexer_by_name("javascript", stripall=True)
                formatter = HtmlFormatter(linenos=True,noclasses=True, cssclass="source")
                result = highlight(script, lexer, formatter)
                return result
            else:
                result = script;
                return result;

    def getScript(self,value):
        root = ET.fromstring(value)
        for node in root.iter('{http://www.w3.org/2000/svg}script'):
            return node.text


class OPCUAConnector():
    def __init__(self):
        self.client = ""
        self.displays = []

    def setAddress(self,adress):
        self.client = Client(adress)


    def connect(self):
        try:
            self.display = []
            security_string = load_security_config()
            if security_string:
                self.client.set_security_string(security_string)
            self.client.connect()

        except:
            print("Unexpected error:", sys.exc_info())

            print("Keine Verbindung möglich")


    def disconnect(self):
        try:
            self.client.disconnect()

        except ConnectionError:
            print("Es besteht keine Verbindung")

    def browse(self,start,filtertype,results=None):
        if results is None:
            results = []

        root = self.client.get_node(start).get_children()
        if len(root) > 0:
            for idx in root:

                if (self.client.get_node(idx).get_type_definition() == filtertype):
                    results.append(self.client.get_node(idx).nodeid.to_string())
                self.browse(idx,filtertype,results)

        self.displays = results
        return list(results)

    def getDisplays(self):
        return self.displays

    def getValue(self,item):
        value = self.client.get_node(item).get_value().Value
        return value;


    def writeValue(self,item,value):
        th = self.client.get_node(item)
        print(value);
        root = ET.fromstring(self.getValue(item))
        for node in root.iter('{http://www.w3.org/2000/svg}script'):
            node.text = '<![CDATA[' + value + ']]>';
            print(node.text);

        #  node.text = '<![CDATA['.encode() + value + ']]>';
        ET.register_namespace("", "http://www.w3.org/2000/svg")
        ET.register_namespace("atv","http://webmi.atvise.com/2007/svgext")
        ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
        root_string = ET.tostring(root,encoding="UTF-8",method="html")

        print(root_string)
        test=  minidom.parseString(ET.tostring(root,encoding="UTF-8")).toprettyxml()

        try:
            print(th.get_type_definition())
            tet = th.get_attribute(13)
            #th.set_writable(True)
            val = str(test).replace("&lt;", "<")
            val2 = val.replace("&gt;", ">")
            val3 = val2.replace("&quot;",'"');
            length = int(len(val3)-1)
            print(length)
            tet.Value.Value.Value = val3

            print(tet.Value.Value.Value);
            th.set_value(tet)


        except:
            print("Unexpected error:", sys.exc_info())


class MyFirstGuiProgram(Ui_MainWindow):
    def __init__(self, dialog):
        Ui_MainWindow.__init__(self)
        self.setupUi(dialog)
    def addListtoView(self,list):
        for i in list:
          print(i)
          self.Nodes.addItem(QListWidgetItem(str(i)))

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    dialog = QtWidgets.QMainWindow()
    ViewFormat = ViewFormatter()
    prog = MyFirstGuiProgram(dialog)
    At = OPCUAConnector();
    test = []
    value = ""
    selectNode = ""
    prog.pushButton.setDisabled(True);

    def showValue(index):
        global value
        global selectNode
        selectNode = prog.Nodes.model().itemData(index)[0]
        value = At.getValue(prog.Nodes.model().itemData(index)[0])
        if ViewFormat.format(value):
            prog.pushButton.setEnabled(True)
            prog.Content.setHtml(ViewFormat.format(value))
        else:
            prog.pushButton.setEnabled(False)
            prog.Content.setText("Kein Scriptcode vorhanden")


    def connectatvise():
        global test
        At.setAddress(prog.URL.text())
        At.connect()
        prog.Nodes.clear()
        test = At.browse("ns=1;s=AGENT", "VariableTypes.ATVISE.Display")
        prog.addListtoView(test)
        prog.Content.setReadOnly(True)
        try:
            prog.Nodes.clicked.connect(showValue)
        except:
            print("Unexpected error:", sys.exc_info()[0])

    def openFile():
        file = open("newfile.js","w")
        file.write(ViewFormat.getScript(value))
        file.close()
        jsfile = "newfile.js"
        editorPath = r'"C:\Program Files (x86)\Microsoft VS Code\Code.exe"'
        process = subprocess.Popen("%s %s" % (editorPath,jsfile))
        dialog.showMinimized()

        stdoutdata, stderrdata = process.communicate()
        if process.returncode == 0:
            dialog.showNormal()
            print("editor closed")
            file = open("newfile.js","r")
            content = file.read()
            At.writeValue(selectNode,content)
            file.close();

    prog.ConnectButton.clicked.connect(connectatvise)
    prog.pushButton.clicked.connect(openFile)
    dialog.setWindowIcon(QtGui.QIcon('icon.png'))
    dialog.show()

    sys.exit(app.exec_())
