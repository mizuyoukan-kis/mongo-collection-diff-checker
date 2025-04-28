# MongoDB差分検証ツール（Docker上2台MongoDB運用前提バージョン）

## 概要
2つのMongoDBインスタンス（Docker等で既に稼働中）で、同名コレクションのデータを比較し、特定カラム（例: load_datetime）を除外して差分を検証・レポート出力します。

---

## 1. 前提
- MongoDB2台は既にDocker等で稼働・データ投入済み
- DB作成・データ投入・仮想環境構築は本ツールでは行いません
- 差分検証のみ自動化します

---

## 2. セットアップ

1. ツール一式を配置
    - `mongo_diff_checker/` ディレクトリ内に `mongo_diff_checker.py`、`.env` などを配置

2. 必要なPythonパッケージをインストール
    ```bash
    pip install -r requirements.txt
    ```
    - 仮想環境利用は任意（推奨）

3. `.env` ファイルを作成し、MongoDB接続情報・コレクション名・除外カラム等を記載
    - 例:
      ```
      MONGO1_URI=mongodb://localhost:27017
      MONGO1_DB=testdb1
      MONGO2_URI=mongodb://localhost:27018
      MONGO2_DB=testdb2
      COLLECTIONS=process_A,process_B,process_C
      EXCLUDE_COLUMNS=load_datetime,_id
      ```

---

## 3. 差分検証の実行

```bash
python mongo_diff_checker.py
```

- `.env` の設定に基づき、各コレクションごとにデータを比較
- 差分内容・サマリーレポートをファイル出力
    - `result_<コレクション名>.txt`（個別詳細）
    - `diff_summary_report.txt`（全体サマリー）
    - 差分データは `diff_*.csv`、完全一致時は `match_*.csv`

---

## 4. 注意・カスタマイズ
- 比較期間やクエリ条件は `mongo_diff_checker.py` の該当部分を編集してください
- 除外カラム・コレクション名も `.env` で柔軟に変更可能
- 実DBで運用する際は、必ずバックアップ等を取ってからご利用ください

---

## 5. 参考
- 既存のDBやデータ投入スクリプトは本ツールには含めません
- サマリーレポート（diff_summary_report.txt）の例:
  ```
  process_A: OK（完全一致, DB1=100件, DB2=100件）
  process_B: NG（差分あり, DB1=99件, DB2=100件）
  ...
  ```
