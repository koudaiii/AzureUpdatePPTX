# Azure Update Helper
このプロジェクトは、Azure Update の RSS をパースして、更新情報を JSON で取得するためのツールです。
GPT-4o による自動要約を行い、更新情報を日本語で簡潔にまとめます。

## 使用方法
1. リポジトリをクローンします。
2. 必要な依存関係をインストールします。

 ```sh
pip install -r requirements.txt
```

3. .env.template を .env にコピーして、Azure OpenAI の資格情報を入力します。
4. メインスクリプトを実行します。

```sh
python azureupdatehelper.py
```

## 貢献
貢献を歓迎します。プルリクエストを送る前に、問題を報告してください。

## ライセンス
このプロジェクトは MIT ライセンスの下でライセンスされています。