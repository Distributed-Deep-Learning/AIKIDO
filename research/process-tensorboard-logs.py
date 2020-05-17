import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def parse_log(filepath, offset=15):
    df = pd.read_csv(filepath)
    wall_time = (df["Wall time"].tolist())
    wall_time_normalized = [(time - wall_time[0])/60 for time in wall_time]
    print(wall_time_normalized)
    time_values, loss_values = wall_time_normalized, df["Value"]
    data = {'Wall time': time_values, 'Loss': loss_values}
    new_df = pd.DataFrame(data)
    return new_df


def write_to_dat(df, outfile):
    df.to_csv(outfile, sep=" ", index=False)

if __name__ == "__main__":
    filepath = "logs/run-full-run-16-gpu-active_validation-tag-epoch_loss.csv"
    outfile = "logs/active-loss.dat"

    df = parse_log(filepath)
    write_to_dat(df, outfile)
