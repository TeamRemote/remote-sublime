import socket 
import diff_match_patch
import timeit 
import sys

host = '' 
port = 50000 
backlog = 5 
size = 1024 
s = None 

def read_file_to_string(filename):
    data = ''
    with open (filename, "r") as myfile:
        data=myfile.read()
    return data

server = read_file_to_string("server.txt")
dmp = diff_match_patch.diff_match_patch()

try: 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.bind((host,port)) 
    s.listen(backlog) 
except socket.error, (value,message): 
    if s: 
        s.close() 
    print "Could not open socket: " + message 
    sys.exit(1) 
while 1: 
    client, address = s.accept() 
    data = client.recv(size) 
    if data:
        print data
        patch = dmp.patch_fromText(data) 
        text2, results = dmp.patch_apply(patch, server)
        print results
        print text2
    client.close()


# class Server:
#     gate = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     host = socket.gethostname()
#     port = 0
#     file = ''
#     size = 4096

#     def __init__(self, port):
#         self.port = port
#         self.gate.bind((self.host, self.port))  
#         self.listen()

#     def listen(self):
#         self.gate.listen(10)
#         while True:
#             add = self.gate.accept()
#             self.reciveFileName()
#             self.reciveFile()


#     def reciveFileName(self):
#         while True:
#             data = self.gate.recv(size)
#             self.file = data

#     def reciveFile(self):
#         createFile = open("new_"+self.file, "wb")
#         while True:
#             data = self.gate.recv(size)
#             createFile.write(data)
#         createFile.close()
