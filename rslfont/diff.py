import re
from typing import Callable
from functools import lru_cache, partial
from .hs.load_diff import hs_difference
from .loc.load_diff import loc_difference
from .ori.load_diff import ori_difference
from .regexes import *

@lru_cache
def sign_data(sign: str, log: bool = False):
    if log: print(sign)
    two_handed = (re.findall(SECOND_HAND, sign) or [""])[0]
    frames = [parse_frame(f) for f in re.findall(FRAME, sign)]
    timeline = "".join(re.findall(fr"{MOV}|{CONT}", sign))
    if log: print(frames, timeline)
    hand_comps = ["hs", "ori"]
    def fill_in_comp(comp: str):
        last = None
        for f in frames:
            if comp in f: last = f[comp]
            elif last: f[comp] = last
    def fill_in(hand: str):
        for c in hand_comps:
            fill_in_comp(hand+c)
    fill_in_comp("bloc")
    fill_in_comp("hloc")
    fill_in("r")
    if "Я" in two_handed:
        for c in hand_comps:
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
    elif two_handed == "09":
        for c in hand_comps:
            for f in frames:
                if "l"+c not in f and "r"+c in f: f["l"+c] = f["r"+c][::-1]
    fill_in("l")
    # last_frame = {}
    # frames = [(last_frame := last_frame | f) for f in frames]
    return frames, timeline

def mod_difference(mod1: str, mod2: str):
    if mod1 == mod2: return 0
    if mod1 is None or mod2 is None: return 2
    return 1

def hands_difference(
        comp: str, frame1: dict[str, str], frame2: dict[str, str], 
        diff_func: Callable[[str, str], int | None], l_args: dict = {}) -> int:
    r1, r2 = frame1.get("r"+comp) or "", frame2.get("r"+comp) or ""
    l1, l2 = frame1.get("l"+comp) or "", frame2.get("l"+comp) or ""
    rh_diff, lh_diff = diff_func(r1, r2), diff_func(l1, l2, **l_args)
    same = r1 == l2[::-1] or r2 == l2[::-1]
    return rh_diff if lh_diff is None else lh_diff if rh_diff is None else min(rh_diff, lh_diff) if same else rh_diff + lh_diff

def frame_difference(frame1: dict[str, str], frame2: dict[str, str], allow_hooks: bool = False):
    hs_diff = hands_difference("hs", frame1, frame2, partial(hs_difference, allow_hooks=allow_hooks))
    mod_diff = mod_difference(frame1.get("mod"), frame2.get("mod"))
    hs_diff = min(hs_diff + mod_diff, 3)

    ori_diff = hands_difference("ori", frame1, frame2, ori_difference, l_args={"hand": "l"}) or 0

    loc1 = frame1.get("bloc", frame1.get("hloc"))
    loc2 = frame2.get("bloc", frame2.get("hloc"))
    loc_diff = 0 if loc1 == loc2 else loc_difference(loc1, loc2) + 1
    return hs_diff, ori_diff, loc_diff

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
        hs_diff, ori_diff, loc_diff = frame_difference(fr1[0], fr2[0])
        return min(hs_diff + ori_diff + loc_diff, 3)
    def lengthen_framelist(frames: list[dict], upto: int):
        new = []
        for f in frames:
            new.append(f)
            f = f.copy()
            if f.pop("mod", None): new.append(f)
        if len(new) >= upto: return new
        else: return new + new
    if len(fr1) < len(fr2): fr1 = lengthen_framelist(fr1, len(fr2))
    elif len(fr1) > len(fr2): fr2 = lengthen_framelist(fr2, len(fr1))
    def multiframe_frame_diff(f1, f2, allow_hooks):
        hs_diff, ori_diff, loc_diff = frame_difference(f1, f2, allow_hooks)
        if hs_diff == 2: hs_diff = 1
        if ori_diff == 2: ori_diff = 1
        return hs_diff + ori_diff + loc_diff
    def frame_seq_diff(fseq1: list[dict], fseq2: list[dict]):
        hooks = False
        diff = 0
        for f1, f2 in zip(fseq1, fseq2):
            diff = max(diff, multiframe_frame_diff(f1, f2, hooks))
            if f1.get("mod") or f2.get("mod"): hooks = True
            else: hooks = False
        return diff
    diff1 = frame_seq_diff(fr1, fr2)
    fr1.reverse()
    diff2 = frame_seq_diff(fr1, fr2) + 1
    return min(diff1, diff2, 3)
