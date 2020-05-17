import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def truncate_data(lines):
    lines = lines[100:]
    truncated_values = []
    for value in lines:
        if value < 0.380:
            truncated_values.append(value)
    return truncated_values


def parse_log(filepath, offset=15):
    with open(filepath) as f:
        lines = [line.strip()
                 for line in f if "time_taken" in line and "BenchmarkMetric" in line and "epoch" not in line]
        print(lines[5])
        x = lines[5].index("time_taken") + offset
        y = x+6
        # for line in lines:
        # print(line)
        # print(x,y)
        # print("float is:",float(line[x:y]))
        # print("-----------------------")
        lines = [float(line[x:y]) for line in lines]

        # truncate data
        lines = truncate_data(lines)
        return lines


def ecdf(logs, outfiles):
    for i in range(len(logs)):
        raw_data = np.array(logs[i])
        # create a sorted series of unique data
        cdfx = np.sort(logs[i])
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
        new_df.to_csv(outfiles[i], sep=" ", index=False)
    


def plot_cdf(logs, titles):
    n_bins = 500

    fig, ax = plt.subplots(figsize=(8, 4))

    for i in range(len(logs)):
        # plot the cumulative histogram
        ax.hist(logs[i], n_bins, density=True, histtype='step',
                cumulative=True, label=titles[i])

    # tidy up the figure
    ax.grid(True)
    ax.legend(loc='right')
    ax.set_title('ResNet50 CDF of Iteration times - 4 VMs, 16 GPUs')
    ax.set_xlabel('Time (seconds)')
    ax.set_ylabel('Likelihood')
    # plt.xlim(0,0.3)
    plt.show()


def main():
    filepath1 = './logs/16-gpu-ideal.log'
    filepath2 = './logs/16-gpu-straggler.log'
    filepath3 = './logs/16-gpu-skip.log'
    filepath4 = './logs/16-gpu-active.log'

    # filepath4 = './logs/ayushs-kf-8-gpu-baseline-imagenet-bs-128.log'
    # filepath5 = './logs/ayushs-kf-8-gpu-baseline-imagenet-bs-512.log'
    # filepath6 = './logs/ayushs-kf-8-gpu-baseline-synth-bs-1024.log'
    # filepath7 = './logs/ayushs-kf-8-gpu-skip-strategy-imagenet-bs-128.log'
    # filepath8 = './logs/ayushs-kf-8-gpu-skip-strategy-imagenet-bs-512.log'

    log1 = parse_log(filepath1)
    log2 = parse_log(filepath2)
    log3 = parse_log(filepath3)
    log4 = parse_log(filepath4)

    # log4 = parse_log(filepath4, 128)
    # log5 = parse_log(filepath5, 512)
    # log6 = parse_log(filepath6, 1025)
    # log7 = parse_log(filepath7, 128, 9)
    # log8 = parse_log(filepath8, 512)

    # print("number of entries: ", len(log1))
    logs = [log1, log2, log3, log4]
    outfiles = ['16-ideal-cdf.dat', '16-straggler-cdf.dat', '16-skip-cdf.dat', '16-active-cdf.dat']
    ecdf(logs, outfiles)
    # plot_cdf(logs, outfiles)

    # fig = plt.figure(figsize=(10,8))
    # axes= fig.add_axes([0.1,0.1,0.8,0.8])

    # x = np.arange(len(log3))
    # y = log3
    # axes.plot(x,y, marker='*', markersize=5, label='Iteration Times, fixed global batch size = 1024 (2^10)')
    # plt.show()


if __name__ == "__main__":
    main()
