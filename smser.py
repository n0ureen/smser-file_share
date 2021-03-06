# ls -l /bin/sh
import sys
import os

from os import system

from datetime import datetime
from PySide import QtCore, QtGui
from PySide.QtCore import Qt

from smser_ui.sms_manager_ui import Ui_MainWindow
import android_lib


class SMSerMainWindow(QtGui.QMainWindow, Ui_MainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)

        self.setCentralWidget(self.tabWidget)
        self.messages.setLayout(self.VLMessages)

        self.message_timer = QtCore.QTimer()

        #Signal handler connections
        self.connect(self.message_timer, QtCore.SIGNAL("timeout()"), self.timer_event)
        self.connect(self.lstMsgs, QtCore.SIGNAL("currentRowChanged(int)"), self.show_contact_messages)
        self.connect(self.lstContacts, QtCore.SIGNAL("currentRowChanged(int)"), self.show_contact_info)
        self.connect(self.lstContacts, QtCore.SIGNAL("doubleClicked(int)"), self.show_contact_info)

        #self.connect(self.actionAdd, QtCore.SIGNAL("triggered()"), self.add_recipe)
        #self.connect(self.actionEdit, QtCore.SIGNAL("triggered()"), self.edit_recipe)
        #self.connect(self.actionDelete, QtCore.SIGNAL("triggered()"), self.delete_recipe)
        self.connect(self.pushButton_2, QtCore.SIGNAL("clicked()"), self.adbPush)
        self.connect(self.pushButton_3, QtCore.SIGNAL("clicked()"), self.start_conversation)
        self.connect(self.pushButton, QtCore.SIGNAL("clicked()"), self.push_file)
        self.connect(self.btnSendSMS, QtCore.SIGNAL("clicked()"), self.send_sms)

        self.message_timer.start(3000)
        self.tabWidget.setCurrentIndex(0)
        self.txtMsgs.setReadOnly(True)
        self.setWindowTitle("Remote SMS")
        #self.changeTitle("Message Recived")
        self.statusbar.showMessage("Loading contacts from the phone....")
        self.contacts, self.reverse_contacts = android_lib.get_contacts()
        self.statusbar.showMessage("Loaded %i contacts from the phone" % len(self.contacts))
        self.btnSendSMS.setEnabled(False)
        self.load_messages()
        self.load_contacts()

        self.current_contact = None
        self.current_contact_number = None
        self.contact_msgs = []
        self.last_msg_id = 0
        # This dictionary keeps track of all messages received from and sent to a contact. Contact's name is the key
        self.messages_log = {}

    def timer_event(self):
        self.load_messages()
        msgs = self.unread_msgs[:]
        msgs.reverse()
        for msg in msgs:
            if int(msg['_id']) > self.last_msg_id:
                #see if there are any new messages for the current contact, if yes, display those
                if self.current_contact == self.reverse_contacts[msg['address']]:
                    self.append_msg(msg, 'incoming')
                    self.contact_msgs.append(msg)

        if self.unread_msgs:
            self.last_msg_id = int(self.unread_msgs[0]['_id'])
    
    
    def load_messages(self):
        self.lstMsgs.clear()
        self.unread_msgs = android_lib.get_smses()
        #print(unread_msgs)
        for msg in self.unread_msgs:
            num = msg['address']
            if num not in self.reverse_contacts:
                self.reverse_contacts[num] = num
                self.contacts[num] = num
            contact_name = self.reverse_contacts[msg['address']]
            
            msg_content = msg['body']
            html= '<b>%s</b>' % contact_name
            self.lstMsgs.setFont(html)
            if len(msg_content) > 50:
                msg_content = msg_content[:47] + '...'
           
            self.lstMsgs.addItem(contact_name+  "\n " + msg_content)  
            self.setWindowTitle("Message Recived")
   

    """def load_messages(self):
        self.lstMsgs.clear()
        self.unread_msgs = android_lib.get_smses()
        #print(unread_msgs)
        for msg in self.unread_msgs:
            contact_name = self.reverse_contacts[msg['address']]
            msg_content = msg['body']
            if len(msg_content) > 50:
                msg_content = msg_content[:47] + '...'
            self.lstMsgs.addItem(contact_name + "\n " + msg_content)"""

    def show_contact_messages(self, current_row):
        list_item = self.lstMsgs.item(current_row)
        if list_item:
            contact_name = list_item.text()
            contact_name = contact_name.split('\n')[0]
            #print(contact_name)
            self.display_contact_messages(contact_name)

    def load_contacts(self):
        self.lstContacts.clear()
        contact_names = sorted(self.contacts.keys())
        for C in contact_names:
            self.lstContacts.addItem(C)

    def show_contact_info(self, current_row):
        list_item = self.lstContacts.item(current_row)
        if list_item:
            contact_name = list_item.text()
            numbers = self.contacts[contact_name]
            html = 'Mobile numbers for <b>%s</b><br />' % contact_name
            for num in numbers:
                html += num + '<br />\n'

            self.txtContactDetails.setHtml(html)

    def get_contact_messages(self, contact_name):
        contact_msgs = []
        contact_numbers = self.contacts[contact_name]
        for msg in self.unread_msgs:
            if msg['address'] in contact_numbers:
                contact_msgs.append(msg)

        return contact_msgs
      
    def push_file(self):
      filename = QtGui.QFileDialog.getOpenFileName(self)
      path = (filename)
      self.lineEdit.setText() 
      #return path
    
    def adbPush(self):
      
      source = self.lineEdit.text()
      destination = '/sdcard/Download/'
      
      
      system('adb push '+source+' '+destination)
     
      #fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 
               # '/')
      #f = open(fname, 'r')
      #with f:        
      #      data = f.read()
      #      self.lineEdit.setText(data)
      #      source = self.lineEdit.text()
      #      destination = '/sdcard/Download/'
      #self.connect(self.pushButton_2, QtCore.SIGNAL("clicked()"))
      
      #system('adb push '+source+' '+destination)
      
                                    #    //////////segmentation fault ////////////////////////////////////
      #source = '/home/noureen/Chapter 6.docx'
     
      
    def start_conversation(self):
      con = QtGui.QWidget()
      
      con.raise_()
      con.activateWindow()
      con.txtMsgs.setFocus(True)
      
      #self.txtMsgs.show()
      """self.ui.txtMsgs.raise_(True)
      self.ui.txtMsgs.activateWindow(True)
      self.ui.txtMsgs.setFocus()"""
      

    def append_msg(self, msg, msg_type):
        """
        msg_type can be incoming or outgoing
        msg is a dict containing timestamp and body
        """

        html = self.txtMsgs.toHtml()
        s = html[:-14]
        e = html[-14:]

        if 'timestamp' not in msg:
            msg['timestamp'] = datetime.fromtimestamp(int(msg['date'])/1e3)

        align_str = 'text-align: left;'
        if 'outgoing' == msg_type:
            align_str = "text-align: right; margin-left:auto; margin-right:0px;"
            direction = '&lt;-'
        else:
            direction = '-&gt;'

        new_html = '<div style="width: 100%%; %s"> %s <i>[%s]</i><br />%s</div><br />' \
                   % (align_str, direction, msg['timestamp'].strftime("%a %d %b, %Y %I:%M:%S %p"),
                      msg['body'].replace("\n", "<br />\n"))
        
        self.txtMsgs.setHtml(s + new_html + e)
        self.txtMsgs.moveCursor(QtGui.QTextCursor.MoveOperation.End)

    def display_contact_messages(self, contact_name):
        #{'read': '0', 'body': 'Sir mjhy question pochna ha', '_id': '19930', 'date': '1379845811886', 'address': '+923219551425'}
        self.btnSendSMS.setEnabled(True)
        self.txtWriteMsg.clear()

        self.current_contact = contact_name
        contact_msgs = self.get_contact_messages(contact_name)

        if contact_msgs:
            contact_msgs.reverse()
            self.current_contact_number = contact_msgs[0]['address']
            #

        html = 'Conversation with <b>%s</b><br />' % contact_name
        self.txtMsgs.setHtml(html)
        for msg in contact_msgs:
            #self.setWindowTitle("Message Recived")
            self.append_msg(msg, 'incoming')
            
            

        self.contact_msgs = contact_msgs

    def send_sms(self):
        msg = self.txtWriteMsg.toPlainText()
        if self.current_contact_number:
            android_lib.send_sms(self.current_contact_number, msg)
            self.setWindowTitle("Remote SMS")

        self.append_msg(dict(body=msg, timestamp=datetime.now()), 'outgoing')
        self.txtWriteMsg.clear()
        if self.contact_msgs:
            android_lib.mark_as_read(self.contact_msgs)
            

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    smser_window = SMSerMainWindow()
    smser_window.show()
    sys.exit(app.exec_())
