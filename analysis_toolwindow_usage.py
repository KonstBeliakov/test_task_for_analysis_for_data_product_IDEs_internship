import csv
from dataclasses import dataclass
from datetime import datetime, timedelta

import matplotlib

matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu
import numpy as np


@dataclass
class Status:
    timestamp: int
    event: str
    open_type: str
    user_id: int


with (open("toolwindow_data.csv", "r", encoding="utf-8", newline="") as f):
    reader = csv.reader(f)
    header = next(reader)

    users = {}

    auto_durations = []
    manual_durations = []

    for row in reader:
        ts, event, open_type, user_id = row
        new_status = Status(int(ts), event, open_type, user_id)

        if user_id in users:
            old_status = users[user_id]
            if old_status.event == 'opened' and new_status.event == 'closed' \
                    and old_status.timestamp < new_status.timestamp:

                time = new_status.timestamp - old_status.timestamp

                if old_status.open_type == 'auto':
                    auto_durations.append(time)
                elif old_status.open_type == 'manual':
                    manual_durations.append(time)

        users[user_id] = new_status


def permutation_test_median(a, b, n=5000):
    observed = np.median(a) - np.median(b)
    combined = np.concatenate([a, b])
    count = 0
    for _ in range(n):
        np.random.shuffle(combined)
        a_perm = combined[:len(a)]
        b_perm = combined[len(a):]
        diff = np.median(a_perm) - np.median(b_perm)
        if abs(diff) >= abs(observed):
            count += 1
    return (count + 1) / (n + 1)


def cliffs_delta(a, b):
    gt = 0
    lt = 0
    for x in a:
        gt += np.sum(x > b)
        lt += np.sum(x < b)
    n = len(a) * len(b)
    return (gt - lt) / n


def readable_time(time_ms):
    seconds, ms = divmod(time_ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return f"{days}d {hours}h {minutes}m {seconds}s"


def print_analysis(auto_durations: list[int], manual_durations: list[int]):
    print('-' * 50)
    print(f'Auto openings: {len(auto_durations)}')
    print(f'Manual openings: {len(manual_durations)}')

    auto_median = np.median(auto_durations)
    manual_median = np.median(manual_durations)

    print(f'Median time for auto openings: {auto_median} ({readable_time(auto_median)})')
    print(f'Median time for manual openings: {manual_median} ({readable_time(manual_median)})\n')

    auto_average = np.average(auto_durations)
    manual_average = np.average(manual_durations)

    print(f'Average time for auto openings: {auto_average} ({readable_time(auto_average)})')
    print(f'Average time for manual openings: {manual_average} ({readable_time(manual_average)})\n')

    stat_small, p_value = mannwhitneyu(auto_durations, manual_durations, alternative='two-sided')
    print(f"\nMann-Whitney p-value: {p_value}")
    if p_value < 0.05:
        print("The differences are statistically significant (p < 0.05)")
    else:
        print("There are no statistically significant differences")

    p_value = permutation_test_median(np.array(auto_durations), np.array(manual_durations))
    print("\nMedian permutation test p-value:", p_value)
    if p_value < 0.05:
        print("The differences are statistically significant (p < 0.05)")
    else:
        print("There are no statistically significant differences")

    delta = cliffs_delta(np.array(manual_durations), np.array(auto_durations))
    print("\nCliff's Delta:", delta)

    print('-' * 50)


print('Analysis for all data:')
print_analysis(auto_durations, manual_durations)

max_value = 18_000_000  # 5 hours

auto_durations_small = [duration for duration in auto_durations if duration <= max_value]
manual_durations_small = [duration for duration in manual_durations if duration <= max_value]

print(f'\n\nAnalysis for openings with length less than {max_value}:')
print_analysis(auto_durations_small, manual_durations_small)

# for all data:
#plt.hist(manual_durations, bins=20, density=True, alpha=0.5, label='Manual')
#plt.hist(auto_durations, bins=20, density=True, alpha=0.5, label='Auto')

# only for short duration:
plt.hist(manual_durations_small, bins=20, density=True, alpha=0.5, label='Manual')
plt.hist(auto_durations_small, bins=20, density=True, alpha=0.5, label='Auto')

plt.xlabel("Time")
plt.ylabel("Amount")
plt.title("Comparison of automatic and manual window opening times")
plt.legend()
plt.show()

# boxplot for short duration
# plt.boxplot([manual_durations_small, auto_durations_small], labels=["Manual", "Auto"])
#
# plt.title("Boxplot of window open durations")
# plt.ylabel("Duration (ms)")
# plt.show()
