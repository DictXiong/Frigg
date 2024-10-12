import argparse
import cmd
import logging
from db import DBManager
from config import ConfigManager

logger = logging.getLogger('frigg')
logger.setLevel(logging.INFO)
config = ConfigManager(logger)
db = DBManager(config.get_config('db'), logger)

parser = argparse.ArgumentParser(description='Frigg CLI')
parser.add_argument('action', nargs='?', help='Action to perform', default='')
parser.add_argument('args', nargs='*', help='Arguments for the action', default=[])
args = parser.parse_args()

def set_host(args):
    if len(args) != 2:
        print('Usage: sethost <name> <uuid>')
        return
    name, uuid_str = args
    db.set_host(name, uuid_str)

def list_hosts(args):
    if len(args) != 0:
        print('Usage: listhosts')
        return
    print('Hosts:')
    for i in db.list_hosts():
        print(i)

def test_host(args):
    if len(args) != 2:
        print('Usage: testhost <name> <uuid>')
        return
    name, uuid_str = args
    if db.auth_host(name, uuid_str):
        print('Authentication Succeeded')
    else:
        print('Authentication Failed')

def set_var(args):
    if len(args) != 2:
        print('Usage: setvar <name> <value>')
        return
    name, value = args
    db.set_var(name, value)

def get_var(args):
    if len(args) != 1:
        print('Usage: getvar <name>')
        return
    name = args[0]
    value = db.get_var(name)
    if value is not None:
        print(value)
    else:
        print('Var Not Found')

def del_var(args):
    if len(args) != 1:
        print('Usage: delvar <name>')
        return
    name = args[0]
    db.del_var(name)

def list_vars(args):
    if len(args) != 0:
        print('Usage: listvars')
        return
    print('Vars:')
    for i in db.list_vars():
        print(i)

class FriggCli(cmd.Cmd):
    prompt = 'frigg> '

    def do_sethost(self, line):
        set_host(line.split())

    def do_listhosts(self, line):
        list_hosts(line.split())

    def do_testhost(self, line):
        test_host(line.split())

    def do_setvar(self, line):
        set_var(line.split())

    def do_getvar(self, line):
        get_var(line.split())

    def do_delvar(self, line):
        del_var(line.split())

    def do_listvars(self, line):
        list_vars(line.split())

    def do_exit(self, line):
        logger.info('Bye!')
        return True

    def do_EOF(self, line):
        logger.info('Bye!')
        return True

    def emptyline(self):
        pass

if __name__ == '__main__':
    if args.action == '':
        FriggCli().cmdloop()
    else:
        FriggCli().onecmd(args.action + ' ' + ' '.join(args.args))
