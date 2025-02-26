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

# Set the browser page title
st.set_page_config(page_title="Azure Update Summary",
                   page_icon=":cloud:",
                   initial_sidebar_state="auto",
                   layout="centered",
                   menu_items={
                       "Report a bug": "https://github.com/koudaiii/AzureUpdatePPTX/issues",
                       "About": "https://koudaiii.com"
                       }
                  )

# Set the browser tab title
st.title('Azure Update Summary')

# ファイル名が重複しないように今日の日付(YYYYMMDDHHMMSS)
save_name = 'AzureUpdates' + datetime.now().strftime('%Y%m%d%H%M%S') + '.pptx'

# Azure Update API からデータを取得
entries = azup.get_rss_feed_entries()
st.write(
    f"取得した Azure Update のエントリーは {azup.oldest_article_date(entries)} から "
    f"{azup.latest_article_date(entries)} の {len(entries)} 件です。"
)

# 何日前までのアップデートを取得するか streamlit で指定
days = st.slider('何日前までのアップデートを取得しますか？', 1, 90, 7)

# Azure Update スライドにタイトル設定
def set_slide_title(shape, text, font_size=Pt(24)):
    shape.text = text
    if shape.text_frame and shape.text_frame.paragraphs:
        shape.text_frame.paragraphs[0].font.size = font_size


# Azure Update スライドに公開日 published_date_text と azure_update_url を一行の文として追加
def add_hyperlink_text(text_frame, prefix, url, font_size=Pt(18)):
    text_frame.clear()
    p = text_frame.paragraphs[0]
    run = p.add_run()
    run.text = f"{prefix}"
    run.hyperlink.address = url
    run.font.size = font_size


# Azure Update スライドに本文 summary を追加
def add_body_summary(slide, summary):
    body_shape = slide.placeholders[11]
    text_frame = body_shape.text_frame
    text_frame.clear()
    # 既存の段落が無い場合は、新たに段落を追加する
    paragraph = text_frame.paragraphs[0] if text_frame.paragraphs else text_frame.add_paragraph()
    paragraph.text = summary
    paragraph.level = 0


# Azure Update スライドに参照リンク reference_links を追加
def add_reference_links(text_frame, label, links):
    # Add header for the reference links
    header = text_frame.add_paragraph()
    header.text = label
    header.level = 2
    # Add each link as a new paragraph with a hyperlink
    for link in links:
        link = link.strip()
        p = text_frame.add_paragraph()
        p.level = 3
        run = p.add_run()
        run.text = link
        run.hyperlink.address = link


# 表紙を作成
def create_title_slide(prs, title, date_str):
    """
    Creates and configures the title slide using the first layout.

    Args:
        prs: Presentation object.
        title: Title text for the slide.
        date_str: Date string to display in the date placeholder.

    Returns:
        The created slide.
    """
    slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(slide_layout)

    # Set the slide title.
    slide.shapes.title.text = title

    # Set the date in the designated placeholder.
    try:
        date_placeholder = slide.placeholders[13]
        date_placeholder.text = date_str
    except IndexError:
        # Log if the expected placeholder index is not found.
        logging.error("Placeholder index 13 for date not found in the title slide.")
    return slide


# セクションタイトルスライドを作成
def create_section_title_slide(prs, update_count):
    """
    Creates a section title slide indicating the total number of Azure updates.
    Args:
        prs: The Presentation object.
        update_count: The number of Azure updates.

    Returns:
        A tuple containing the created slide and its first placeholder.
    """
    layout = prs.slide_layouts[27]
    slide = prs.slides.add_slide(layout)
    slide.shapes.title.text = (
        f"Azureアップデートは {update_count} 件です。\n"
        "※ Azure OpenAI で要約しています。"
    )
    return slide, slide.placeholders[0]


# Azure Update の情報を表示
def display_update_info(title, url, published_date, summary, ref_label, ref_links):
    st.write('')
    st.markdown(f"「{title}」", unsafe_allow_html=True)
    st.markdown(
        f"<small><a href='{url}' target='_blank'>{published_date}</a></small>",
        unsafe_allow_html=True
    )
    st.markdown(f"<small>{summary}</small>", unsafe_allow_html=True)
    st.markdown(f"<small>{ref_label}</small>", unsafe_allow_html=True)
    for link in ref_links:
        st.markdown(
            f"<p style='line-height:80%; margin-bottom:10px; padding:0;'>"
            f"<a href='{link}' target='_blank'>{link}</a></p>",
            unsafe_allow_html=True
        )
    st.write('')


