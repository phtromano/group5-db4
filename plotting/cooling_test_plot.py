import matplotlib.pyplot as plt
import csv

time = []
temperature = []

with open("pid_cooling_test.csv", "r") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        time.append(int(row[0]))
        temperature.append(float(row[1]))
plt.figure(figsize=(8, 5))
plt.plot(time, temperature, marker='o')
plt.xlabel('Time')
plt.ylabel('Temperature')
plt.title('Cooling Curve')
plt.grid(True)
plt.tight_layout()
plt.show()  