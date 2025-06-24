import matplotlib.pyplot as plt
import csv

time = []
temperature = []
pid_output = []

with open("system_info.csv", "r") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        time.append(str(row[0]))
        temperature.append(float(row[1]))
        pid_output.append(float(row[2]))

plt.figure(figsize=(10, 6))
plt.plot(time, temperature, label="Temperature (°C)")
plt.plot(time, pid_output, label="Output (u)")
plt.xlabel('Time')
plt.ylabel('Value')
plt.title('Temperature and PID Output')
plt.legend()
plt.grid(True)
plt.show()
