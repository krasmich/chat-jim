"""
1. Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность сетевых узлов.
Аргументом функции является список, в котором каждый сетевой узел должен быть представлен именем хоста или ip-адресом.
В функции необходимо перебирать ip-адреса и проверять их доступность с выводом соответствующего сообщения
(«Узел доступен», «Узел недоступен»). При этом ip-адрес сетевого узла должен создаваться с помощью функции ip_address().
"""


import subprocess
import ipaddress
import socket
import os


def host_ping(lst):
    result = []
    for host in lst:
        verified_ip = ip_address(host)
        if verified_ip:
            with open(os.devnull, 'w') as DNULL:
                response = subprocess.call(
                    ["ping", "-n", "2", "-w", "2", verified_ip], stdout=DNULL
                )
            if response == 0:
                result.append(('Доступен', str(host), f'[{verified_ip}]'))
                continue
        result.append(('Не доступен', str(host),
                       f'[{verified_ip if verified_ip else "Не определён"}]'))
    return result


def ip_address(host):
    try:
        if type(host) in (str, int):
            check = str(ipaddress.ip_address(host))
        else:
            return False
    except ValueError:
        try:
            check = socket.gethostbyname(host)
        except socket.gaierror:
            return False
    return check


ip_addresses = ['127.0.0.1', 'google.com', 'dfr245$%', 2130706433]

for i in host_ping(ip_addresses):
    print(f'{i[0].ljust(11)} {i[1].ljust(15)} {i[2]}')
