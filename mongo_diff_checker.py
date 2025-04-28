import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

MONGO1_URI = os.environ["MONGO1_URI"]
MONGO2_URI = os.environ["MONGO2_URI"]
MONGO1_DB = os.environ["MONGO1_DB"]
MONGO2_DB = os.environ["MONGO2_DB"]
COLLECTIONS = os.environ["COLLECTIONS"].split(",")
EXCLUDE_COLUMNS = os.environ["EXCLUDE_COLUMNS"].split(",")

client1 = MongoClient(MONGO1_URI)
client2 = MongoClient(MONGO2_URI)
db1 = client1[MONGO1_DB]
db2 = client2[MONGO2_DB]

summary_lines = []
for col in COLLECTIONS:
    print(f"\n========== コレクション: {col} ==========")
    q1 = {"load_datetime": {"$gte": datetime(2024, 4, 1), "$lt": datetime(2024, 4, 11)}}
    q2 = {"load_datetime": {"$gte": datetime(2024, 4, 11), "$lt": datetime(2024, 4, 21)}}
    df1 = pd.DataFrame(list(db1[col].find(q1)))
    df2 = pd.DataFrame(list(db2[col].find(q2)))
    for c in EXCLUDE_COLUMNS:
        if c in df1.columns:
            df1 = df1.drop(columns=[c])
        if c in df2.columns:
            df2 = df2.drop(columns=[c])
    df1 = df1.sort_values(list(df1.columns)).reset_index(drop=True) if not df1.empty else df1
    df2 = df2.sort_values(list(df2.columns)).reset_index(drop=True) if not df2.empty else df2
    result_lines = []
    if df1.empty and df2.empty:
        msg = f"[OK] {col}: どちらも該当データなし"
        print(msg)
        result_lines.append(msg)
        summary_lines.append(f"{col}: OK（どちらも該当データなし）")
    elif df1.empty:
        msg = f"[NG] {col}: DB1は0件、DB2は{len(df2)}件（全件DB2のみに存在）"
        print(msg)
        print(df2.head(3).to_string(index=False))
        result_lines.append(msg)
        result_lines.append(df2.head(3).to_string(index=False))
        summary_lines.append(f"{col}: NG（DB1=0件, DB2={len(df2)}件）")
        df2.to_csv(f"diff_{col}_only_in_db2.csv", index=False)
    elif df2.empty:
        msg = f"[NG] {col}: DB1は{len(df1)}件、DB2は0件（全件DB1のみに存在）"
        print(msg)
        print(df1.head(3).to_string(index=False))
        result_lines.append(msg)
        result_lines.append(df1.head(3).to_string(index=False))
        summary_lines.append(f"{col}: NG（DB1={len(df1)}件, DB2=0件）")
        df1.to_csv(f"diff_{col}_only_in_db1.csv", index=False)
    elif df1.equals(df2):
        msg = f"[OK] {col}: 完全一致（DB1:{len(df1)}件, DB2:{len(df2)}件）"
        print(msg)
        result_lines.append(msg)
        summary_lines.append(f"{col}: OK（完全一致, DB1={len(df1)}件, DB2={len(df2)}件）")
        df1.to_csv(f"match_{col}.csv", index=False)
    else:
        msg = f"[NG] {col}: 差分あり（DB1:{len(df1)}件, DB2:{len(df2)}件）"
        print(msg)
        result_lines.append(msg)
        summary_lines.append(f"{col}: NG（差分あり, DB1={len(df1)}件, DB2={len(df2)}件）")
        diff1 = df1.merge(df2, how='outer', indicator=True).query('_merge == "left_only"')
        diff2 = df2.merge(df1, how='outer', indicator=True).query('_merge == "left_only"')
        if not diff1.empty:
            print(f"  DB1のみに存在（{len(diff1)}件）: 例→\n{diff1.head(3).to_string(index=False)}")
            result_lines.append(f"  DB1のみに存在（{len(diff1)}件）: 例→\n{diff1.head(3).to_string(index=False)}")
            diff1.to_csv(f"diff_{col}_only_in_db1.csv", index=False)
        if not diff2.empty:
            print(f"  DB2のみに存在（{len(diff2)}件）: 例→\n{diff2.head(3).to_string(index=False)}")
            result_lines.append(f"  DB2のみに存在（{len(diff2)}件）: 例→\n{diff2.head(3).to_string(index=False)}")
            diff2.to_csv(f"diff_{col}_only_in_db2.csv", index=False)
        print(f"  → 差分csv出力 (diff_{col}_only_in_db1.csv, diff_{col}_only_in_db2.csv)")
        result_lines.append(f"  → 差分csv出力 (diff_{col}_only_in_db1.csv, diff_{col}_only_in_db2.csv)")
    # 証拠としてテキストファイルにも出力
    with open(f"result_{col}.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(result_lines))
# 全体サマリーレポート出力
with open("diff_summary_report.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(summary_lines))
print("\n==== 差分サマリーレポート ====\n" + "\n".join(summary_lines))
