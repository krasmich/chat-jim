"""
3. Написать функцию host_range_ping_tab(), возможности которой основаны
на функции из примера 2.
Но в данном случае результат должен быть итоговым по всем ip-адресам,
представленным в табличном формате
(использовать модуль tabulate). Таблица должна состоять из двух колонок
и выглядеть примерно так:
Reachable
10.0.0.1
10.0.0.2
Unreachable
10.0.0.3
10.0.0.4
"""

import ipaddress
from task1 import host_ping
from tabulate import tabulate


def host_range_ping_tab(network):
    table = [('Доступные', 'Недоступные')]
    sort = [[], []]
    try:
        hosts = list(map(str, ipaddress.ip_network(network).hosts()))
    except ValueError as e:
        print(e)
    else:
        result = host_ping(hosts)
        for host in result:
            if len(host[0]) == 8:
                sort[0].append(f'{host[1].ljust(15)} {host[2]}')
            else:
                sort[1].append(f'{host[1].ljust(15)} {host[2]}')
        table.extend(list(zip(*sort)))
        if len(sort[0]) > len(sort[1]):
            for item in sort[0][len(sort[1]):]:
                table.append((item, None))
        elif len(sort[0]) < len(sort[1]):
            for item in sort[1][len(sort[0]):]:
                table.append((None, item))
        print(tabulate(table, headers='firstrow', stralign='center',
                       tablefmt='pipe'))


host_range_ping_tab('173.194.222.0/28')
