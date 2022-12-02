import dis


class ServerVerifier(type):
    """
    Метакласс, выполняющий базовую проверку класса «Сервер»:
    отсутствие вызовов connect для сокетов;
    использование сокетов для работы по TCP.
    """
    def __init__(self, clsname, bases, clsdict):
        methods = []
        attrs = []

        for item in clsdict:
            try:
                ret = dis.get_instructions(clsdict[item])
            except TypeError:
                pass
            else:
                for i in ret:
                    print(i)
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in attrs:
                            attrs.append(i.argval)
        if 'connect' in methods:
            raise TypeError('Вызов connect недопустим для серверного сокета')
        if not ('SOCK_STREAM' in attrs and 'AF_INET' in attrs):
            raise TypeError('Некорректная инициализация сокета!')

        super().__init__(clsname, bases, clsdict)


class ClientVerifier(type):
    """
    Метакласс, выполняющий базовую проверку класса «Клиент»:
    отсутствие вызовов accept и listen для сокетов;
    использование сокетов для работы по TCP;
    отсутствие создания сокетов на уровне классов.
    """
    def __init__(self, clsname, bases, clsdict):
        methods = []
        for item in clsdict:
            try:
                ret = dis.get_instructions(clsdict[item])
            except TypeError:
                pass
            else:
                for i in ret:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
        for command in ('accept', 'listen', 'socket'):
            if command in methods:
                raise TypeError('В классе обнаружено использование запрещённого метода!')
        if 'receive_message' in methods or 'send_message' in methods:
            pass
        else:
            raise TypeError('Отсутствуют вызовы функций, работающих с сокетами.')
        super().__init__(clsname, bases, clsdict)
