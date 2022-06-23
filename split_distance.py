from typing import Sequence, Any, Iterable, Tuple, Dict
import pandas as pd


def get_junction(junction: Any, target: Iterable[Tuple[str, int, int]]) -> Dict[str, Sequence[int]]:
    tb = pd.read_table(junction, header=None).iloc[:, [0, 1, 2, -1]].drop_duplicates()

    def get_index(row):
        return '@'.join(str(s) for s in (row[0], row[1], row[2]))

    tb.index = tb.apply(get_index, axis=1)
    tags = [get_index(x) for x in target]
    return {'split_distance': tb.loc[tags].iloc[:, -1].values}
