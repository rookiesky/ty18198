from Request import Request
from bs4 import BeautifulSoup
import time

request = Request()
list_links = []
post_api = 'https://www.ty18198.com/wordpress_post_json_api.php?action=save'

def getList(url):
    global list_links
    headers = {
        'Host':'forum.thetaxbook.com',
        'Referer':'https://forum.thetaxbook.com/forum/discussion-forums/main-forum-tax-discussion/304111-preparer-responsible-for-client-penalty'
    }

    response = request.request(url=url,headers=headers)
    if response == False:
        return False

    soup = BeautifulSoup(response,'html.parser')
    links = soup.find_all('a',attrs={'class','topic-title js-topic-title'})
    list_links = [item.get('href') for item in links]

def bodyFormat(soup):
    post_title = soup.find('h2',attrs={'class','b-post__title js-post-title b-post__hide-when-deleted'}).text.replace('\r','').replace('\n','').replace('\t','')
    author = soup.find_all('div',attrs={'class','author h-text-size--14'})
    post_author = [item.contents[1].text for item in author]
    author = []
    dates = soup.find_all('time',attrs={'itemprop':'dateCreated'})
    post_date = [item.get('datetime').replace('T',' ') for item in dates]
    dates = []
    body = soup.find_all('div',attrs={'class','js-post__content-text restore h-wordwrap'})
    post_content = [str(item) for item in body]
    body = []
    return {'post_title':post_title,'post_author':post_author,'post_date':post_date,'post_content':post_content}

def resultFormat(data):
    body = {
        'post_title':data['post_title'],
        'post_author':data['post_author'][0],
        'post_date':data['post_date'][0],
        'post_content': data['post_content'][0],
        'replys':[]
    }
    for i in range(1,len(data['post_author'])):
        body['replys'].append({
            'author':data['post_author'][i],
            'date':data['post_date'][i],
            'content': data['post_content'][i]
        })
    data = []
    return body

def body():
    global list_links
    for url in list_links:
        response = request.request(url=url)
        if response == False:
            continue

        try:
            soup = BeautifulSoup(response,'html.parser')
            data = bodyFormat(soup)
            data = resultFormat(data)
            data['post_category'] = 'Taxation'
            request.requestPostJson(api=post_api,json=data)
            request.logger.info('Post Success,TITLE:{}'.format(data['post_title']))
        except Exception as e:
            request.logger.error('body format error,msg:{}'.format(e))
        soup = ''
        data = ''
        response = ''
    list_links = []

def main():  
    url = 'https://forum.thetaxbook.com/forum/discussion-forums/main-forum-tax-discussion/page1'
    getList(url)
    if len(list_links) <= 0:
        exit()
    body()
    request.logger.info('reptile success')

try:
    main()
    request.logger.info('thetaxbook success')
except:
    request.logger.error('thetaxbook Error')