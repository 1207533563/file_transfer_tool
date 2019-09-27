#!/usr/bin/python3
# -*- coding: utf-8 -*- 

import socket,os,sys,hashlib,json,re
import user_reg_login

conf = json.load(open("client_conf.json",encoding = "utf-8"))  # 加载配置信息

# sock = socket.socket()  #创建套接字
# sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,True)  #端口复用
# sock.bind(("0.0.0.0",9748))  #套接字绑定地址和端口
# sock.connect((conf["ip地址"], conf["端口号"]))  #与目标服务器建立连接



#获取文件的md5值函数
def get_file_md5(file_path):
    m = hashlib.md5()

    with open(file_path, "rb") as f:
        while True:
            data = f.read(1024)
            if len(data) == 0:
                break    
            m.update(data)    
    return m.hexdigest().upper()

def get_passwd_md5(passwd):
    m = hashlib.md5()  
    m.update(passwd.encode())    
    return m.hexdigest().upper()


def user_check(uname):
    '''
    用户名校验
    函数功能：检验用户名是否存在
    返回值：用户名存在返回1，不存在返回0，用户名不合法返回2
    '''
    global sock
    sock = socket.socket()  #创建套接字
    sock.connect((conf["ip地址"], conf["端口号"]))  #与目标服务器建立连接
    if not re.match("^[a-zA-Z0-9_]{6,15}$", uname):  #检验是否合法
        return 2

    a_rsp = {"op":3,"args":{"uname":uname}}
    a_rsp = json.dumps(a_rsp).encode()
    data_len = "{:<15}".format(len(a_rsp)).encode()
    sock.send(data_len)
    sock.send(a_rsp)

    len_rsq=sock.recv(15).decode().rstrip()
    rsq_msg = sock.recv(int(len_rsq)).decode()
    rsq_msg = json.loads(rsq_msg)
    sock.close() 

    if rsq_msg["error_code"] == 0:
  
        return 0    #用户名不存在
    else:
        return 1    #用户名存在
    

def reg_check(uname,passwd,phone,email):
    '''
    函数功能：用户注册验证函数
    参数描述：
        uname 用户名
        passwd 密码
        返回值，注册成功返回0，注册失败返回1
    '''
    global sock
    sock = socket.socket()  #创建套接字
    sock.connect((conf["ip地址"], conf["端口号"]))  #与目标服务器建立连接
    passwd = get_passwd_md5(passwd)
    a_rsp = {"op":2,"args":{"uname":uname,"passwd":passwd,"phone":phone,"email":email}}
    a_rsp = json.dumps(a_rsp).encode()
    data_len = "{:<15}".format(len(a_rsp)).encode()
    sock.send(data_len)
    sock.send(a_rsp)

    len_rsq=sock.recv(15).decode().rstrip()
    rsq_msg = sock.recv(int(len_rsq)) 
    rsq_msg = json.loads(rsq_msg)
    sock.close()
    if rsq_msg["error_code"] == 0:
        return 0   #注册成功
    else:
        return 1   #注册失败s

def login_check(uname,passwd):
    '''
    函数功能：用户登录验证函数
    参数描述：
        uname 用户名
        passwd 密码
        返回值，登录成功返回0，登录失败返回1
    '''

    global sock
    sock = socket.socket()  #创建套接字
    sock.connect((conf["ip地址"], conf["端口号"]))  #与目标服务器建立连接
    passwd = get_passwd_md5(passwd)         
    a_rsp = {"op":1,"args":{"uname":uname,"passwd":passwd}}
    a_rsp = json.dumps(a_rsp).encode()
    data_len = "{:<15}".format(len(a_rsp)).encode()


    sock.send(data_len)
    sock.send(a_rsp)

    len_rsq=sock.recv(15).decode().rstrip()
    
  
    rsq_msg = sock.recv(int(len_rsq)).decode()

    rsq_msg = json.loads(rsq_msg)
    
    if rsq_msg["error_code"] == 0:
        return 0   #登录成功
    else: 
        return 1   #登录失败


