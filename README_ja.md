# AzureUpdatePPTX

## 概要

AzureUpdatePPTX は、Azure の最新情報を自動的に取得し、PowerPoint プレゼンテーションを生成するツールです。

## 特徴

- Azure の最新情報を自動取得(最大90日分)
- Azure OpenAI を利用して Azure の最新情報を三行に要約ならびにリンクを取得
- PowerPoint プレゼンテーションの自動生成

## 事前にデプロイする Azure サービス

- Azure OpenAI(GPT-4o のモデルデプロイメント)

## Docker での実行

```console
$ docker run --rm -p 8000:8000 --env API_KEY=<fake_key> --env API_ENDPOINT=https://example.com/deployments/test/?api-version=2024-08-01-preview koudaiii/azureupdatepptx
or
$ cp .env.sample
$ docker run --rm -p 8000:8000 --env-file .env koudaiii/azureupdatepptx
```

ブラウザで `http://localhost:8000` にアクセスします

## 開発

1. `git clone https://github.com/koudaiii/AzureUpdatePPTX.git`
2. `cd AzureUpdatePPTX`
3. .env.sample を .env としてコピーします。Azure OpenAI の API Key, API Endpoint の接続文字列を設定します。
   ```console
   cp .env.sample .env
   ```
4. セットアップします。
   ```console
   $ script/bootstrap
   ```
6. サーバーを起動します。
   ```console
   script/server
   ```

ブラウザで `http://localhost:8000` にアクセスします

## 貢献
貢献を歓迎します。プルリクエストを送る前に、問題を報告してください。

## ライセンス
このプロジェクトは MIT ライセンスの下でライセンスされています。