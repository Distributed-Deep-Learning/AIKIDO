import numpy as np
import matplotlib.pyplot as plt



def parse_log(filepath, gs, offset=8):
    with open(filepath) as f:
        lines = [line.strip()
                 for line in f if "current_examples_per_sec" in line and "INFO" in line]
        print(lines[5])
        x = lines[5].index("value") + offset
        y = x+6
        # for line in lines: 
            # print(line)
            # print(x,y)
            # print("float is:",float(line[x:y]))
            # print("-----------------------/n")
        lines = [gs/float((line[x:y])) for line in lines]

        # truncate data
        lines = lines[40:-40]
        return lines


def plot_cdf(logs, titles):
    n_bins = 200

    fig, ax = plt.subplots(figsize=(8, 4))

    for i in range(len(logs)):
        # plot the cumulative histogram
        ax.hist(logs[i], n_bins, density=True, histtype='step',
                               cumulative=True, label=titles[i])


    # tidy up the figure
    ax.grid(True)
    ax.legend(loc='right')
    ax.set_title('CDF Iteration time')
    ax.set_xlabel('time (seconds)')
    ax.set_ylabel('Likelihood')
    plt.show()


def main():
    filepath1= './logs/luo-16-gpu-baseline.log'
    filepath2 = './logs/ayush-16-gpu-baseline.log'
    filepath3 = './logs/ayush-4-gpu-baseline.log'

    # filepath4 = './logs/ayushs-kf-8-gpu-baseline-imagenet-bs-128.log'
    # filepath5 = './logs/ayushs-kf-8-gpu-baseline-imagenet-bs-512.log'
    # filepath6 = './logs/ayushs-kf-8-gpu-baseline-synth-bs-1024.log'
    # filepath7 = './logs/ayushs-kf-8-gpu-skip-strategy-imagenet-bs-128.log'
    # filepath8 = './logs/ayushs-kf-8-gpu-skip-strategy-imagenet-bs-512.log'

    log1 = parse_log(filepath1, 1024)
    log2 = parse_log(filepath2, 1024)
    log3 = parse_log(filepath3, 256)

    # log4 = parse_log(filepath4, 128)
    # log5 = parse_log(filepath5, 512)
    # log6 = parse_log(filepath6, 1025)
    # log7 = parse_log(filepath7, 128, 9)
    # log8 = parse_log(filepath8, 512)


    # print("number of entries: ", len(log1))
    logs = [log1, log2]
    titles = ['16-gpu-baseline-Luo', '16-gpu-baseline-Ayush']

    plot_cdf(logs, titles)

    # fig = plt.figure(figsize=(10,8))
    # axes= fig.add_axes([0.1,0.1,0.8,0.8])

    # x = np.arange(len(log3))
    # y = log3
    # axes.plot(x,y, marker='*', markersize=5, label='Iteration Times, fixed global batch size = 1024 (2^10)')
    # plt.show()

if __name__ == "__main__":
    main()
