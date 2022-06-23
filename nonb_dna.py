from typing import Any, Dict, Iterable, Tuple


class SpecialDic:
    def __init__(self):
        self.diction = {}

    def put(self, chr: str, start: str, end: str, note: str):
        key = self.encode(chr, start, end)
        if self.diction.get(key) is None:
            self.diction.update({key: {note: 1}})
        else:
            if self.diction[key].get(note) is None:
                self.diction[key].update({note: 1})
            else:
                self.diction[key][note] += 1

    def get(self, chr: str, start: str, end: str) -> dict:
        key = self.encode(chr, start, end)
        try:
            return self.diction[key]
        except KeyError:
            return {}

    @staticmethod
    def encode(chr: str, start: str, end: str) -> str:
        return '@'.join([chr, start, end])


class LenDic:
    def __init__(self):
        self.diction = {}

    def put(self, chr: str, start: str, end: str, note: str, nstart: str, nend: str):
        nstart, nend = map(int, (nstart, nend))
        key = self.encode(chr, start, end)
        if self.diction.get(key) is None:
            self.diction.update({key: {note: LengthDocker(nstart, nend)}})
        else:
            if self.diction[key].get(note) is None:
                self.diction[key].update({note: LengthDocker(nstart, nend)})
            else:
                self.diction[key][note].add(nstart, nend)

    def get(self, chr: str, start: str, end: str) -> dict:
        key = self.encode(chr, start, end)
        try:
            return self.diction[key]
        except KeyError:
            return {}

    @staticmethod
    def encode(chr: str, start: str, end: str) -> str:
        return '@'.join([chr, start, end])


class LengthDocker:
    def __init__(self, start: int, end: int):
        self.stack1 = [start, end]

    def add(self, start: int, end: int):
        stack2 = []
        while len(self.stack1) > 0 and self.stack1[-1] >= start:
            stack2.append(self.stack1.pop())
        if len(self.stack1) % 2 == 0:
            self.stack1.append(start)
        while len(stack2) > 0 and stack2[-1] <= end:
            stack2.pop()
        if len(stack2) % 2 == 0:
            self.stack1.append(end)
        while len(stack2) > 0:
            self.stack1.append(stack2.pop())

    def get_len(self) -> int:
        cnt = 0
        num = len(self.stack1) // 2
        for i in range(num):
            cnt += self.stack1[2 * i + 1] - self.stack1[2 * i]
        return cnt

    def __str__(self):
        return str(self.stack1)


def build_ld(nonb_file: Any) -> LenDic:
    ld = LenDic()
    with open(nonb_file) as file:
        for l in file:
            ll = l.strip().split('\t')
            chr, start, end = ll[0:3]
            hybride = ll[-2]
            nstart, nend = ll[-4:-2]
            note = hybride.split('@')[1]
            ld.put(chr, start, end, note, nstart, nend)
    return ld


def get_note_list(nonb_file: Any) -> list:
    note_list = []
    with open(nonb_file) as file:
        for l in file:
            ll = l.strip().split('\t')
            hybride = ll[-2]
            note = hybride.split('@')[1]
            if note not in note_list:
                note_list.append(note)
    note_list.sort()
    return note_list


def extra_ration(ld: LenDic, ntl: list, tags: Iterable) -> Dict[str, list]:
    out = dict()
    for i in ntl:
        out[i] = list()
    for chr, start, end in tags:
        start, end = map(str, (start, end))
        dic = ld.get(chr, start, end)
        for i in ntl:
            if dic.get(i) is None:
                out[i].append(0.0)
            else:
                result = dic[i].get_len() / (int(end) - int(start))
                if result > 1:
                    out[i].append(1.0)
                else:
                    out[i].append(result)
    return out


def get_nonB(nonB: Any, target: Iterable[Tuple[str, int, int]]) -> Dict[str, list]:
    return extra_ration(build_ld(nonB), get_note_list(nonB), target)
