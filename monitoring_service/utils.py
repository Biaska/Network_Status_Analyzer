import re

def is_ipv4_address(ip_str):
    # Regular expression for IPv4 address pattern
    ipv4_pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'

    # Check if the string matches the IPv4 pattern
    match = re.match(ipv4_pattern, ip_str)
    if match:
        # Check if each octet is in the valid range (0-255)
        for octet in match.groups():
            if not (0 <= int(octet) <= 255):
                return False
        return True
    else:
        return False
    
def is_valid_port(port):
        try:
            port = int(port)
            if port < 0 or port > 65535:
                return False
        except ValueError:
            print("Invalid input.")
            return False
        return True