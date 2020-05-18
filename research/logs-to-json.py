import argparse
import json
import simplejson
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


parser = argparse.ArgumentParser(
    description='convert timeline logs to JSON file for Chrome tracing')
parser.add_argument('--file',
                    type=str,
                    required=True,
                    help='path/to/log/file')
parser.add_argument('--out',
                    type=str,
                    required=True,
                    help='path/to/out/file')
parser.add_argument('--out-dat-file',
                    type=str,
                    required=True,
                    help='path/to/out/dat-file')


args = parser.parse_args()


NUM_LINES = 10**6


def parse_wait_times(num_lines=NUM_LINES):
    t1, t2 = [], []

    with open(args.file) as f:
        current_line = 0
        for line in f:
            if current_line == num_lines:
                break
            current_line += 1

            line = line.rstrip().replace(" ", "").split("|")
            cat, ph, name, ts = line
            name = cat + ": " + name
            ts = str(int(ts))
            # print(cat, ph, name, ts)
            # T1 = timestamp for KungfuAllReduce_125, reduce op end
            if cat == "ReduceOp" and ph == "END" and "KungfuAllReduce_125[0:256]" in name:
                t1.append(int(ts))
            elif cat == "BroadcastOp" and ph == "BEGIN" and "KungfuAllReduce_125[0:256]" in name:
                t2.append(int(ts))

    duration = []
    for i in range(len(t1)):
        duration.append(t2[i] - t1[i])
    return duration


def parse_tid(name):
    # parse the tid from name. Example - KungfuAllReduce_7 -> 7, KungfuAllReduce -> 0
    split_string = name.split("_")
    if len(split_string) == 1:
        return 0
    if "[" in name:
        split_string = split_string[1].split("[")
        return split_string[0]
    return int(split_string[1])


def main():
    data = {}
    data['traceEvents'] = []
    # read lines from input log file
    with open(args.file1) as f:
        for line in f:
            line = line.rstrip().replace(" ", "").split("|")
            cat, ph, name, ts = line
            name = cat + ": " + name
            ts = str(int(ts))

            pid = 1
            tid = parse_tid(name)
            # convert to JSON format
            data['traceEvents'].append({
                'pid': pid,
                'tid': tid,
                'ts': ts,
                'ph': ph[0],
                "name": name,
                "cat": cat
            })

    # sort by timestamp
    trace_events = data['traceEvents']
    sorted_trace_events = sorted(trace_events, key=lambda x: x['ts'])
    data['traceEvents'] = sorted_trace_events
    # write to JSON format

    with open(args.out, 'w') as outfile:
        json.dump(data, outfile, indent=4)


def truncate_data(lines):
    lines = lines[100:]
    truncated_values = []
    for value in lines:
        if value < 0.380:
            truncated_values.append(value)
    return truncated_values


def ecdf(values, out_dat_file):
    raw_data = np.array(values)
    # create a sorted series of unique data
    cdfx = np.sort(values)
    # x-data for the ECDF: evenly spaced sequence of the uniques
    x_values = np.linspace(start=min(cdfx),
                           stop=max(cdfx), num=len(cdfx))

    size_data = raw_data.size
    y_values = []
    for j in x_values:
        temp = raw_data[raw_data <= j]
        value = temp.size / size_data
        y_values.append(value)

    data = {'X': x_values, 'Y': y_values}
    new_df = pd.DataFrame(data)
    new_df.to_csv(out_dat_file, sep=" ", index=False)


def plot_cdf(values, title):
    n_bins = 500

    fig, ax = plt.subplots(figsize=(8, 4))

    # plot the cumulative histogram
    ax.hist(values, n_bins, density=True, histtype='step',
            cumulative=True, label=title)

    # tidy up the figure
    ax.grid(True)
    ax.legend(loc='right')
    ax.set_title('CDF of gradient wait times')
    ax.set_xlabel('Time (ms)')
    ax.set_ylabel('Likelihood')
    plt.show()


def plot():
    values = parse_wait_times()
    outfiles = ['16-ideal-cdf.dat', '16-straggler-cdf.dat',
                '16-skip-cdf.dat', '16-active-cdf.dat']

    plot_cdf(values, "title")
    # ecdf(logs, outfiles)


def test_parse_tid():
    print(parse_tid("part::KungfuAllReduce_6[0:1280]"))
    print(parse_tid("part::KungfuAllReduce[0:288]"))
    print(parse_tid("part::KungfuAllReduce_4[471860:707790]"))
    print(parse_tid("KungfuAllReduce_212"))
    print(parse_tid("part::KungfuAllReduce_147[0:1024]"))


if __name__ == "__main__":
    durations = parse_wait_times()
    # print(durations)
    # main()
    # plot()
    ecdf(durations, args.out_dat_file)
