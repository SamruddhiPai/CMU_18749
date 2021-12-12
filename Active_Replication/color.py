PURPLE = '\033[95m'
CYAN = '\033[96m'
DARKCYAN = '\033[36m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
END = '\033[0m'

dict = {
    "PURPLE":'\033[95m',
    "CYAN":'\033[96m',
    "DARKCYAN":'\033[36m',
    "BLUE":'\033[94m',
    "GREEN":'\033[92m',
    "YELLOW":'\033[93m',
    "RED":'\033[91m',
    "BOLD":'\033[1m',
    "UNDERLINE":'\033[4m',
    "END":'\033[0m'
}

# print(dict["RED"] + dict["BOLD"] + "HELLO" + dict["END"])


def cprint(mystr, color=""):
    if (color in dict):
        print(dict[color] + dict["BOLD"] + mystr + dict["END"])
    else:
        print(mystr)
