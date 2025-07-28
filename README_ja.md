# AzureUpdatePPTX

[English version here / 英語版はこちら](README.md)

## 概要

AzureUpdatePPTX は、Azure の最新情報を自動的に取得し、AI を活用した要約で多言語対応の PowerPoint プレゼンテーションを生成するツールです。

## 特徴

- Azure の最新情報を自動取得(最大90日分)
- Azure OpenAI を利用して9言語でAzureの最新情報を要約
- PowerPoint プレゼンテーションの自動生成
- ブラウザ言語検出と多言語対応
- 日本語、英語、韓国語、中国語（簡体字・繁体字）、タイ語、ベトナム語、インドネシア語、ヒンディー語のサポート
- robots.txt と sitemap.xml による SEO 最適化

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

## 対応言語

アプリケーションは自動的にブラウザ言語を検出し、以下の言語をサポートします：

- **日本語 (ja)**: 日本語 - デフォルト
- **英語 (en)**: English
- **韓国語 (ko)**: 한국어
- **中国語簡体字 (zh-cn)**: 中文(简体)
- **中国語繁体字 (zh-tw)**: 中文(繁體)
- **タイ語 (th)**: ไทย
- **ベトナム語 (vi)**: Tiếng Việt
- **インドネシア語 (id)**: Bahasa Indonesia
- **ヒンディー語 (hi)**: हिन्दी

## SEO と静的ファイル

アプリケーションには SEO 最適化機能が含まれています：

- **robots.txt**: `/robots.txt` で利用可能 - 検索エンジンクローリングを許可
- **sitemap.xml**: `/sitemap.xml` で利用可能 - 適切な優先度を持つすべての言語バリアントを含む
- **メタタグ**: SEO メタタグ、Open Graph、Twitter Card メタデータの自動追加
- **言語検出**: 英語へのフォールバックを伴うブラウザベースの言語検出

これらの静的ファイルは Docker ビルドプロセス中に自動生成され、Streamlit によって提供されます。

## テスト

すべてのテストを実行するには：
```console
python test_runner.py
```

## 貢献
貢献を歓迎します。プルリクエストを送る前に、問題を報告してください。

## ライセンス
このプロジェクトは MIT ライセンスの下でライセンスされています。