import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import pandas as pd
import requests

start_url = 'https://www.musashino-u.ac.jp/'
parsed_base = urlparse(start_url)
domain = parsed_base.netloc

visited_urls = set()
queue = [start_url]
page_data = {}

# ★除外したい拡張子（PDFや画像、Excelなどを弾く）
excluded_extensions = (
    '.pdf',
    '.xlsx',
    '.xls',
    '.docx',
    '.doc',
    '.zip',
    '.jpg',
    '.png',
    '.gif',
    '.css',
    '.js',
)

print('クローリングおよびスクレイピングを開始します（HTMLページ限定）...')

while queue:
  current_url = queue.pop(0)

  if current_url in visited_urls:
    continue

  print(f'訪問中: {current_url}')
  time.sleep(1)

  try:
    response = requests.get(current_url, timeout=10)
    response.encoding = response.apparent_encoding

    soup = BeautifulSoup(response.text, 'html.parser')

    title_tag = soup.find('title')
    if title_tag:
      page_title = title_tag.get_text(strip=True)
      page_data[current_url] = page_title

    visited_urls.add(current_url)

    links = soup.find_all('a', href=True)
    for a_tag in links:
      href = a_tag['href']
      absolute_url = urljoin(current_url, href)
      parsed_link = urlparse(absolute_url)

      if parsed_link.netloc == domain:
        clean_url = f'{parsed_link.scheme}://{parsed_link.netloc}{parsed_link.path}'

        # ★PDFなどの不要なファイルをキューに入れない
        if not clean_url.lower().endswith(excluded_extensions):
          if clean_url not in visited_urls and clean_url not in queue:
            queue.append(clean_url)

  except Exception as e:
    print(f'エラー発生 ({current_url}): {e}')

df = pd.DataFrame(list(page_data.items()), columns=['URL', 'Title'])
csv_filename = 'musashino_u_pages.csv'
df.to_csv(csv_filename, index=False, encoding='utf-8-sig')

print(f'\nすべての処理が完了しました！')
print(f'総取得ページ数: {len(page_data)}件')
print(f'保存ファイル: {csv_filename}')