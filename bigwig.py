import pyBigWig
from typing import Tuple, Iterable, List, Any, Dict


def get_one(bw: pyBigWig.pyBigWig, interval: Tuple[str, int, int], statistic: str, nBins: int, enlarge: int) -> float:
    start, end = interval[1] - enlarge, interval[2] + enlarge
    score = bw.stats(interval[0], start, end, type=statistic, nBins=nBins)[0]
    if score is not None:
        return score
    return float('nan')


def get_bw(name: str, fp: Any, target: Iterable[Tuple[str, int, int]],
           statistic: str, nBins: int, enlarge: int) -> Dict[str, List[float]]:
    if statistic == 'mean':
        feature = '{}_mean'.format(name)
    else:
        feature = '{}_{}_{}'.format(name, statistic, nBins)
    with pyBigWig.open(fp) as bw:
        result = [get_one(bw, x, statistic, nBins, enlarge) for x in target]
    return {feature: result}
