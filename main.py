import json
from random import choice
data = []

start_time = ["8:30", "9:00"]
end_time = ["12:00", "13:00", "14:30" , "15:30"]

c = 1

for i in range (2,11):
    for day in range(1,8):
        data.append(
            {
                "model": "healthcare.DoctorSchedule",
                "pk": c,
                "fields": {
                    "doctor": i,
                    "day_of_week": day,
                    "start_time": choice(start_time),
                    "end_time": choice(end_time)
                }
            },
        )
        c+=1

json_data = json.dumps(data)

with open("doctors_schedule.json", "w") as file:
    file.write(json_data)
