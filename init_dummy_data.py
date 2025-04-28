import os
import random
from datetime import datetime, timedelta
from pymongo import MongoClient

COLLECTIONS = ["process_A", "process_B", "process_C", "process_D", "process_E"]
EQUIPMENTS = ["Line1", "Line2", "Line3"]
PROCESSES = ["A", "B", "C", "D", "E"]

# 2つのMongoDB
MONGO1_URI = os.environ.get("MONGO1_URI", "mongodb://localhost:27017")
MONGO2_URI = os.environ.get("MONGO2_URI", "mongodb://localhost:27018")
MONGO1_DB = os.environ.get("MONGO1_DB", "testdb1")
MONGO2_DB = os.environ.get("MONGO2_DB", "testdb2")

client1 = MongoClient(MONGO1_URI)
client2 = MongoClient(MONGO2_URI)
db1 = client1[MONGO1_DB]
db2 = client2[MONGO2_DB]

start_time = datetime(2024, 4, 1, 8, 0, 0)

for i, col in enumerate(COLLECTIONS):
    records = []
    for lot in range(1, 11):
        base_time = start_time + timedelta(hours=lot + i * 10)
        doc = {
            "LotNo": f"LOT{1000+i*10+lot}",
            "生産量": random.randint(100, 500),
            "生産開始時刻": base_time,
            "生産終了時刻": base_time + timedelta(hours=2),
            "生産設備名": random.choice(EQUIPMENTS),
            "工程名": col,
            "load_datetime": base_time + timedelta(minutes=random.randint(1, 59))
        }
        records.append(doc)
    db1[col].delete_many({})
    db2[col].delete_many({})
    db1[col].insert_many(records)
    # DB2のload_datetimeだけずらす（内容は一致）
    records2 = [dict(r, load_datetime=r["load_datetime"] + timedelta(days=10)) for r in records]
    db2[col].insert_many(records2)

print("[INFO] ダミーデータ投入完了（DB1, DB2とも内容一致、load_datetimeのみ異なる）")
