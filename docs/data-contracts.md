# Data Contracts (simplified)
- Required: ride_id, pickup_ts, dropoff_ts, passenger_count, trip_km, fare
- Bounds: 0 <= trip_km <= 200; 0 <= fare <= 1000
- Types: passenger_count INT; trip_km DOUBLE; fare DOUBLE; pickup_ts/dropoff_ts TIMESTAMP
- Partitioning: Silver by pickup_date
