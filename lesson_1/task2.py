"""
2. Написать функцию host_range_ping() для перебора ip-адресов из
заданного диапазона.
Меняться должен только последний октет каждого адреса. По результатам
проверки должно выводиться соответствующее сообщение.
"""

import ipaddress
from task1 import host_ping


def host_range_ping(network):
    try:
        hosts = list(map(str, ipaddress.ip_network(network).hosts()))
    except ValueError as e:
        print(e)
    else:
        count = 255
        for host in host_ping(hosts):
            if not count:
                break
            count -= 1
            print(f'{host[0].ljust(11)} {host[1].ljust(15)} {host[2]}')


host_range_ping('173.194.222.0/28')
