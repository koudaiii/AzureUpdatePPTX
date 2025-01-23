# AzureUpdatePPTX

## 概要

AzureUpdatePPTX は、Azure の最新情報を自動的に取得し、PowerPoint プレゼンテーションを生成するツールです。

## 特徴

- Azure の最新情報を自動取得
- PowerPoint プレゼンテーションの自動生成


## 事前にデプロイする Azure サービス
- Azure OpenAI
  - GPT-4o のモデルデプロイメント

## 使い方

1. `git clone https://github.com/koudaiii/AzureUpdatePPTX.git`
2. `cd AzureUpdatePPTX`
3. .env.template を .env としてコピーします。Azure OpenAI の API Key, API Endpoint の接続文字列を設定します。
   ```sh
   cp .env.sample .env
   ```
4. セットアップします。
   ```console
   $ script/bootstrap
   ```
6. サーバーを起動します。
   ```sh
   script/server
   ```

ブラウザで `http://localhost:8000` にアクセスします

## Docker での実行

1. docker build
   ```sh
   script/docker-bootstrap
   ```
2. Docker コンテナを起動します
   ```sh
   script/docker-server
   ```

ブラウザで `http://localhost:8000` にアクセスします

## 貢献
貢献を歓迎します。プルリクエストを送る前に、問題を報告してください。

## ライセンス
このプロジェクトは MIT ライセンスの下でライセンスされています。
