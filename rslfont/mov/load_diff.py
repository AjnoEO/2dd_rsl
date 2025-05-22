import os
import re
import json
from ..regexes import ROUND_MOV, CONT

with open(os.path.join("rslfont", "mov", "planes.json"), encoding="utf8") as f:
    PLANES: dict[str, list[str]] = json.load(f)

def __get_planes_rounds(mov: str) -> tuple[set[str], set[str]]:
    result = set()
    for plane, orthos in PLANES.items():
        for orth in orthos:
            if orth in mov: break
        else: result.add(plane)
    return result, set(re.findall(ROUND_MOV, mov))

def __monodirected(mov: str, checked: str, opposite: str) -> bool:
    return checked in mov and opposite not in mov

def __opposite_dirs(mov1: str, mov2: str) -> bool:
    for orthos in PLANES.values():
        d1, d2, *both = orthos
        if "(Д" in mov1 or "(Д" in mov2:
            ambi = False
            both += [f"(Д{d1})", f"(Д{d2})"]
            for d in both:
                if d in mov1 or d in mov2: ambi = True
            if ambi: continue
        if (__monodirected(mov1, d1, d2) and __monodirected(mov2, d2, d1)
            or __monodirected(mov1, d2, d1) and __monodirected(mov2, d1, d2)):
            return True
    return False

def mov_difference(mov1: str, mov2: str):
    """
    Примерная оценка разницы между движением
    - `None`: mov1 и mov2 — None
    - `0`: отсутствует 
    - `1`: мала
    - `2`: достаточно мала
    - `3`: велика
    """
    mov1, mov2 = re.sub(CONT, "", mov1), re.sub(CONT, "", mov2)
    if not mov1 and not mov2: return 0
    if not mov1 or not mov2: return 3
    if mov1 == mov2: return 0
    (planes1, rounds1), (planes2, rounds2) = __get_planes_rounds(mov1), __get_planes_rounds(mov2)
    if not planes1 and not planes2:
        if not rounds1 and not rounds2: return 1
        if not rounds1 or not rounds2: return 2
        if "Д" in rounds1 or "Д" in rounds2: return 1
        if rounds1 == rounds2: return 1
        if rounds1 & rounds2: return 2
        return 3
    if len(planes1) + len(planes2) >= 5: return 0
    if planes1 & planes2:
        if __opposite_dirs(mov1, mov2): return 3
        return 1
    return 3

if __name__ == "__main__":
    ...
    # print(ori_difference(".Э", "-."), ori_difference(".Э", "-.", hand="l"))
