import argparse
import datetime
import socket
import struct
import sys

PROTOCOLS = {
    1: "ICMP",
    6: "TCP",
    17: "UDP",
}

ARP_OPCODES = {
    1: "request",
    2: "reply",
}


def format_mac_address(bytes_addr: bytes) -> str:
    return ":".join(f"{b:02x}" for b in bytes_addr)


def format_ipv4_address(bytes_addr: bytes) -> str:
    return ".".join(str(b) for b in bytes_addr)


def parse_ethernet_header(packet: bytes) -> tuple[int, str, str, bytes]:
    dest_mac, src_mac, proto = struct.unpack("!6s6sH", packet[:14])
    return proto, format_mac_address(dest_mac), format_mac_address(src_mac), packet[14:]


def parse_ipv4_header(packet: bytes) -> tuple[int, str, str, int, int, int, bytes]:
    version_header_length = packet[0]
    version = version_header_length >> 4
    ihl = (version_header_length & 0x0F) * 4
    ttl, protocol, src, dest = struct.unpack("!8xBB2x4s4s", packet[:20])
    return version, format_ipv4_address(src), format_ipv4_address(dest), ttl, protocol, ihl, packet[ihl:]


def parse_tcp_header(packet: bytes) -> tuple[int, int, int, int, int, int, bytes]:
    src_port, dest_port, sequence, acknowledgement, offset_reserved_flags = struct.unpack("!HHLLH", packet[:14])
    offset = (offset_reserved_flags >> 12) * 4
    flags = offset_reserved_flags & 0x01FF
    return src_port, dest_port, sequence, acknowledgement, flags, offset, packet[offset:]


def parse_udp_header(packet: bytes) -> tuple[int, int, int, bytes]:
    src_port, dest_port, size = struct.unpack("!HHH2x", packet[:8])
    return src_port, dest_port, size, packet[8:]


def parse_icmp_header(packet: bytes) -> tuple[int, int, bytes]:
    icmp_type, code, checksum = struct.unpack("!BBH", packet[:4])
    return icmp_type, code, packet[4:]


def parse_arp_header(packet: bytes) -> tuple[str, str, str, str, str, int]:
    hardware_type, protocol_type, hardware_size, protocol_size, opcode = struct.unpack("!HHBBH", packet[:8])
    sender_mac = format_mac_address(packet[8:14])
    sender_ip = format_ipv4_address(packet[14:18])
    target_mac = format_mac_address(packet[18:24])
    target_ip = format_ipv4_address(packet[24:28])
    return hardware_type, protocol_type, sender_mac, sender_ip, target_mac, target_ip, opcode


def print_packet_summary(timestamp: datetime.datetime, eth_proto: int, src_mac: str, dest_mac: str, info: str) -> None:
    print(f"[{timestamp:%Y-%m-%d %H:%M:%S}] {src_mac} -> {dest_mac} | Ethertype: 0x{eth_proto:04x} | {info}")


def sniff(interface: str | None, count: int, protocol_filter: str | None) -> None:
    if sys.platform != "linux":
        print("This sniffer only works on Linux with raw packet capture.")
        sys.exit(1)

    try:
        sniffer = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
    except PermissionError:
        print("ERROR: Raw socket access requires root privileges. Run with sudo.")
        sys.exit(1)
    except OSError as exc:
        print(f"ERROR: Could not open raw socket: {exc}")
        sys.exit(1)

    if interface:
        sniffer.bind((interface, 0))

    seen = 0
    while count < 0 or seen < count:
        raw_data, _ = sniffer.recvfrom(65535)
        timestamp = datetime.datetime.now()
        eth_proto, src_mac, dest_mac, payload = parse_ethernet_header(raw_data)

        if eth_proto == 0x0800:  # IPv4
            version, src_ip, dest_ip, ttl, protocol, header_length, ip_payload = parse_ipv4_header(payload)
            protocol_name = PROTOCOLS.get(protocol, f"OTHER({protocol})")
            if protocol_filter and protocol_name.lower() != protocol_filter.lower() and protocol_filter.lower() != "ip":
                continue

            if protocol == 6:  # TCP
                src_port, dest_port, sequence, acknowledgement, flags, offset, tcp_payload = parse_tcp_header(ip_payload)
                flags_str = []
                if flags & 0x002: flags_str.append("SYN")
                if flags & 0x010: flags_str.append("ACK")
                if flags & 0x001: flags_str.append("FIN")
                if flags & 0x004: flags_str.append("RST")
                if flags & 0x008: flags_str.append("PSH")
                if flags & 0x020: flags_str.append("URG")
                info = f"IPv4 {protocol_name} {src_ip}:{src_port} -> {dest_ip}:{dest_port} TTL={ttl} Flags={','.join(flags_str) or 'NONE'}"

            elif protocol == 17:  # UDP
                src_port, dest_port, size, udp_payload = parse_udp_header(ip_payload)
                info = f"IPv4 {protocol_name} {src_ip}:{src_port} -> {dest_ip}:{dest_port} length={size}"

            elif protocol == 1:  # ICMP
                icmp_type, code, icmp_payload = parse_icmp_header(ip_payload)
                info = f"IPv4 {protocol_name} {src_ip} -> {dest_ip} Type={icmp_type} Code={code}"

            else:
                info = f"IPv4 {protocol_name} {src_ip} -> {dest_ip} TTL={ttl}"

            print_packet_summary(timestamp, eth_proto, src_mac, dest_mac, info)
            seen += 1

        elif eth_proto == 0x0806:  # ARP
            try:
                hardware_type, protocol_type, sender_mac, sender_ip, target_mac, target_ip, opcode = parse_arp_header(payload)
            except struct.error:
                continue
            op_text = ARP_OPCODES.get(opcode, str(opcode))
            if protocol_filter and protocol_filter.lower() not in ("arp", "all"):
                continue
            info = f"ARP {op_text} {sender_ip} ({sender_mac}) -> {target_ip} ({target_mac})"
            print_packet_summary(timestamp, eth_proto, src_mac, dest_mac, info)
            seen += 1

        else:
            if protocol_filter and protocol_filter.lower() not in ("all", "ethernet"):
                continue
            info = f"Unknown ethertype 0x{eth_proto:04x}"
            print_packet_summary(timestamp, eth_proto, src_mac, dest_mac, info)
            seen += 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Basic network sniffer for Linux.")
    parser.add_argument("-i", "--interface", help="Network interface to listen on, e.g. eth0")
    parser.add_argument("-c", "--count", type=int, default=-1, help="Number of packets to capture; default is unlimited")
    parser.add_argument(
        "-p",
        "--protocol",
        choices=["all", "ip", "tcp", "udp", "icmp", "arp", "ethernet"],
        default="all",
        help="Protocol filter for displayed packets.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print("Starting Python network sniffer. Press Ctrl+C to stop.")
    if args.interface:
        print(f"Listening on interface: {args.interface}")
    print(f"Protocol filter: {args.protocol}")

    try:
        sniff(args.interface, args.count, args.protocol)
    except KeyboardInterrupt:
        print("\nCapture stopped by user.")


if __name__ == "__main__":
    main()
