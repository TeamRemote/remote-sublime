import diff_match_patch
import timeit
import socket 
import sys

def read_file_to_string(filename):
	data = ''
	with open (filename, "r") as myfile:
		data=myfile.read()
	return data

client = read_file_to_string("client.txt")
shadow = read_file_to_string("server.txt")
server = read_file_to_string("server.txt")

#create a diff_match_patch object
dmp = diff_match_patch.diff_match_patch()

# Depending on the kind of text you work with, in term of overall length
# and complexity, you may want to extend (or here suppress) the
# time_out feature
dmp.Diff_Timeout = 0   # or some other value, default is 1.0 seconds

# All 'diff' jobs start with invoking diff_main()
diffs = dmp.diff_main(shadow, client)

#Generate patches between client and shadow
patch = dmp.patch_make(shadow, diffs)

def create_client_socket():
	host = 'localhost' 
	port = 50000 
	size = 4096 
	s = None 
	try: 
	    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	    s.connect((host,port)) 
	except socket.error, (value,message): 
	    if s: 
	        s.close() 
	    print "Could not open socket: " + message 
	    sys.exit(1) 
	return s


socket = create_client_socket()
socket.send(dmp.patch_toText(patch))
socket.recv(4096)

#text2, results = dmp.patch_apply(patch, server)

	
	# s.send('Hello, world') 
	# data = s.recv(size) 
	# s.close() 
	# print 'Received:', data

    	


