import argparse
import json
import simplejson


parser = argparse.ArgumentParser(
    description='convert timeline logs to JSON file for Chrome tracing')
parser.add_argument('--file1',
                    type=str,
                    required=True,
                    help='path/to/log/file')
parser.add_argument('--file2',
                    type=str,
                    required=True,
                    help='path/to/log/file')
parser.add_argument('--out',
                    type=str,
                    required=True,
                    help='path/to/out/file')

args = parser.parse_args()


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
    prev_ts, current_ts = 0, 0
    # read lines from input log file
    with open(args.file1) as f:
        for line in f:
            line = line.rstrip().replace(" ", "").split("|")
            cat, ph, name, ts = line
            name = cat + ": " + name
            ts = str(int(ts))
            prev_ts = current_ts
            current_ts = ts
            # if int(current_ts) < int(prev_ts):
            #     print("warning here----")
            #     print(cat, ph, name, ts)

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

    with open(args.file2) as f:
        for line in f:
            line = line.rstrip().replace(" ", "").split("|")
            cat, ph, name, ts = line
            name = cat + ": " + name
            ts = str(int(ts))
            prev_ts = current_ts
            current_ts = ts
            # if int(current_ts) < int(prev_ts):
            #     print("warning here----")
            #     print(cat, ph, name, ts)

            pid = 2
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


def test_parse_tid():
    print(parse_tid("part::KungfuAllReduce_6[0:1280]"))
    print(parse_tid("part::KungfuAllReduce[0:288]"))
    print(parse_tid("part::KungfuAllReduce_4[471860:707790]"))
    print(parse_tid("KungfuAllReduce_212"))
    print(parse_tid("part::KungfuAllReduce_147[0:1024]"))


if __name__ == "__main__":
    main()
    # test_parse_tid()
