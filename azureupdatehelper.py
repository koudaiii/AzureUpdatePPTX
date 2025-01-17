import os
import requests
import urllib
import logging
import re
import feedparser
from datetime import datetime, timedelta
from openai import AzureOpenAI
from time import mktime
from dotenv import load_dotenv

load_dotenv()

# ログレベルの設定
logging.basicConfig(level=logging.CRITICAL)

# 何日前のアップデートまでスライドに含めるかの設定
DAYS = 7

# Azure Update の RSS フィードの URL
RSS_URL = "https://www.microsoft.com/releasecommunications/api/v2/azure/rss"

# Azure OpenAI のクライアントを生成
client = AzureOpenAI(
    api_key=os.getenv("API_KEY"),
    api_version=os.getenv("API_VERSION"),
    azure_endpoint=os.getenv("API_ENDPOINT")
)

# システムプロンプトの設定
systemprompt = ("渡されたデータに含まれている Azure のアップデート情報を日本語で 3 行程度で要約してください。" +
                "リンク用のURLやマークダウンは含まず、プレーンテキストで出力してください。")

# 過去 N 日分、の計算をするために、現在時刻の取得
now = datetime.now()


# 引数に渡された URL から、Azure Update の記事 ID を取得して Azure Update API に HTTP Get を行い、その記事を要約する
def read_and_summary(url):
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

# Azure Update の RSS フィードを読み込んで URL のリストを返す。引数には過去何日まで取得するかを指定する
def get_update_urls(days):
    # RSS フィードを読み込む
    feed = feedparser.parse(RSS_URL)
    logging.debug(feed)

    # フィードからエントリーを取得
    entries = feed.entries

    # entries から published が指定された日数以内のエントリーの URL をリスト化
    start_date = now - timedelta(days=days) # 取得開始日
    urls = []
    for entry in entries:
        published = entry.published_parsed
        rss_published_datetime = datetime.fromtimestamp(mktime(published))
        if published is not None:
            if (rss_published_datetime > start_date):
                urls.append(entry.link)

    return urls

def environment_check():
    logging.debug(f"API_KEY: {os.getenv('API_KEY')}")
    logging.debug(f"API_VERSION: {os.getenv('API_VERSION')}")
    logging.debug(f"API_ENDPOINT: {os.getenv('API_ENDPOINT')}")
    logging.debug(f"DEPLOYMENT_NAME: {os.getenv('DEPLOYMENT_NAME')}")
    # logging.debug(f"AZURE_STORAGE_CONNECTION_STRING: {os.getenv('AZURE_STORAGE_CONNECTION_STRING')}")
    # logging.debug(f"AZURE_STORAGE_ACCOUNT_CONTAINER_NAME: {os.getenv('AZURE_STORAGE_ACCOUNT_CONTAINER_NAME')}")

    if (os.getenv("API_KEY") == ""
        or os.getenv("API_VERSION") == ""
        or os.getenv("API_ENDPOINT") == ""
        or os.getenv("DEPLOYMENT_NAME") == ""
        # or os.getenv("AZURE_STORAGE_CONNECTION_STRING") == ""
        # or os.getenv("AZURE_STORAGE_ACCOUNT_CONTAINER_NAME") == ""
        ):
        logging.error('環境変数が不足しています。.env ファイルを確認してください。 (Environment variables are missing. Please check the .env file.)')
        return False
    else:
        return True

# メイン関数
def main():
    # Azure Update の RSS フィードから条件に合う URL のリストを取得
    urls = get_update_urls(DAYS)
    logging.debug(urls)

    # URL のリストをループして、それぞれの URL を読み込んで要約を取得
    for url in urls:
        print("\n")
        logging.debug("***** Begin of Recode *****")
        result = read_and_summary(url)
        # result の中身をログに出力
        logging.debug(result)

        # result の中身は json なので、パースして一行ずつ出力。出力は 要素名 : 値 とする
        for key in result.keys():
            print(f"{key} : {result[key]}")
        logging.debug("***** End of Recode *****")

        print("\n")

# メイン関数を実行
if __name__ == '__main__':
    main()
