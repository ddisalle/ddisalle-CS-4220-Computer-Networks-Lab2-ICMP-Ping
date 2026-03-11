from socket import *
import os
import struct
import time
import select

ICMP_ECHO_REQUEST = 8


def checksum(data):
    """
    Compute checksum required for ICMP packets.
    """
    if len(data) % 2 == 1:
        data += b"\x00"

    csum = 0
    for i in range(0, len(data), 2):
        word = (data[i] << 8) + data[i + 1]
        csum += word
        csum = (csum & 0xFFFF) + (csum >> 16)

    return ~csum & 0xFFFF


def receiveOnePing(mySocket, ID, sequence, timeout, destAddr):
    """
    Wait for an ICMP reply packet and compute RTT.
    """
    timeLeft = timeout

    while True:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = time.time() - startedSelect

        if whatReady[0] == []:  # Timeout
            return {
                "success": False,
                "message": "Request timed out.",
                "rtt": None
            }

        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

     
        # ------------------- FILL IN START (Lab Skeleton) ---------------

        # Extract the IP header (first 20 bytes)
        ipHeader = recPacket[:20]

        # TTL is located in byte 8 of the IP header
        ttl = ipHeader[8]

        # Extract the ICMP header (bytes 20–28)
        icmpHeader = recPacket[20:28]

        # Unpack ICMP header fields
        icmpType, code, checksum_recv, packetID, seq = struct.unpack("!BBHHH", icmpHeader)

        # Verify reply matches ping request
        if icmpType == 0 and packetID == ID and seq == sequence:

            # Extract the timestamp
            bytesInDouble = struct.calcsize("!d")
            timeSent = struct.unpack("!d", recPacket[28:28 + bytesInDouble])[0]

            # Compute round trip time in msec
            rtt = (timeReceived - timeSent) * 1000

            return {
                "success": True,
                "message": f"Reply from {addr[0]}: bytes={len(recPacket)} time={rtt:.2f}ms TTL={ttl}",
                "rtt": rtt
            }

        # -------------------- FILL IN END (Lab Skeleton) ----------------

        timeLeft -= howLongInSelect
        if timeLeft <= 0:
            return {
                "success": False,
                "message": "Request timed out.",
                "rtt": None
            }


def sendOnePing(mySocket, destAddr, ID, sequence):
    """
    Build and send one ICMP Echo Request packet.
    """

    myChecksum = 0

    # Create a dummy ICMP header with checksum = 0
    header = struct.pack("!BBHHH", ICMP_ECHO_REQUEST, 0, myChecksum, ID, sequence)

    # Data payload contains timestamp
    data = struct.pack("!d", time.time())

    # Compute checksum using header + data
    myChecksum = checksum(header + data)

    # Rebuild the header with correct checksum
    header = struct.pack("!BBHHH", ICMP_ECHO_REQUEST, 0, myChecksum, ID, sequence)

    packet = header + data

    # Send packet
    mySocket.sendto(packet, (destAddr, 1))


def doOnePing(destAddr, timeout, sequence):
    """
    Send one ping and wait for reply.
    """

    icmp = getprotobyname("icmp")

    # Raw socket required for ICMP
    mySocket = socket(AF_INET, SOCK_RAW, icmp)

    # Unique identifier for this process
    myID = os.getpid() & 0xFFFF

    sendOnePing(mySocket, destAddr, myID, sequence)

    result = receiveOnePing(mySocket, myID, sequence, timeout, destAddr)

    mySocket.close()

    return result


def ping(host, timeout=1, count=4):
    """
    Send multiple ping requests and calculate statistics.
    """

    dest = gethostbyname(host)

    print(f"Pinging {host} [{dest}] using Python:\n")

    rtts = []
    sent = count
    received = 0

    for sequence in range(1, count + 1):

        result = doOnePing(dest, timeout, sequence)

        print(result["message"])

        if result["success"]:
            received += 1
            rtts.append(result["rtt"])

        time.sleep(1)

    lost = sent - received
    lossRate = (lost / sent) * 100

    print(f"\nPing statistics for {dest}:")
    print(f"Packets: Sent = {sent}, Received = {received}, Lost = {lost} ({lossRate:.0f}% loss)")

    if rtts:
        print("\nApproximate round trip times in milli-seconds:")
        print(f"Minimum = {min(rtts):.2f}ms")
        print(f"Maximum = {max(rtts):.2f}ms")
        print(f"Average = {sum(rtts)/len(rtts):.2f}ms")

### Change the following for different ping options ###
if __name__ == "__main__":
    ping("google.com", timeout=1, count=4)              # Google (North America)
    # ping("127.0.0.1", timeout=1, count=4)             # Local Host
    # ping("bbc.co.uk", timeout=1, count=4)             # Europe
    # ping("1.1.1.1", timeout=1, count=4)               # Cloudfare
    # ping("www.tsinghua.edu.cn", timeout=1, count=4)   # Asia
    # ping("www.uct.ac.za", timeout=1, count=4)         # Africa