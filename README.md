# AzureUpdatePPTX

## 概要
AzureUpdatePPTX は、Azure の最新情報を自動的に取得し、PowerPoint プレゼンテーションを生成するツールです。

## 特徴
- Azure の最新情報を自動取得
- PowerPoint プレゼンテーションの自動生成

## コードの入手
以下のコマンドを使用してコードをローカルにクローンしてください。

```sh
git clone https://github.com/tokawa-ms/AzureUpdatePPTX.git
```

## 事前にデプロイする Azure サービス
- Azure OpenAI
  - GPT-4o のモデルデプロイメント
- Azure Storage
  - LRS の Standard Storage Account

## 使い方
1. リポジトリをクローンします。
2. `AzureUpdatePPTX` フォルダに移動します。
3. .env.template を .env としてコピーします。
   ```sh
   cp .env.template .env
   ```
4. .env ファイルを編集し、Azure OpenAI の API Key, API Endpoint, API Version, Model Deployment Name, Azure Storage の接続文字列を設定します。
5. .venv 仮想環境を作成し、有効化します
    ```sh
    python -m venv .venv
    .venv\Scripts\activate
    ```
6. 必要なパッケージをインストールします。
   ```sh
   pip install -r requirements.txt
   ```
7. streamlit を起動します。
   ```sh
   streamlit run main.py
   ```

## Docker での実行
1. Streamlit 単体でローカル実行できるところまで確認します
2. 以下のコマンドを実行して Docker イメージをビルドします
   ```sh
   docker build -t <タグ> .
   ```
3. 以下のコマンドを実行して Docker コンテナを起動します
   ```sh
   docker run -p 8501:80 <タグ>
   ```
4. ブラウザで `http://localhost:8501` にアクセスします

## 貢献
貢献を歓迎します。プルリクエストを送る前に、問題を報告してください。

## ライセンス
このプロジェクトは MIT ライセンスの下でライセンスされています。

## コンタクト
質問や提案がある場合は、[tokawa@microsoft.com](mailto:tokawa@microsoft.com) までご連絡ください。