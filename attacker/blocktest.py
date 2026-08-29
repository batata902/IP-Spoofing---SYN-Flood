from scapy.all import IP, TCP, send

for _ in range(110):
        package = IP(dst='192.168.0.13') / TCP(dport=8080, flags='S')
        send(package)
