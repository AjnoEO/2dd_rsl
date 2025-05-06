import re

HS = r"[а-яё1-8АВГЕИКЛМНОПРСТУФЧШЫ]"
CONT = r"[*!Ц;+]"
FING = r"[%Ж\"=Э-]"
ORI = fr"(?:[.Ё]{FING}|{FING}[.Ё])"
DIR = r"[_ЬБЮ/З\\Щ]"
MOD = r"(?:\?\??)"

HANDLOC = fr"(?:9(?:{HS}{DIR}|" + r"[.Ё]{,2}" + HS + r"[.Ё]{,2})0)"
HANDLOC_W_HS = fr"(?:9(?:(?P<lhs>{HS}){DIR}|" + r"[.Ё]{,2}(?P<lhs>" + HS + r")[.Ё]{,2})0)"
BODYLOC = r"(?:\([.Ё]{,2}Й?[.Ё]{,2}\)|9[.Ё]{,2}(?:Й\.?Й?)?[.Ё]{,2}0|" + fr"Й(?:{DIR}|{FING}{DIR}|{DIR}{FING})Й)"
# LEFT_HAND = fr"(?:{HS}{ORI}?|{HANDLOC}{HS}?{ORI}?)"
LEFT_HAND = (
    fr"(?:(?:(?P<lhs>{HS})|(?P<hloc>{HANDLOC_W_HS})|"
    fr"(?P<hloc>{HANDLOC})(?P<lhs>{HS}))?(?P<lori>{ORI})??(?P<mod>{MOD})?)"
)
RIGHT_HAND = fr"(?:(?:(?P<rori>{ORI})?(?:(?P<rhs>{HS}){HANDLOC}?)|(?P<rori>{ORI}))(?P<mod>{MOD})?)"

MOV = fr"(?:{DIR}+|(?:{DIR}*ДД?{DIR}*|[/З\\Щ])(?:\({FING}\))?|\(Д{DIR}\))"

FRAME = fr"(?:{BODYLOC}|{HANDLOC}|{CONT}|{ORI}|{HS}|{MOD})+"
TIMELINE = fr"(?:{MOV}({MOV}|{CONT})*)"
SECOND_HAND = r"(?:09|\)|ЯЯ?)"

def __distinguish_groups(regexp: str):
    groups = {}
    def addgroupnum(match: re.Match):
        s = match.group()
        num = groups.get(s, 0) + 1
        groups[s] = num
        return f"{s}{num}"
    return re.sub(r"(?<=\(\?P\<)\w+(?=\>.+?\))", addgroupnum, regexp)

def __remove_groupdict_nums(groups: dict[str, str]):
    return {re.sub("\d+$", "", k): v for k, v in groups.items() if v}

def parse_frame(frame: str):
    exp = (
        fr"^(?:(?P<bloc>{BODYLOC})?(?P<cont>{CONT}*){RIGHT_HAND}|"
        fr"{LEFT_HAND}(?P<cont>{CONT}*)(?P<bloc>{BODYLOC})?|"
        fr"{LEFT_HAND}(?P<cont>{CONT}*)(?P<bloc>{BODYLOC})?(?P<cont>{CONT}*){RIGHT_HAND}|"
        fr"(?P<bloc>{BODYLOC})?(?P<cont>{CONT}*){LEFT_HAND}(?P<cont>{CONT}*){RIGHT_HAND}??)$"
    )
    exp = __distinguish_groups(exp)
    match = re.match(exp, frame)
    if not match: raise ValueError(f"Could not parse '{frame}' as a frame")
    return __remove_groupdict_nums(match.groupdict())

if __name__ == "__main__":
    print(FRAME)
    print(TIMELINE)
    print(SECOND_HAND)
