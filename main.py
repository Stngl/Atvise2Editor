import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QListWidgetItem
import sys
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
            #self.client.set_security(self.client.server_policy_uri(ua.MessageSecurityMode.None_), "uaclient_untrustedRootCert.der", "uaclient_privateKey.pem")
            self.client.connect()
            #print(self.client.load_client_certificate("../uaclient_untrustedRootCert.der"))
            #print(self.client.load_private_key("../uaclient_privateKey.pem"))
            #print(self.client.user_certificate);


        except:
            print("Unexpected error:", sys.exc_info())

            print("Keine Verbindung möglich")


    def disconnect(self):
        try:
            self.client.disconnect()

        except ConnectionError:
            print("Es besteht keine Verbindung")

    def browse(self,start,filtertype):
        visited = set()
        display_nodes = set(self.displays)
        stack = list(self.client.get_node(start).get_children())

        while stack:
            node_ref = stack.pop()
            node = self.client.get_node(node_ref)
            node_id = node.nodeid.to_string()

            if node_id in visited:
                continue

            visited.add(node_id)

            if node.get_type_definition() == filtertype and node_id not in display_nodes:
                self.displays.append(node_id)
                display_nodes.add(node_id)

            for child in node.get_children():
                child_node_id = self.client.get_node(child).nodeid.to_string()
                if child_node_id not in visited:
                    stack.append(child)

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
        At.browse("ns=1;s=AGENT", "VariableTypes.ATVISE.Display")
        test = At.getDisplays()
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
