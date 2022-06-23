import os
from argparse import ArgumentParser
from subprocess import Popen, PIPE
import json
from typing import Dict
from pathlib import Path
import pandas as pd
from bigwig import get_bw
from narrow_peak import get_np
from split_distance import get_junction
from nonb_dna import get_nonB
from concurrent.futures import ThreadPoolExecutor, as_completed


with open(Path(__file__).parent / 'config.json') as handle:
    config = json.load(handle)

bash = config['bash']
bedtools = config['bedtools']
enlarge = config['enlarge']
window = config['window']
try:
    cores = config['cores']
except KeyError:
    cores = 4


def run_bash(cmd):
    p = Popen([bash, '-c', cmd], stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    out, err = out.decode('utf8'), err.decode('utf8')
    rc = p.returncode
    if rc != 0:
        print(err)
    return rc, out, err


def read_manifest(file_type: str) -> Dict[str, str]:
    read = False
    dic = dict()
    with open('manifest.txt') as handle:
        for line in handle:
            line = line.strip()
            if line == '' or line.startswith('%'):
                continue
            if line.startswith('# start {}'.format(file_type)):
                read = True
                continue
            if line.startswith('# end {}'.format(file_type)):
                break
            if read:
                name, path = map(lambda x: x.strip(), line.strip().split('='))
                dic[name] = path
    return dic


def annotate(file: str, to_dir: str):
    Path(to_dir).mkdir(exist_ok=True)
    bw_dic = read_manifest('bigwig')
    np_dic = read_manifest('narrowpeak')
    nonb = read_manifest('nonb').get('nonb')
    junction = read_manifest('junction').get('junction')
    tmp_b, tmp_n, tmp_j = [Path(to_dir) / x.format(Path(file).stem) for x in ('{}_tmp_b', '{}_tmp_n', '{}_tmp_j')]
    rc, _, err = run_bash('{} sort -i {} > {}'.format(bedtools, file, tmp_b))
    assert rc == 0
    if nonb is not None:
        rc, _, err = run_bash('{} intersect -wo -a {} -b {} > {}'.format(bedtools, tmp_b, nonb, tmp_n))
        assert rc == 0
    if junction is not None:
        rc, _, err = run_bash('{} closest -d -a {} -b {} > {}'.format(bedtools, tmp_b, junction, tmp_j))
        assert rc == 0
    targets = pd.read_table(file, header=None).iloc[:, :3].values

    pool = list()
    executor = ThreadPoolExecutor(max_workers=cores)
    if nonb is not None:
        pool.append(executor.submit(get_nonB, tmp_n, targets))
    if junction is not None:
        pool.append(executor.submit(get_junction, tmp_j, targets))
    for k, v in bw_dic.items():
        pool.append(executor.submit(get_bw, k, v, targets, 'mean', 1, 0))
        pool.append(executor.submit(get_bw, k, v, targets, 'max', window, enlarge))
    for k, v in np_dic.items():
        pool.append(executor.submit(get_np, k, v, targets, True))
    summary = {'chr': targets[:, 0], 'start': targets[:, 1], 'end': targets[:, 2]}
    for t in as_completed(pool):
        summary.update(t.result())
    pd.DataFrame(summary).to_csv(Path(to_dir)/'annotated.csv', index=False)

    os.remove(tmp_b)
    if nonb is not None:
        os.remove(tmp_n)
    if junction is not None:
        os.remove(tmp_j)


def get_args():
    parser = ArgumentParser(description='ItvAnt (Interval Annotator) is an automatic protocol to integrate'
                                        'epigenetic information from related source.')
    parser.add_argument('input', help='the full-path name of the BED6 file to annotate.')
    parser.add_argument('--output', '-o', help='the output path, please don\'t include file name.')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    annotate(args.input, args.output)