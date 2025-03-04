import shutil
from bs4 import BeautifulSoup

# Path to the Streamlit package directory
streamlit_path = '/usr/local/lib/python3.12/site-packages/streamlit/static/index.html'

# Create a backup of the original index.html
shutil.copy2(streamlit_path, streamlit_path + '.bak')

# Read the original index.html
with open(streamlit_path, 'r') as file:
    html_content = file.read()

# Parse the HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Create new meta tags
meta_tags = [
    # General SEO
    {'name': 'description', 'content': 'Azure Updates を要約して PPTX にまとめます。'},
    {'name': 'author', 'content': 'Kodai Sakabe'},
    {
        'name': 'keywords',
        'content': (
            'azure updates, azure, azure updates summary, '
            'azure updates generate pptx, updates, summary, powerpoint'
        )
    },

    # Open Graph
    {'property': 'og:type', 'content': 'website'},
    {'property': 'og:url', 'content': 'https://azure.koudaiii.com'},
    {'property': 'og:title', 'content': 'Azure Updates Summary'},
    {'property': 'og:description', 'content': 'Azure Updates を要約して PPTX にまとめます。'},
    {'property': 'og:image', 'content': 'https://koudaiii.com/azure_update_summary.png'},

    # Twitter
    {'property': 'twitter:domain', 'content': 'azure.koudaiii.com'},
    {'property': 'twitter:url', 'content': 'https://azure.koudaiii.com'},
    {'name': 'twitter:image', 'content': 'https://koudaiii.com/azure_update_summary.png'},
    {'name': 'twitter:title', 'content': 'Azure Updates Summary'},
    {'name': 'twitter:description', 'content': 'Azure Updates を要約して PPTX にまとめます。'},
    {'name': 'twitter:card', 'content': 'summary_large_image'},
    {'name': 'twitter:site', 'content': '@koudaiii'},
    {'name': 'twitter:creator', 'content': '@koudaiii'},
]

# Add new meta tags to the head
for tag in meta_tags:
    new_tag = soup.new_tag('meta')
    for key, value in tag.items():
        new_tag[key] = value
    soup.head.append(new_tag)

# Add custom CSS and HTML for the header banner
style_tag = soup.new_tag('style')
style_tag.string = """
.header-banner {
    color: black;
    text-align: center;
    font-size: 14px;
    position: fixed;
    top: 0;
    width: 100%;
    z-index: 999991;
}
"""
soup.head.append(style_tag)

banner_div = soup.new_tag('div', **{'class': 'header-banner'})
banner_div.string = "Public Preview"
soup.body.insert(0, banner_div)

# Save the modified HTML
with open(streamlit_path, 'w') as file:
    file.write(str(soup))

print("Meta tags and header banner have been added to the Streamlit index.html file.")
