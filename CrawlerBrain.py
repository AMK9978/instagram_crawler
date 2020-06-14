import requests
import re
from bs4 import BeautifulSoup
import json

url = 'https://www.instagram.com/chandmahame/'
page = requests.get(url)
epoch_min = 60
epoch_hour = 3600
epoch_day = 86400
epoch_month = 2592000
epoch_year = 31557600


def convert_to_date(created_at):
    year = created_at // epoch_year
    rem_month = created_at - year * epoch_year
    month = rem_month // epoch_month
    rem_day = rem_month - month * epoch_month
    day = rem_day // epoch_day
    rem_hour = rem_day - day * epoch_day
    hour = rem_hour // epoch_hour
    rem_min = rem_hour - hour * epoch_hour
    minute = rem_min // epoch_min
    year += 1970
    return "{}/{}/{},{}:{}".format(year, day, month, hour, minute)


soup = BeautifulSoup(page.content, 'html.parser')
results = soup.find_all('section', class_='ySN3v')

posts = []
like_base_url = 'https://www.instagram.com/graphql/query/'

posts_dic = {}
# Specify how many users must be fetched
first = 0
include_reel = True
# query_hash_like = input("Please input query hash for like:").strip()
# query_hash_comment = input("Please input query hash for comment:").strip()
like_query_hash = "d5d763b1e2acf209d62d22d184488e57"
comment_query_hash = "bc3296d1ce80a24b1b6e40b1e72903f5"

x = re.findall("shortcode\":\".*?\"", str(page.content))
for target in x:
    short_code = re.search(":\"(.*?)\"", target).group(0)[2:-1]
    link = url + "p/" + short_code
    # Get all links of posts as below
    posts.append(link)
    # Get the likes count
    sub_content = requests.get(link).content
    likes_count = re.search("\"edge_media_preview_like\":{\"count\":(.*?),", str(sub_content)).group(1)
    comments_count = re.search("\"edge_media_preview_comment\":{\"count\":(.*?),", str(sub_content)).group(1)
    first = likes_count
    posts_dic[likes_count] = link
    like_params = {'query_hash': like_query_hash, 'shortcode': short_code, 'first': first,
                   'include_reel': include_reel}
    comment_params = {'query_hash': comment_query_hash, 'shortcode': short_code, 'first': first,
                      'include_reel': include_reel}
    likes_content = requests.request("GET", like_base_url, params=like_params)
    like_response = likes_content.text.encode('utf8')
    like_nodes = json.loads(like_response)['data']['shortcode_media']['edge_liked_by']['edges']
    comments_content = requests.request("GET", like_base_url, params=comment_params)
    comment_response = comments_content.text.encode('utf8')
    comment_nodes = json.loads(comment_response)['data']['shortcode_media']['edge_media_to_parent_comment']['edges']
    for node in comment_nodes:
        json_node = json.loads(json.dumps(node))['node']
        print("username:{},text:{}, date:{}".format(json_node['owner']['username'],
                                                    json_node['text'],
                                                    convert_to_date(int(json.dumps(json_node['created_at'])))))
