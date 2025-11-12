#!/usr/bin/env python
import os, csv, random, time
from datetime import datetime, timedelta

raw_dir = "/work/data/raw"
os.makedirs(raw_dir, exist_ok=True)

def gen_row(id, t0):
    pickup = t0 + timedelta(minutes=random.randint(0, 120))
    duration = random.randint(5, 55)
    dropoff = pickup + timedelta(minutes=duration)
    km = max(0.2, random.gauss(5, 3))
    fare = max(3.0, km * (1.5 + random.random()) + random.random()*3.0)
    return {
        "ride_id": f"ride_{id}",
        "pickup_ts": pickup.strftime("%Y-%m-%d %H:%M:%S"),
        "dropoff_ts": dropoff.strftime("%Y-%m-%d %H:%M:%S"),
        "passenger_count": random.randint(1,4),
        "trip_km": round(km,2),
        "fare": round(fare,2),
        "payment_type": "CARD" if random.random()<0.7 else "CASH",
        "pickup_zone": random.choice(["Downtown","Airport","Uptown","Suburb","Midtown"]),
        "dropoff_zone": random.choice(["Downtown","Airport","Uptown","Suburb","Midtown"])
    }

t0 = datetime.now()

batches, rows = 5, 300
for b in range(1, batches+1):
    path = os.path.join(raw_dir, f"batch_{b:03d}.csv")
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["ride_id","pickup_ts","dropoff_ts","passenger_count","trip_km","fare","payment_type","pickup_zone","dropoff_zone"])
        w.writeheader()
        for i in range(rows):
            w.writerow(gen_row((b-1)*rows+i, t0))
    print("wrote", path)
    time.sleep(0.2)
print("done")