# Azure Update スライドに追加
def create_update_slide(prs, title, published_date, url, summary, ref_label, ref_links):
    """Creates a new slide for an Azure update and configures its elements."""
    layout = prs.slide_layouts[10]
    slide = prs.slides.add_slide(layout)

    # Set slide title
    set_slide_title(slide.shapes.title, title)

    # Add published date with hyperlink (using placeholder index 10)
    try:
        ph_date = slide.placeholders[10].text_frame
        add_hyperlink_text(ph_date, published_date, url)
    except IndexError:
        logging.error("Placeholder index 10 not found in update slide.")

    # Add summary/body content
    add_body_summary(slide, summary)

    # Add reference links (using placeholder index 11)
    try:
        ph_refs = slide.placeholders[11].text_frame
        add_reference_links(ph_refs, ref_label, ref_links)
    except IndexError:
        logging.error("Placeholder index 11 not found in update slide.")

    return slide


# Azure Update の内容を生成
def extract_update_data(result):
    title = result.get("title", "No Title")
    published_date_raw = result.get("publishedDate", "")
    published_date_str = published_date_raw.split(".")[0] if published_date_raw else ""
    try:
        dt = datetime.strptime(published_date_str, '%Y-%m-%dT%H:%M:%S')
        published_date_text = f"公開日: {dt.strftime('%Y年%m月%d日')}"
    except ValueError:
        published_date_text = "公開日: 不明"
    url = result.get("url", "")
    summary = result.get("summary", "")
    ref_label = "参照リンク: "
    ref_links = [link.strip() for link in result.get("referenceLink", "").split(",") if link.strip()]
    return title, published_date_text, url, summary, ref_label, ref_links


# Azure Update 作成
def process_update(url, client, deployment_name, prs):
    # Process and log Azure Update information
    logging.info("***** Begin of Record *****")
    result = azup.read_and_summary(client, deployment_name, url)
    logging.debug("Result: %s", result)
    for key, value in result.items():
        logging.info("%s : %s", key, value)
    logging.info("***** End of Record *****")

    # Extract update data from the result
    (
        azure_update_title,
        published_date_text,
        azure_update_url,
        azure_update_summary,
        reference_link_label,
        reference_links,
    ) = extract_update_data(result)

    # Display update information via Streamlit
    display_update_info(azure_update_title, azure_update_url, published_date_text,
                        azure_update_summary, reference_link_label, reference_links)

    # Create and add the update slide to the presentation
    create_update_slide(prs, azure_update_title, published_date_text, azure_update_url,
                        azure_update_summary, reference_link_label, reference_links)


# 表紙のタイトル
def generate_slide_info(start_date, end_date) -> tuple[str, str]:
    slide_title = f"Azure Updates {start_date.strftime('%Y/%m/%d')} ~ {end_date.strftime('%Y/%m/%d')}"
    return slide_title


# Azure Update の URL 一覧を表示
def display_update_urls(urls):
    update_count = len(urls)
    st.write(f"Azureアップデートは {update_count} 件です。")
    st.write("含まれる Azure Update の URL は以下の通りです。")
    st.write(urls)


# 指定された日付
def start_date(days):
    return datetime.now().astimezone() - timedelta(days)


# 終了日時は現在時刻
def end_date():
    return datetime.now().astimezone()


# ボタンを押すと Azure Update API からデータを取得して PPTX を生成
if st.button('PPTX 生成'):
    # 環境変数が不足している場合はエラーを表示して終了
    if not azup.environment_check():
        st.error('環境変数が不足しています。API_ENDPOINT と API_KEY を環境変数で指定してください。')
        st.stop()

    st.write(f'{start_date(days).strftime("%Y-%m-%d")} から {end_date().strftime("%Y-%m-%d")} のアップデートを取得します。')
    urls = azup.target_update_urls(entries, start_date(days))
    display_update_urls(urls)

    # PPTX 生成処理
    st.write('PPTX 生成中...')

    # Generate slide title and date string
    slide_title = generate_slide_info(start_date(days), end_date())

    # Create a temporary PPTX file using a template
    pptx_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pptx")
    prs = Presentation("template/gpstemplate.pptx")

    # スライド一枚目（タイトルスライド）
    slide = create_title_slide(prs, slide_title, end_date().strftime('%Y%m%d%H%M%S'))
    # スライド二枚目（セクションタイトルスライド）
    slide, date_ph = create_section_title_slide(prs, len(urls))

    # Azure OpenAI のクライアントを取得
    client, deployment_name = azup.azure_openai_client(os.getenv("API_KEY"), os.getenv("API_ENDPOINT"))
    # Azure Update の情報を取得してスライドを作成
    for url in urls:
        process_update(url, client, deployment_name, prs)

    # PPTX を保存
    prs.save(pptx_file.name)
    st.write('PPTX 生成完了')

    try:
        with open(pptx_file.name, "rb") as f:
            st.download_button("Download PPTX", f.read(), file_name=save_name)
    finally:
        pptx_file.close()
        # 一時ファイルを削除
        os.remove(pptx_file.name)
