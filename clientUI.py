# coding=utf-8

import sys
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, \
    QLabel, QGridLayout, QLineEdit, QLabel, \
    QTextBrowser, QMessageBox
from PyQt5.QtGui import QIcon
from socket import *
from threading import Thread


class Example(QWidget):
    def __init__(self, sockfd, ADDR):
        self.sockfd = sockfd
        self.ADDR = ADDR
        self.sockfd.connect(self.ADDR)
        super().__init__()
        self.initUI()

    def initUI(self):
        self.btn = QPushButton("发送", self)
        self.btn.resize(60, 35)
        self.msg = QLineEdit(self)
        self.msg.resize(240, 35)
        self.ShowMsg = QTextBrowser(self)
        self.ShowMsg.resize(240, 250)
        self.lbl1 = QLabel(" 未登录", self)
        self.lbl2 = QLabel(" name", self)
        self.name = QLineEdit(self)
        self.name.resize(60, 35)
        self.btn1 = QPushButton("登录", self)
        self.btn1.resize(60, 35)
        self.btn2 = QPushButton("注销", self)
        self.btn2.resize(60, 35)

        self.ShowMsg.move(5, 5)
        self.msg.move(5, 260)
        self.btn.move(250, 260)
        self.lbl1.move(250, 5)
        self.lbl2.move(250, 35)
        self.name.move(250, 55)
        self.btn1.move(250, 100)
        self.btn2.move(250, 150)

        self.setGeometry(300, 300, 315, 300)
        self.setWindowTitle("聊天室")
        self.setWindowIcon(QIcon("zw.png"))
        self.main()

    def main(self):
        self.status = "NO"
        t = Thread(target=self.do_recv)
        t.setDaemon(True)
        t.start()
        self.btn1.clicked.connect(lambda: self.do_login(self.name.text()))
        self.btn.clicked.connect(lambda: self.do_send(self.msg.text()))
        self.btn2.clicked.connect(lambda: self.do_quit(self.name.text()))

    def do_recv(self):
        while True:
            data = self.sockfd.recv(1024)
            if data.decode() == 'OK':
                self.status = "OK"
                self.lbl1.setText("已登录")
                self.name.setEnabled(False)
                # self.name.setReadOnly(True) # 设为只读
            elif data.decode() == "EXIT":
                self.status = "NO"
            elif data.decode() == "CLOSE":
                self.sockfd.close()
                break
            else:
                self.ShowMsg.append(data.decode())

    def do_login(self, msg):
        if self.status == "OK":
            reply = QMessageBox.question(
                self, 'Message', "你以登录", QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                return
        elif not msg:
            reply = QMessageBox.question(
                self, 'Message', "name不能为空", QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                pass
        else:
            msg = "L " + msg
            self.sockfd.send(msg.encode())

    def do_send(self, msg):
        if self.status == "OK":
            msgs = "C %s %s" % (self.name.text(), msg)
            self.sockfd.send(msgs.encode())
            mymsg = "<b>我 说:</b>%s" % msg
            self.ShowMsg.append(mymsg)
            self.msg.clear()
        elif self.status == "NO":
            reply = QMessageBox.question(
                self, 'Message', "请先登录", QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self.msg.clear()

    def do_quit(self, msg):
        msg = "Q " + msg
        self.sockfd.send(msg.encode())
        self.lbl1.setText("未登录")
        self.name.setEnabled(True)

    def closeEvent(self, event):
        if self.status == "OK":
            msg = "E " + self.name.text()
            self.sockfd.send(msg.encode())
            event.accept()
        elif self.status == "NO":
            self.sockfd.send(b'N')
            event.accept()


if __name__ == "__main__":
    # ADDR = ("132.232.150.129", 8888)
    ADDR = ("127.0.0.1", 8888)
    sockfd = socket(AF_INET, SOCK_STREAM)
    app = QApplication(sys.argv)
    ex = Example(sockfd, ADDR)
    ex.show()
    sys.exit(app.exec_())
