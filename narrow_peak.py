import gzip
import os
from typing import Any, Iterable, Tuple, List, Dict

import numpy as np


class BasicBED(object):
    def __init__(self, input_file, bin_size=50000):
        self.input_file = input_file
        self.chroms = dict()
        self.bin_size = bin_size

    def intersect(self, chrom, start, end) -> list:
        start, end = int(start), int(end)
        res = set()
        if chrom in self.chroms:
            for idx in range(start // self.bin_size, (end - 1) // self.bin_size + 1):
                if idx not in self.chroms[chrom]:
                    continue
                try:
                    for i_start, i_end, attr in self.chroms[chrom][idx]:
                        if i_start >= end or i_end <= start:
                            continue
                        res.add((i_start, i_end, attr))
                except:
                    print(self.chroms[chrom][idx])
                    exit(1)
        res = sorted(list(res), key=lambda l: (l[0], l[1]))
        return res

    def sort(self, merge=False):
        for chrom in self.chroms:
            for idx in self.chroms[chrom]:
                self.chroms[chrom][idx] = \
                    sorted(self.chroms[chrom][idx], key=lambda l: (l[0], l[1]))

    def add_record(self, chrom, start, end, attrs=None, cut=False):
        if chrom not in self.chroms:
            self.chroms[chrom] = dict()
        for bin_idx in range(start // self.bin_size, (end - 1) // self.bin_size + 1):
            if bin_idx not in self.chroms[chrom]:
                self.chroms[chrom][bin_idx] = list()
            if cut:
                raise NotImplementedError
            else:
                self.chroms[chrom][bin_idx].append((start, end, attrs))

    def __str__(self):
        return "BasicBED(filename:{})".format(os.path.relpath(self.input_file))


class NarrowPeak(BasicBED):
    def __init__(self, input_file):
        super(NarrowPeak, self).__init__(input_file=input_file)
        self.parse_input()
        self.sort()

    def parse_input(self):
        with gzip.open(self.input_file, 'rb') as infile:
            for l in infile:
                chrom, start, end, _, _, _, score = l.decode().strip().split('\t')[0:7]
                start, end = int(start), int(end)
                self.add_record(chrom, start, end, attrs=float(score))

    def seq_lisa(self, chrm: str, start: int, end: int, use_score=True) -> float:
        mid = (start + end) // 2
        intervals = self.intersect(chrm, mid - 100000, mid + 100000)
        return self.cal_reg_score(start, end, intervals, use_score=use_score)

    @staticmethod
    def cal_weight(d, L=1000, M=2) -> float:
        mu = np.log(2 * M - 1) / L
        w = 2 * np.exp(-mu * d) / (1 + np.exp(-mu * d))
        return w

    @staticmethod
    def cal_reg_score(start: int, end: int, intervals: list, use_score: bool) -> float:
        s = 0.0
        for left, right, score in intervals:
            for i in range(left, right):
                d = NarrowPeak.distance(start, end, i)
                w = NarrowPeak.cal_weight(d)
                if use_score:
                    s += w * float(score)
                else:
                    s += w
        return s

    @staticmethod
    def distance(start: int, end: int, pos: int) -> int:
        if start <= pos <= end:
            return 0
        return min(abs(pos - start), abs(pos - end))


def get_np(name: str, fp: Any, target: Iterable[Tuple[str, int, int]], use_score: bool) -> Dict[str, List[float]]:
    narrow_peak = NarrowPeak(fp)
    return {name: [narrow_peak.seq_lisa(*x, use_score=use_score) for x in target]}