def file_recv():
    while True:
        file_desc_info = sock.recv(300 + 15 + 32)   #收到的文件信息的消息，根据协议包括300字节的文件名，15字节的文件大小，128字节的md5值
        if file_desc_info.strip().decode() == ' ':   #如果收到的文件信息是空就退出
            print("*************所有文件接收完成！**************")
            break
        file_name = file_desc_info[:300].strip().decode() #获取文件名

        if len(file_desc_info[300:315].strip().decode()) == 0:
            break
        file_size = int(file_desc_info[300:315].strip().decode())  #获取文件大小

        file_md5 = file_desc_info[315:].strip().decode()   #获取文件md5值
        
        if file_size == -1:
            print("正在接收空文件夹！")
            os.makedirs(r"C:\Users\Administrator\Desktop\%s"%file_name,exist_ok=True)
            continue
        
        print("正在接收文件：",file_name)
        print("接收文件的大小",file_size)
        print("接收文件的md5值",file_md5)

        load_size = 0                              # 接收的大小
        load_process_new = 0                       # 已接收的大小新进度
        load_process_old = 0                       # 已接收的大小新进度
        dir_name = os.path.dirname(file_name)      #文件的相对路径

        if os.path.isdir(r"C:\Users\Administrator\Desktop\%s"%dir_name):  #判断文件的相对路径文件夹是否存在
            pass
        else:
            os.makedirs(r"C:\Users\Administrator\Desktop\%s"%dir_name)   #不存在就创建它

        f = open(r"C:\Users\Administrator\Desktop\%s"%file_name,"ab")   #接收文件的保存路径及名字
        while True:
        # 接收客户端发送过来的数据
            msg = sock.recv(file_size - load_size)                 #接收文件数据
            f.write(msg)                          #将接收的数据写入文件

            load_size += len(msg)                 #接收的大小更新
            if file_size == 0:
                break
            load_process_new = int(load_size * 100 / file_size)  
            if load_process_new != load_process_old:
                load_process_old = load_process_new
                print("已接收... {}% ...".format(load_process_old))
            if load_size == file_size:             #当接收的大小等于文件大小时退出
                break
        print("接收成功！")
        f.close()              #关闭文件
        
        new_file_md5 = get_file_md5(r"C:\Users\Administrator\Desktop\%s"%file_name)  #判断接收后的数据md5值是否相等
        if file_md5 == new_file_md5:
            print("文件md5完全相同！\n")
        else:
            print("这次接收有丢包！\n")
            break            
    sock.close()           #关闭连接



def reg_main():
    while True:
        user_name = input("请输入用户名（只能包含英文字母、数字或下划线，最短6位，最长15位）：")

        ret = user_check(user_name)
        if ret == 1:
            print("用户名已存在，请重新输入！")
        elif ret == 2:
            print("用户名格式错误，请重新输入！")
        else:
            break

    while True:
        while True:
            password = input("请输入密码：（只能包含英文字母、数字或下划线，最短6位，最长15位）：")

            ret = user_reg_login.check_password(password)

            if ret == 0:
                break
            else:
                print("密码格式错误，请重新输入！")

        confirm_pass = input("请再次输入密码：")

        if password == confirm_pass:
            break
        else:
            print("两次输入的密码不一致，请重新输入！")

    while True:
        phone = input("请输入手机号：")

        if user_reg_login.check_phone(phone):
            print("手机号输入错误，请重新输入！")
        else:
            break

    # verify_code = user_reg_login.send_sms_code(phone)

    # if verify_code:
    #     print("短信验证码已发送！")
    # else:
    #     print("短信验证码发送失败，请检查网络连接或联系软件开发商！")
    #     sys.exit(1)

    # while True:
    #     verify_code2 = input("请输入短信验证码：")

    #     if verify_code2 != verify_code:
    #         print("短信验证码输入错误，请重新输入！")
    #     else:
    #         break


    while True:
        email = input("请输入邮箱：")

        if user_reg_login.check_email(email):
            print("邮箱输入错误，请重新输入！")
        else:
            break

    # email_verify_code = user_reg_login.send_email_code(email)

    # if email_verify_code:
    #     print("邮箱验证码已发送！")
    # else:
    #     print("邮箱验证码发送失败，请检查网络连接或联系软件开发商！")
    #     sys.exit(1)

    # while True:
    #     email_verify_code2 = input("请输入邮箱验证码：")

    #     if email_verify_code2 != email_verify_code:
    #         print("短信验证码输入错误，请重新输入！")
    #     else:
    #         break
    # 校验邮箱的合法性
    # ...
    if reg_check(user_name,password,phone,email) == 0:
        return 0
    else:
        return 1
    



def login_main():
    '''
    函数功能：用户登录验证
    函数参数：无
    返回值：登录验证成功返回0，失败返回1
    '''
    while True:
        user_name = input("\n用户名：")
        ret = user_check(user_name)
        if ret == 0:
            print("用户名不存在，请重新输入！")
        elif ret == 2:
            print("用户名格式错误，请重新输入！")
        else:
            break
    #user_name = input("\n用户名：")    
    while True:
        password = input("\n密码：")
        ret = user_reg_login.check_password(password)
        if ret == 0:
            break
        else:
            print("密码格式错误，请重新输入！")

    if login_check(user_name,password) == 0:
        print("登录成功")
        return 0
    else:
        print("登录失败")
        return 1
    


def main():
    while True:
        print("请选择功能:")
        print("1.登录")
        print("2.注册")
        print("3.退出")
        com = input(">")
        if com == "1":
            if login_main() == 0:
                file_recv()
            else: 
                print("登录失败!")
            break

        elif com == "2":
            if reg_main() == 0 :
                continue
                
        elif com == "3":
       
            sys.exit()



if __name__ == "__main__":
    main()


