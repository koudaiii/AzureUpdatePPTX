import sys
import os
import requests
import urllib
import logging
import re
import feedparser
import urllib.parse as urlparse
from datetime import datetime, timedelta
from openai import AzureOpenAI

# ログレベルの設定
logging.basicConfig(level=logging.CRITICAL)

# 何日前のアップデートまでスライドに含めるかの設定
DAYS = 7

# Azure Update の RSS フィードの URL
RSS_URL = "https://www.microsoft.com/releasecommunications/api/v2/azure/rss"

# システムプロンプトの設定
systemprompt = ("渡されたデータに含まれている Azure のアップデート情報を日本語で 3 行程度で要約してください。" +
                "リンク用のURLやマークダウンは含まず、プレーンテキストで出力してください。")


# 日付フォーマット 'Thu, 23 Jan 2025 21:30:21 Z' は RSS フィードの published で使用
DATE_FORMAT = '%a, %d %b %Y %H:%M:%S %z'


# 環境変数のチェック
def environment_check():
    if (os.getenv("API_KEY") == "" or os.getenv("API_KEY") is None or
            os.getenv("API_ENDPOINT") == "") or os.getenv("API_ENDPOINT") is None:
        logging.error('環境変数が不足しています。.env ファイルを確認してください。 (Environment variables are missing. Please check the .env file.)')
        return False
    else:
        return True


# Azure OpenAI のクライアントを生成する関数
def azure_openai_client(key, endpoint):
    parsed_url = urlparse.urlparse(endpoint)
    query_params = dict(urlparse.parse_qsl(parsed_url.query))

    api_version = query_params.get('api-version', '')

    deployment_name_match = re.search(r"deployments/([^/]+)/", parsed_url.path)
    deployment_name = deployment_name_match.group(1) if deployment_name_match else ''

    logging.debug(f"Extracted API Key: {key}")
    logging.debug(f"Extracted API Version: {api_version}")
    logging.debug(f"Extracted Deployment Name: {deployment_name}")

    return AzureOpenAI(api_key=key, api_version=api_version, azure_endpoint=endpoint)


# Azure Update の RSS フィードを読み込んでエントリーを取得
def get_rss_feed_entries():
    feed = feedparser.parse(RSS_URL)
    return feed.entries


# entries から published が指定された日数以内のエントリーの URL をリスト化
def get_update_urls(days):
    entries = get_rss_feed_entries()
    start_date = datetime.now().astimezone() - timedelta(days=days)  # 取得開始日
    urls = []
    for entry in entries:
        # DATE_FORMAT から datetime に変換
        published_at = datetime.strptime(entry.published, DATE_FORMAT).astimezone()
        if published_at is None:
            continue
        if (published_at > start_date):
            urls.append(entry.link)
    return urls


# 引数に渡された URL から、Azure Update の記事 ID を取得して Azure Update API に HTTP Get を行い、その記事を要約する
def read_and_summary(client, url):
    # url からクエリ文字列を取得してリスト化する
    query = urllib.parse.urlparse(url).query
    query_list = dict(urllib.parse.parse_qsl(query))
    logging.debug(query_list)

    # query_list の中で id がキーの値を取得する
    docid = query_list['id']

    # url からクエリ文字列以外を取得する
    base_url = "https://www.microsoft.com/releasecommunications/api/v2/azure/"
    target_url = base_url + docid
    logging.debug(target_url)

    # リクエストヘッダーをブラウザーからのアクセスとして偽装しないと Azure Update API が正しい応答を返さない
    headers = {
        "User-Agent": "Safari/605.1.15"
    }

    # URL からデータをダウンロード
    response = requests.get(target_url, headers=headers)
    logging.debug(response.text)

    # response.text をパースして、title と description と publishedDate を取得
    title = response.json()['title']
    description = response.json()['description']
    publishedDate = response.json()['created']
    updatedDate = response.json()['modified']
    products = response.json()['products']

    # description から HTML タグを削除
    description = re.sub(r'<[^>]*?>', '', description)

    logging.debug(title)
    logging.debug(description)

    # ダウンロードしたデータを Azure OpenAI で要約
    summary_list = client.chat.completions.create(
        model=os.getenv("DEPLOYMENT_NAME"),
        messages=[
            {"role": "system", "content": systemprompt},
            {"role": "user", "content": response.text}
        ]
    )

    summary = summary_list.choices[0].message.content

    # retval に title と description と summary を JSON 形式で格納
    retval = {
        "url": url,
        "apiUrl": target_url,
        "docId": docid,
        "title": title,
        "products": products,
        "description": description,
        "summary": summary,
        "publishedDate": publishedDate,
        "updatedDate": updatedDate
    }
    logging.debug(retval)

    return retval


def main():
    from dotenv import load_dotenv

    load_dotenv()

    # ログの設定
    logging.basicConfig(force=True, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    if len(sys.argv) > 1 and (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
        print("Usage: cp .env.template .env; python azureupdatehelper.py")
        return

    print("Checking environment variables...")
    # 環境変数が不足している場合はエラーを表示して終了
    if not environment_check():
        logging.error('環境変数が不足しています。.env ファイルを確認してください。')
        return
    print("Environment variables OK.")
    client = azure_openai_client(os.getenv("API_KEY"), os.getenv("API_ENDPOINT"))
    print("Client: ", client)

    entries = get_rss_feed_entries()
    print(f"RSS フィードのエントリーは {len(entries)} 件です。")

    urls = get_update_urls(DAYS)
    print(f"Azureアップデートは {len(urls)} 件です。")
    print('含まれる Azure Update の URL は以下の通りです。')
    print(urls)


if __name__ == "__main__":
    main()
