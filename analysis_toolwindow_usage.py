import csv
from dataclasses import dataclass
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

                #print(old_status, new_status, time)

                if old_status.open_type == 'auto':
                    auto_durations.append(time)
                elif old_status.open_type == 'manual':
                    manual_durations.append(time)

        users[user_id] = new_status

avg_auto_time = sum(auto_durations) / len(auto_durations) if auto_durations else 0
avg_manual_time = sum(manual_durations) / len(manual_durations) if manual_durations else 0

print(f'Auto openings: {len(auto_durations)}')
print(f'Manual openings: {len(manual_durations)}\n')

print(f'Median time for auto openings: {np.median(auto_durations)}')
print(f'Median time for manual openings: {np.median(manual_durations)}\n')

print(f'Average time for auto openings: {avg_auto_time}')
print(f'Average time for manual openings: {avg_manual_time}\n')

stat, p_value = mannwhitneyu(manual_durations, auto_durations, alternative='two-sided')

print(f"\nMann-Whitney U statistic: {stat}")
print(f"p-value: {p_value}")

print(p_value)
if p_value < 0.05:
    print("The differences are statistically significant (p < 0.05)")
else:
    print("There are no statistically significant differences")


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


p_value = permutation_test_median(np.array(auto_durations), np.array(manual_durations))
print("\nPermutation test p-value:", p_value)
if p_value < 0.05:
    print("The differences are statistically significant (p < 0.05)")
else:
    print("There are no statistically significant differences")


def cliffs_delta(a, b):
    gt = 0
    lt = 0
    for x in a:
        gt += np.sum(x > b)
        lt += np.sum(x < b)
    n = len(a) * len(b)
    return (gt - lt) / n

delta = cliffs_delta(np.array(manual_durations), np.array(auto_durations))
print("\nCliff's Delta:", delta)

max_value = 18_000_000
print(f'\n\nAnalysis for openings with length less than {max_value}:')

auto_durations_small = [duration for duration in auto_durations if duration <= max_value]
auto_durations_big = [duration for duration in auto_durations if duration > max_value]

manual_durations_small = [duration for duration in manual_durations if duration <= max_value]
manual_durations_big = [duration for duration in manual_durations if duration > max_value]

print(f'{len(auto_durations_small)=}')
print(f'{len(manual_durations_small)=}')

stat_small, p_value_small = mannwhitneyu(auto_durations_small, manual_durations_small, alternative='two-sided')
print(f"\nMann-Whitney p-value for small durations: {p_value_small}")

p_value = permutation_test_median(np.array(auto_durations_small), np.array(manual_durations_small))
print("\nPermutation test p-value for small durations:", p_value)
if p_value < 0.05:
    print("The differences are statistically significant (p < 0.05)")
else:
    print("There are no statistically significant differences")


# for all data:
# plt.hist(manual_durations, bins=50, density=True, alpha=0.5, label='Manual')
# plt.hist(auto_durations, bins=50, density=True, alpha=0.5, label='Auto')

# only for short duration:
plt.hist(manual_durations_small, bins=50, density=True, alpha=0.5, label='Manual')
plt.hist(auto_durations_small, bins=50, density=True, alpha=0.5, label='Auto')

plt.xlabel("Time")
plt.ylabel("Amount")
plt.title("Comparison of automatic and manual window opening times")
plt.legend()
plt.show()
