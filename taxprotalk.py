from Request import Request
from bs4 import BeautifulSoup
import time

request = Request()

host= 'https://www.taxprotalk.com/forums'
list_links = []
post_api = 'https://www.ty18198.com/wordpress_post_json_api.php?action=save'
cate = ''

def getList(url):
    global list_links
    response = request.request(url=url)
    if response == False:
        return False

    soup = BeautifulSoup(response,'html.parser')
    links = soup.find_all('a',attrs={'class','topictitle'})
    list_links = [host + item.get('href').lstrip('.') for item in links][2:]

def bodyAndRepay(title,usernames,post_dates,post_content):
    body = {
        'post_title':title,
        'post_author':usernames[0],
        'post_date':post_dates[0],
        'post_content': post_content[0]
    }
    repay = []
    for i in range(1,len(usernames)):
        repay.append({
            'author':usernames[i],
            'date':post_dates[i],
            'content': post_content[i]
        })
    usernames = []
    post_content = []
    post_dates = []
    body['replys'] = repay
    return body

def bodyFormat(soup):
    title = soup.find('h2').next.text
    names = soup.find_all('div',attrs={'class','tpt-whome'})
    usernames = [item.contents[1].text for item in names]
    names = []
    dates = soup.find_all('span',attrs={'class','tpt-postdate'})
    post_dates = [time.strftime('%Y-%m-%d %H:%M',time.strptime(item.text.rstrip('\n\t\t\t\t\t').replace('\n\xa0',''),"%d-%b-%Y %I:%M%p")) for item in dates]
    body = soup.find_all('div',attrs={'class','content'})
    post_content = [str(item) for item in body]
    body = []
    return bodyAndRepay(title,usernames,post_dates,post_content)


def body():
    global list_links, cate
    for url in list_links:
        response = request.request(url=url)
        if response == False:
            continue

        soup = BeautifulSoup(response,'html.parser')
        try:
            data = bodyFormat(soup)
            data['post_category'] = cate
            response = request.requestPostJson(api=post_api,json=data)
            request.logger.info('Post Success,title:{}'.format(data['post_title']))
        except Exception as e:
            request.logger.error('body format error,msg:{}'.format(e))
        soup = ''
        response = ''
    list_links = []

def content(url):
    getList(url)
    if len(list_links) <= 0 :
        request.logger.error('list links is empty')
        return False
    body()

def main():
    global cate
    list = [{
            'cate': 'Taxation',
            'url': 'https://www.taxprotalk.com/forums/viewforum.php?f=8'
            },
            {
            'cate': 'General Accounting',
            'url': 'https://www.taxprotalk.com/forums/viewforum.php?f=9'
            },
            {
            'cate': 'Business Operations and Development',
            'url': 'https://www.taxprotalk.com/forums/viewforum.php?f=10'
            },
        ]
    for item in list:
        cate = item['cate']      
        content(item['url'])
        request.logger.info('reptile success,cate:{}'.format(item['cate']))
        time.sleep(2)
        
try:        
    main()
    request.logger.info('taxprotalk Success')
except:
    request.logger.error('taxprotalk Error')