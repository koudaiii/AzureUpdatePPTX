from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import azureupdatehelper as azup
import random
from pptx import Presentation
from pptx.util import Inches, Pt, Cm
from datetime import datetime, timedelta, timezone
from time import mktime
import os

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, generate_blob_sas, BlobSasPermissions

import tempfile
import logging

st.title('Azure Update PPTX Generator')

# 何日前までのアップデートを取得するか streamlit で指定
days = st.slider('何日前までのアップデートを取得しますか？', 1, 30, 7)

# スライド作者名設定
slide_auther = st.text_input('スライドの作者名を入力してください。', 'Takashi Okawa')

# スライドのファイル名の拡張子なしの文字列を入力
name_prefix = st.text_input('スライドのファイル名を拡張子なしで入力してください。', 'AzureUpdates')
#ファイル名が重複しないように今日の日付(YYYYMMDD)と4桁のランダムな数字を付与
save_name = name_prefix + datetime.now().strftime('%Y%m%d') + str(random.randint(1000,9999)) + '.pptx'

# ボタンを押すと Azure Update API からデータを取得して PPTX を生成
if st.button('PPTX 生成'):
    # 環境変数の確認
    st.info(
        f"""
    以下の環境変数が設定されています。 \n
    API_KEY: {os.getenv("API_KEY")} \n
    API_ENDPOINT: {os.getenv("API_ENDPOINT")} \n
    API_VERSION: {os.getenv("API_VERSION")} \n
    DEPLOYMENT_NAME: {os.getenv("DEPLOYMENT_NAME")} \n
    AZURE_STORAGE_CONNECTION_STRING: {os.getenv("AZURE_STORAGE_CONNECTION_STRING")} \n
    AZURE_STORAGE_ACCOUNT_CONTAINER_NAME: {os.getenv("AZURE_STORAGE_ACCOUNT_CONTAINER_NAME")} \n
    """
    )

    # 環境変数が不足している場合はエラーを表示して終了
    if (os.getenv("API_KEY") == ""
        or os.getenv("API_ENDPOINT") == ""
        or os.getenv("API_VERSION") == ""
        or os.getenv("DEPLOYMENT_NAME") == ""
        or os.getenv("AZURE_STORAGE_CONNECTION_STRING") == ""
        or os.getenv("AZURE_STORAGE_ACCOUNT_CONTAINER_NAME") == ""):
        st.error('環境変数が不足しています。.env ファイルを確認してください。 (Environment variables are missing. Please check the .env file.)')
        st.stop()

    # Azure Update API からデータを取得
    st.write('データ取得中...')
    urls = azup.get_update_urls(days)
    st.write('含まれる Azure Update の URL は以下の通りです。')
    st.write(urls)

    # PPTX 生成処理
    st.write('PPTX 生成中...')

    #初期設定
    #スライドタイトルテキスト
    slide_title = "Azure Updates"
    #スライドの発行者名
    #slide_auther = "Takashi Okawa"
    #スライドの保存ファイル名
    #save_name = "AzureUpdates.pptx"

    # PPTX の保存先を一時ファイルに指定
    pptx_file = tempfile.NamedTemporaryFile(delete=False)
    tmp_prs = Presentation("template/gpstemplate.pptx")
    prs = tmp_prs

    # スライドに関する諸々の初期設定
    now = datetime.now() # 現在時刻の取得
    today = now.strftime('%Y年%m月%d日') # 現在時刻を年月曜日で表示
    start_date = now - timedelta(days) # 現在時刻から過去何日前までのアップデートをスライドに含めるか
    start_day_str = start_date.strftime('%Y年%m月%d日') # アップデートの開始日を年月曜日で表示

    # 1枚目（タイトルスライドを自動生成)
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title_shape = slide.shapes.title
    date_ph = slide.placeholders[13]
    title_shape.text = slide_title
    date_ph.text = today
    auth_ph = slide.placeholders[12]
    auth_ph.text = slide_auther

    # 2枚目(スライドレイアウト ID 27 のプレースホルダーに、いつからいつまでの情報が入っているか記載)
    section_title_slide_layout = prs.slide_layouts[27]
    slide = prs.slides.add_slide(section_title_slide_layout)
    title_shape = slide.shapes.title
    title_shape.text = str(start_day_str) + " ～ \n" + str(today) + " のアップデート"
    date_ph = slide.placeholders[0]

    # 3枚目以降（Azure Update の情報をスライドに追加)
    for url in urls:
        print("\n")
        logging.info("***** Begin of Recode *****")
        result = azup.read_and_summary(url)
        # result の中身をログに出力
        logging.debug(result)

        # result の中身は json なので、パースして一行ずつ出力。出力は 要素名 : 値 とする
        for key in result.keys():
            print(f"{key} : {result[key]}")
        logging.info("***** End of Recode *****")

        st.write('以下の Azure Update の情報をスライドに追加しています。')
        st.write(result["title"])
        st.write(result["summary"])

        #スライドマスタの3番目にあるレイアウト（社内テンプレではタイトルと箇条書きテキスト）を選択
        main_layout = prs.slide_layouts[2]

        # スライドを一枚追加
        slide = prs.slides.add_slide(main_layout)
        title_shape = slide.shapes.title
        title_shape.text = result["title"]

        #title_shapeのフォントサイズを26ptにする
        title_shape.text_frame.paragraphs[0].font.size = Pt(26)

        #body_shape にプレースホルダー 1 を割り当て
        body_shape = slide.placeholders[10]

        #プレースホルダー1に諸々のコンテンツを流し込み
        p = body_shape.text_frame.add_paragraph()
        p.text = result["summary"]
        p.level = 0

        p = body_shape.text_frame.add_paragraph()
        p.level = 1
        r = p.add_run()
        r.text = result["url"]
        hlink = r.hyperlink
        hlink.address = result["url"]

        # 公開日の時刻データに標準準拠しないタイムゾーン情報が入っているので、それを削除してから利用。
        p = body_shape.text_frame.add_paragraph()
        idx = result["publishedDate"].find(".")
        pubDate = result["publishedDate"][:idx]

        logging.info(result["publishedDate"])
        p.text = "公開日: " + datetime.strptime(pubDate, '%Y-%m-%dT%H:%M:%S').strftime('%Y年%m月%d日')
        p.level = 2
        print("\n")

    # PPTX を保存
    prs.save(pptx_file.name)
    st.write('PPTX 生成完了')

    #　.env の Azure Storage の設定を読み込み
    azurestorageconstr = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container_name = os.getenv("AZURE_STORAGE_ACCOUNT_CONTAINER_NAME")

    # Azure Storage に接続
    blob_service_client = BlobServiceClient.from_connection_string(azurestorageconstr)
    container_client = blob_service_client.get_container_client(container_name)

    # 保存先のコンテナが存在しない場合は作成
    if not container_client.exists():
        container_client.create_container()
        st.write('コンテナを新規作成しました。')

    # 一時ファイルから Azure Storage にアップロード
    with open(pptx_file.name, "rb") as data:
        blob_client = container_client.upload_blob(name=save_name, data=data, overwrite=True)
        st.write('PPTX を Azure Storage にアップロードしました。')

        # blob client から account key を取得
        account_key = blob_service_client.credential.account_key

        # いまアップロードした PPTX にアクセス可能な SAS URL を生成
        sas_token = generate_blob_sas(
            account_name=blob_service_client.account_name,
            container_name=container_name,
            blob_name=save_name,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(timezone.utc) + timedelta(hours=1)
        )

        sas_url = blob_client.url + "?" + sas_token

        # SAS URL でダウンロードボタンを作成
        st.write('以下のリンクからダウンロードしてください。')
        st.markdown(f'<a href="{sas_url}" download="{save_name}">Download {save_name}</a>', unsafe_allow_html=True)
    pptx_file.close()
    # 一時ファイルを削除
    os.remove(pptx_file.name)
