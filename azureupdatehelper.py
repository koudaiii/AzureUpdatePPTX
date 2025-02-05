import sys
import os
import requests
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
                "各提供する地域のリージョンについては、翻訳せずに英語表記のままにしてください。" +
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
    if query_params is None:
        logging.error("Query Parameters are not found in the endpoint URL.")
        return None, None

    api_version = query_params.get('api-version', '')
    if api_version == '' or api_version is None:
        logging.error("API Version is not found in the endpoint URL.")
        return None, None

    deployment_name_match = re.search(r"deployments/([^/]+)/", parsed_url.path)
    deployment_name = deployment_name_match.group(1) if deployment_name_match else ''
    if deployment_name == '':
        logging.error("Deployment Name is not found in the endpoint URL.")
        return None, None

    logging.debug(f"Extracted API Key: {key}")
    logging.debug(f"Extracted API Version: {api_version}")
    logging.debug(f"Extracted Deployment Name: {deployment_name}")

    return AzureOpenAI(api_key=key, api_version=api_version, azure_endpoint=endpoint), deployment_name


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


# URL から記事を順番に取得する
def get_article(url):
    # 記事用の url 生成
    docid = docid_from_url(url)
    if docid is None:
        logging.error(f"{url} から docid を取得できませんでした。")
        return None
    link = target_url(docid)
    if link is None:
        logging.error(f"{url} から link を取得できませんでした。")
        return None

    # Azure Update API 用に header に User-Agent 設定
    headers = {
        "User-Agent": "Safari/605.1.15"
    }

    # 記事取得
    response = requests.get(link, headers=headers)
    if response.status_code != 200:
        logging.error(f"{link} から記事を取得できませんでした。")
        logging.error(f"Status Code is '{response.status_code}'")
        logging.error(f"Response Message is '{response.text}'")
        return None

    return response


# 記事を要約する
def summarize_article(client, deployment_name, article):
    try:
        summary_list = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": systemprompt},
                {"role": "user", "content": article}
            ]
        )
        return summary_list.choices[0].message.content
    except Exception as e:
        logging.error("An error occurred during summary generation: %s", e)
        return None


# Azure Update API の URL を生成
def target_url(id):
    base_url = "https://www.microsoft.com/releasecommunications/api/v2/azure/"
    if id is None or id == '':
        return None
    return base_url + id


# URL から記事 ID を取得
def docid_from_url(url):
    query = urlparse.urlparse(url).query
    if query is None or query == '':
        logging.error(f"{url} からクエリ文字列を取得できませんでした。")
        return None

    query_list = dict(urlparse.parse_qsl(query))
    if query_list is None or query_list == '' or 'id' not in query_list:
        logging.error(f"{url} からリスト化と id を取得できませんでした。")
        return None
    return query_list['id']


# description から HTML タグを削除
def remove_html_tags(text):
    return re.sub(r'<[^>]*?>', '', text)


# description から a タグの href を取得
def get_a_href_from_html(html):
    return re.findall(r'<a href="([^"]*)"', html)


# 引数に渡された URL から、Azure Update の記事 ID を取得して Azure Update API に HTTP Get を行い、その記事を要約する
def read_and_summary(client, url):
    # URL からデータをダウンロード
    response = get_article(url)
    if response is None:
        return None
    logging.debug(response.text)

    logging.debug(f"記事のタイトル: {response.json()['title']}")
    logging.debug(f"記事の製品: {response.json()['products']}")
    logging.debug(f"記事の作成日: {response.json()['created']}")
    logging.debug(f"記事の更新日: {response.json()['modified']}")
    logging.debug(f"記事の説明: {remove_html_tags(response.json()['description'])}")
    logging.debug(f"記事の説明内のリンク: {get_a_href_from_html(response.json()['description'])}")
    logging.debug(f"記事のリンク: {url}")
    content = (
        "タイトル: " + response.json()['title'] + "\n"
        + "製品: " + ", ".join(response.json()['products']) + "\n"
        + "説明: " + remove_html_tags(response.json()['description']) + "\n"
        + "説明内のリンク: " + ", ".join(get_a_href_from_html(response.json()['description']))
    )


    # ダウンロードしたデータを Azure OpenAI で要約
    summary_list = client.chat.completions.create(
        model=os.getenv("DEPLOYMENT_NAME"),
        messages=[
            {"role": "system", "content": systemprompt},
            {"role": "user", "content": content}
        ]
    )
    summary = summary_list.choices[0].message.content
    if summary is None:
        logging.error("要約が生成されませんでした。")
        return None

    # URL から記事 ID を取得
    docid = docid_from_url(url)
    if docid is None:
        logging.error(f"{url} から docid を取得できませんでした。")
        return None
    # description から HTML タグを削除
    description = remove_html_tags(response.json()['description'])
    if description is None:
        logging.error(f"{response.json()['description']} の HTML タグの削除に失敗しました。")
        return None

    # retval に title と description と summary を JSON 形式で格納
    retval = {
        "url": url,
        "apiUrl": target_url(docid),
        "docId": docid,
        "title": response.json()['title'],
        "products": response.json()['products'],
        "description": description,
        "summary": summary,
        "publishedDate": response.json()['created'],
        "updatedDate": response.json()['modified']
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
    client, _ = azure_openai_client(os.getenv("API_KEY"), os.getenv("API_ENDPOINT"))
    print("Client: ", client)

    entries = get_rss_feed_entries()
    print(f"RSS フィードのエントリーは {len(entries)} 件です。")

    urls = get_update_urls(DAYS)
    print(f"Azureアップデートは {len(urls)} 件です。")
    print('含まれる Azure Update の URL は以下の通りです。')
    print(urls)
    print(read_and_summary(client, urls[0]))


if __name__ == "__main__":
    main()
