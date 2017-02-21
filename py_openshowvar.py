'''
A Python port of KUKA Varproxy client (OpenShowVar).

Authors:
    - Message format analysis: Liang Tao
    - Programming: Huang Jie
'''

import struct
import random
import socket

class openshowvar(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.msg_id = random.randint(1, 100)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.ip, self.port))
        except socket.error:
            pass
        
    def test_connection(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            ret = sock.connect_ex((self.ip, self.port))
            return ret == 0
        except socket.error:
            print 'socket error'
            return False

    can_connect = property(test_connection)

    def read(self, var, debug=False):
        if not isinstance(var, str):
            raise Exception('Var name is a string')
        else:
            self.varname = var
        return self._read_var(debug)

    def write(self, var, value):
        if not (isinstance(var, str) and isinstance(value, str)):
            raise Exception('Var name and its value should be string')
        self.varname = var
        self.value = value
        return self._write_var()

    def _read_var(self, debug=False):
        req = self._pack_read_req()
        self._send_req(req)
        _value = self._read_rsp(debug)
        print 'read value -->', _value
        return _value

    def _write_var(self):
        req = self._pack_write_req()
        self._send_req(req)
        _value = self._read_rsp()
        print 'write value -->', _value
        return _value

    def _send_req(self, req):
        self.rsp = None
        self.sock.sendall(req)
        self.rsp = self.sock.recv(256)

    def _pack_read_req(self):
        var_name_len = len(self.varname)
        flag = 0
        req_len = var_name_len + 3

        return struct.pack(
            '!HHBH'+str(var_name_len)+'s',
            self.msg_id,
            req_len,
            flag,
            var_name_len,
            self.varname
            )

    def _pack_write_req(self):
        var_name_len = len(self.varname)
        flag = 1
        value_len = len(self.value)
        req_len = var_name_len + 3 + 2 + value_len

        return struct.pack(
            '!HHBH'+str(var_name_len)+'s'+'H'+str(value_len)+'s',
            self.msg_id,
            req_len,
            flag,
            var_name_len,
            self.varname,
            value_len,
            self.value
            )

    def _read_rsp(self, debug=False):
        if self.rsp is None: return None
        var_value_len = len(self.rsp) - struct.calcsize('!HHBH') - 3
        result = struct.unpack('!HHBH'+str(var_value_len)+'s'+'3s', self.rsp)
        _msg_id, body_len, flag, var_value_len, var_value, isok = result
        if debug:
            print '[DEBUG]', result
        if result[-1].endswith('\x01') and _msg_id == self.msg_id:   # todo
            self.msg_id += 1
            return var_value

def test():
    foo = openshowvar('192.168.19.246', 7000)
    if not foo.can_connect:
        print 'connection error'
        import sys
        sys.exit(-1)
    foo.write('$OV_PRO', str(random.randint(30, 50)))
    print 'start: $OV_PRO minus one, until zero'

    ov = int(current_ov)
    for i in range(ov, 0, -1):
        foo.write('$OV_PRO', str(i))

def test2():
    foo = openshowvar('192.168.19.133', 7001)
    if not foo.can_connect:
        print 'connection error'
        import sys
        sys.exit(-1)
    while True:
        varname = raw_input('\nInput var name (`q` for quit): ')
        if varname == 'q': break
        foo.read(varname, True)

if __name__ == '__main__':
    test2()

