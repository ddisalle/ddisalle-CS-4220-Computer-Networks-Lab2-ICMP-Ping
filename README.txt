Lab 2 - ICMP Pinger
Dustin DiSalle
CS 4220 - 003
Computer Networks

File Structure:
- icmp_pinger.py
- README.txt
- report.pdf
  - localhost.png
  - north_america.png (Google)
  - europe.png
  - 1.1.1.1.png (Cloudflare)
  - asia.png
  - africa.png

Environment Info:
- Python 3.10+
- Tested on Windows 10/11
- Raw sockets require Administrator privileges

How to Run:
1. Open Command Prompt or PowerShell as Administrator
2. Navigate to the project folder (cd ....)
3. Run:
   python icmp_pinger.py
4. Change the ping location at the bottom of the .py code to test different locations/continents, then:
   save code
   re-run python icmp_pinger.py

Program Behavior:
- Sends ICMP Echo Request packets to the target host
- Waits up to 1 second for each reply
- Prints either a reply message or a timeout/error message
- Calculates and prints:
  - minimum RTT
  - maximum RTT
  - average RTT
  - packet loss percentage
- Parses common ICMP error responses such as:
  - Destination Network Unreachable
  - Destination Host Unreachable
  - TTL Expired in Transit

Notes:
- Some hosts may block ICMP and will not respond to ping
- In that case, the program may show timeout or unreachable messages
- Testing localhost first is recommended