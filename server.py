#!/usr/bin/env python3
# coding=utf-8

'''
name:  zhangw
email: 297960393@qq.com
date:  2018-9
class: AID
introduce: Chatroom server
env : python3.6
'''
from socket import *
import selectors


# 登录判断
def do_login(c, user, name):
    if (name in user) or name == '管理员':
        c.send("该用户已存在,请重新输入姓名".encode())
        return
    c.send(b'OK')
    # 通知其他人
    msg = "\n欢迎 %s 进入聊天室" % name
    for i in user:
        user[i].send(msg.encode())
    # 插入用户
    user[name] = c
    print(name, "以登录")


# 转发聊天消息
def do_chat(user, name, text):
    msg = "<b>%s 说:</b>%s" % (name, text)
    for i in user:
        if i != name:
            user[i].send(msg.encode())


# 退出聊天室
def do_quit(c, user, name):
    msg = '\n' + name + "退出了聊天室"
    for i in user:
        if i == name:
            user[i].send(b'EXIT')
        else:
            user[i].send(msg.encode())
    # 从字典删除用户
    del user[name]
    print(name, "已注销")


def do_close(c, user, name):
    msg = '\n' + name + "退出了聊天室"
    for i in user:
        if i == name:
            user[i].send(b'CLOSE')
        else:
            user[i].send(msg.encode())
    # 从字典删除用户
    del user[name]
    sel.unregister(c)
    c.close()
    print(name, "以注销并关闭")


def do_NOclose(c):
    c.send(b'CLOSE')
    sel.unregister(c)
    c.close()
    print("已有客户端关闭")


# 接收客户端请求
def read(c, user, mask):
    msg = c.recv(1024)
    msgList = msg.decode().split(' ')

    # 区分请求类型
    if msgList[0] == 'L':
        do_login(c, user, msgList[1])
    elif msgList[0] == 'C':
        do_chat(user, msgList[1], ' '.join(msgList[2:]))
    elif msgList[0] == 'Q':
        do_quit(c, user, msgList[1])
    elif msgList[0] == 'E':
        do_close(c, user, msgList[1])
    elif msgList[0] == 'N':
        do_NOclose(c)


def accept(s, user, mask):
    c, addr = s.accept()
    sel.register(c, selectors.EVENT_READ, read)
    print("已有客户端连接", addr)


# server address
ADDR = ('0.0.0.0', 8888)
sel = selectors.DefaultSelector()

# 创建套接字
s = socket(AF_INET, SOCK_STREAM)
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
sel.register(s, selectors.EVENT_READ, accept)
s.bind(ADDR)
s.listen(5)

# 存储结构 {'zhangsan':conn}
user = {}

print("等待客户端连接...")
while True:
    events = sel.select()
    for key, mask in events:
        callback = key.data
        callback(key.fileobj, user, mask)
