import utilities.log as log
from core import Core

log.init()

def main():
    print(Core.run("config/default.yaml"))

if __name__ == "__main__":
    main()