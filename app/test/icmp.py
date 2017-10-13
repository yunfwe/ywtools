import socket
import struct
def checksum(source_string):
    sum = 0
    countTo = (len(source_string)/2)*2
    count = 0
    while count<countTo:
        thisVal = ord(source_string[count + 1])*256 + ord(source_string[count])
        sum = sum + thisVal
        sum = sum & 0xffffffff 
        count = count + 2
    if countTo<len(source_string):
        sum = sum + ord(source_string[len(source_string) - 1])
        sum = sum & 0xffffffff 
    sum = (sum >> 16)  +  (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer
def ping(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, 1)
    packet = struct.pack(
            "!BBHHH", 8, 0, 0, 0, 0
    )
    chksum=checksum(packet)
    packet = struct.pack(
            "!BBHHH", 8, 0, chksum, 0, 0
    )
    s.sendto(packet, (ip, 1))
    s.recvfrom()
if __name__=='__main__':
    ping('192.168.41.56')