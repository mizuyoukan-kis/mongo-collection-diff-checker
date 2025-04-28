# MongoDB Diff Checker

## 概要
2つのMongoDBインスタンスの同名コレクションのデータを比較し、特定カラム（例: load_datetime）を除外して差分を検証します。

## セットアップ
```bash
cd mongo_diff_checker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
docker-compose up -d
```

## ダミーデータ投入
```bash
python init_dummy_data.py
```

## 差分比較
```bash
python mongo_diff_checker.py
```

## 設定
- `.env` を `.env.example` を参考に作成し、MongoDB接続情報を記載してください。
