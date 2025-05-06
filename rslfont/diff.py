import re
from functools import lru_cache
from .hs.load_diff import hs_difference
from .loc.load_diff import loc_difference
from .regexes import *

@lru_cache
def sign_data(sign: str):
    two_handed = (re.findall(SECOND_HAND, sign) or [""])[0]
    frames = [parse_frame(f) for f in re.findall(FRAME, sign)]
    timeline = "".join(re.findall(fr"{MOV}|{CONT}", sign))
    comps = ["hs", "ori"]
    if "Я" in two_handed:
        for c in comps:
            r = {f["r"+c] for f in frames}
            if len(r) == 1:
                r = r.pop()[::-1]
                for f in frames:
                    if "l"+c not in f: f["l"+c] = r
                continue
            r1 = r.pop()
            l1 = r1[::-1]
            r2 = r.pop()
            l2 = r2[::-1]
            for f in frames:
                if "l"+c in f: continue
                if f["r"+c] == r1: f["l"+c] = l2
                else: f["l"+c] = l1
        return
    elif two_handed == "09":
        for c in comps:
            for f in frames:
                if "l"+c not in f: f["l"+c] = f["r"+c][::-1]
    last_frame = {}
    frames = [(last_frame := last_frame | f) for f in frames]
    return frames, timeline

def frame_difference(frame1: dict[str, str], frame2: dict[str, str]):
    rhs_diff = hs_difference(frame1.get("rhs"), frame2.get("rhs"))
    lhs_diff = hs_difference(frame1.get("lhs"), frame2.get("lhs"))
    hs_diff = rhs_diff if lhs_diff is None else lhs_diff if rhs_diff is None else min(rhs_diff + lhs_diff, 3)
    loc1 = frame1.get("bloc", frame1.get("hloc"))
    loc2 = frame2.get("bloc", frame2.get("hloc"))
    loc_diff = 0 if loc1 == loc2 else loc_difference(loc1, loc2) + 1
    return hs_diff, loc_diff

def sign_difference(sign1: str, sign2: str):
    """
    Отличие между жестами
    - `0`: отсутствует
    - `1`: пренебрежимо мало / похоже на совпадение
    - `2`: мало / возможное совпадение
    - `3`: велико
    """
    fr1, tl1 = sign_data(sign1)
    fr2, tl2 = sign_data(sign2)
    if len(fr1) == len(fr2) == 1:
        hs_diff, loc_diff = frame_difference(fr1[0], fr2[0])
        return min(hs_diff + loc_diff, 3)
    if len(fr1) < len(fr2): fr1 += fr1
    elif len(fr1) > len(fr2): fr2 += fr2
    diff1 = 0
    diff2 = 0
    def multiframe_frame_diff(f1, f2):
        hs_diff, loc_diff = frame_difference(f1, f2)
        if hs_diff == 2: hs_diff = 1
        return min(hs_diff + loc_diff, 3)
    for f1, f2 in zip(fr1, fr2):
        diff1 = max(diff1, multiframe_frame_diff(f1, f2))
    fr1.reverse()
    for f1, f2 in zip(fr1, fr2):
        diff2 = max(diff2, multiframe_frame_diff(f1, f2))
    return min(diff1, diff2)
