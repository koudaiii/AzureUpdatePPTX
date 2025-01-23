import streamlit as st
import azureupdatehelper as azup
import os
import tempfile
import logging
from pptx import Presentation
from pptx.util import Pt
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

st.title('Azure Update PPTX Generator')

# 何日前までのアップデートを取得するか streamlit で指定
days = st.slider('何日前までのアップデートを取得しますか？', 1, 30, 7)

# スライドのファイル名の拡張子なしの文字列を入力
name_prefix = st.text_input('スライドのファイル名を拡張子なしで入力してください。', 'AzureUpdates')
# ファイル名が重複しないように今日の日付(YYYYMMDDHHMMSS)
save_name = name_prefix + datetime.now().strftime('%Y%m%d%H%M%S') + '.pptx'

# ボタンを押すと Azure Update API からデータを取得して PPTX を生成
if st.button('PPTX 生成'):
    # 環境変数が不足している場合はエラーを表示して終了
    if not azup.environment_check():
        st.error('環境変数が不足しています。.env ファイルを確認してください。')
        st.stop()

    # Azure Update API からデータを取得
    st.write('データ取得中...')
    entries = azup.get_rss_feed_entries()
    urls = azup.get_update_urls(entries, days)

    st.write(f"Azureアップデートは {len(urls)} 件です。")
    st.write('含まれる Azure Update の URL は以下の通りです。')
    st.write(urls)

    # PPTX 生成処理
    st.write('PPTX 生成中...')

    # 初期設定
    # スライドタイトルテキスト
    start_date_str = (datetime.now() - timedelta(days=days)).strftime('%Y/%m/%d')
    end_date_str = datetime.now().strftime('%Y/%m/%d')
    slide_title = f"Azure Updates {start_date_str} ~ {end_date_str}"

    # PPTX の保存先を一時ファイルに指定
    pptx_file = tempfile.NamedTemporaryFile(delete=False)
    tmp_prs = Presentation("template/gpstemplate.pptx")
    prs = tmp_prs

    # 1枚目（タイトルスライドを自動生成)
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title_shape = slide.shapes.title
    date_ph = slide.placeholders[13]
    title_shape.text = slide_title
    date_ph.text = end_date_str
    auth_ph = slide.placeholders[12]

    # 2枚目(スライドレイアウト ID 27 のプレースホルダーに、いつからいつまでの情報が入っているか記載)
    section_title_slide_layout = prs.slide_layouts[27]
    slide = prs.slides.add_slide(section_title_slide_layout)
    title_shape = slide.shapes.title
    title_shape.text = f"Azureアップデートは {len(urls)} 件です。\n※ Azure OpenAI で要約しています。"
    date_ph = slide.placeholders[0]

    # 3枚目以降（Azure Update の情報をスライドに追加)
    client = azup.azure_openai_client(os.getenv("API_KEY"), os.getenv("API_ENDPOINT"))
    for url in urls:
        print("\n")
        logging.info("***** Begin of Record *****")
        result = azup.read_and_summary(client, url)
        # result の中身をログに出力
        logging.debug(result)

        # result の中身は json なので、パースして一行ずつ出力。出力は 要素名 : 値 とする
        for key in result.keys():
            print(f"{key} : {result[key]}")
        logging.info("***** End of Recode *****")

        st.write('以下の Azure Update の情報をスライドに追加しています。')
        st.write(result["title"])
        st.write(result["summary"])

        # スライドマスタの3番目にあるレイアウト（社内テンプレではタイトルと箇条書きテキスト）を選択
        main_layout = prs.slide_layouts[2]

        # スライドを一枚追加
        slide = prs.slides.add_slide(main_layout)
        title_shape = slide.shapes.title
        title_shape.text = result["title"]

        # title_shapeのフォントサイズを26ptにする
        title_shape.text_frame.paragraphs[0].font.size = Pt(26)

        # body_shape にプレースホルダー 1 を割り当て
        body_shape = slide.placeholders[10]

        # プレースホルダー1に諸々のコンテンツを流し込み
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

    try:
        with open(pptx_file.name, "rb") as f:
            st.download_button("Download PPTX", f.read(), file_name=save_name)

        # .env の Azure Storage の設定を読み込み
        azurestorageconstr = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        container_name = os.getenv("AZURE_STORAGE_ACCOUNT_CONTAINER_NAME")
    finally:
        pptx_file.close()
        # 一時ファイルを削除
        os.remove(pptx_file.name)
