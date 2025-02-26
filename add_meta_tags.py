import os
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
    {'name': 'keywords', 'content': 'azure updates, azure, azure updates summary, azure updates generate pptx, updates, summary, powerpoint'},

    # Open Graph
    {'property': 'og:type', 'content': 'website'},
    {'property': 'og:url', 'content': 'https://azure.koudaiii.com'},
    {'property': 'og:title', 'content': 'Azure Updates Summary'},
    {'property': 'og:description', 'content': 'Azure Updates を要約して PPTX にまとめます。'},
    {'property': 'og:image', 'content': 'https://opengraph.b-cdn.net/production/images/189613b4-180c-4fec-8715-908d5f86146b.png?token=5O8n6YskRFyXUC_Gi1qNqF3ocTOGCVxcLXzU4WcGbKg&height=630&width=1200&expires=33276555879'},

    # X
    {'property': 'twitter:domain', 'content': 'azure.koudaiii.com'},
    {'property': 'twitter:url', 'content': 'https://azure.koudaiii.com'},
    {'name': 'twitter:image', 'content': 'https://opengraph.b-cdn.net/production/images/189613b4-180c-4fec-8715-908d5f86146b.png?token=5O8n6YskRFyXUC_Gi1qNqF3ocTOGCVxcLXzU4WcGbKg&height=630&width=1200&expires=33276555879'},
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

# Save the modified HTML
with open(streamlit_path, 'w') as file:
    file.write(str(soup))

print("Meta tags have been added to the Streamlit index.html file.")
