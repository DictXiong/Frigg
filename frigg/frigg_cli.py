import argparse
import cmd
import logging
from .db import DBManager
from .config import ConfigManager

logger = logging.getLogger("frigg")
logger.setLevel(logging.INFO)

parser = argparse.ArgumentParser(description="Frigg CLI")
parser.add_argument("action", nargs="?", help="Action to perform", default="")
parser.add_argument("args", nargs="*", help="Arguments for the action", default=[])
parser.add_argument(
    "-c", "--config", default="frigg.yaml", help="Path to the configuration file"
)
args = parser.parse_args()

config = ConfigManager(args.config, logger)
db = DBManager(config.get_config("db"), logger)


class FriggCli(cmd.Cmd):
    prompt = "frigg> "

    def do_host(self, line):
        args = line.strip().split()
        if not args:
            print("Usage: host [set|list|test] ...")
            return
        match args:
            case ["set", name, uuid]:
                db.set_host(name, uuid)
            case ["list"]:
                print("Hosts:")
                for h in db.list_hosts():
                    print(h)
            case ["test", name, uuid]:
                if db.auth_host(name, uuid):
                    print("Authentication Succeeded")
                else:
                    print("Authentication Failed")
            case _:
                print("Usage: host [set <name> <uuid> | list | test <name> <uuid>]")

    def do_var(self, line):
        args = line.strip().split()
        if not args:
            print("Usage: var [set|get|del|list] ...")
            return
        match args:
            case ["set", name, value]:
                db.set_var(name, value)
            case ["get", name]:
                value = db.get_var(name)
                print(value if value is not None else "Var Not Found")
            case ["del", name]:
                db.del_var(name)
            case ["list"]:
                print("Vars:")
                for v in db.list_vars():
                    print(v)
            case _:
                print("Usage: var [set <name> <value> | get <name> | del <name> | list]")

    def do_exit(self, _):
        logger.info("Bye!")
        return True

    def do_EOF(self, _):
        logger.info("Bye!")
        return True

    def emptyline(self):
        pass


def main():
    if args.action == "":
        FriggCli().cmdloop()
    else:
        FriggCli().onecmd(args.action + " " + " ".join(args.args))


if __name__ == "__main__":
    main()
