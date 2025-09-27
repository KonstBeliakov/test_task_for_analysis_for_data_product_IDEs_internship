import csv
from dataclasses import dataclass
import matplotlib.pyplot as plt


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

    manual_time = 0
    manual_events = 0

    for row in reader:
        ts, event, open_type, user_id = row
        new_status = Status(int(ts), event, open_type, user_id)

        if user_id in users:
            old_status = users[user_id]
            if old_status.event == 'opened' and new_status.event == 'closed'\
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

print(f'\n{avg_auto_time=}\n{avg_manual_time=}')

# plt.hist(manual_durations, bins=50, alpha=0.5, label="Manual")
# plt.hist(auto_durations, bins=50, alpha=0.5, label="Auto")
# plt.xscale('log')
# plt.legend()
# plt.show()

