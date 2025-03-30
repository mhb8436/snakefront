import os, re
import requests
from urllib.parse  import urlparse
import smart_open
# https://github.com/mhb8436/test11/raw/main/workflow/Snakefile
# https://raw.githubusercontent.com/mhb8436/test11/main/workflow/Snakefile

def make_github_raw_url_with_token(url):
    # print('make_github_raw_url_with_token', url)
    parsed_url = urlparse(url)
    path_arr = parsed_url.path.split('/')
    path_arr.remove('raw')    
    # token = os.environ['GITHUB_TOKEN']
    new_url = 'https://raw.githubusercontent.com%s'%('/'.join(path_arr))    
    return new_url
    

def open_test(url):    
    token = os.environ['GITHUB_TOKEN']
    # return smart_open.http.open(url,mode='rb')
    return smart_open.http.open(url,mode='rb', headers={'Authorization': 'token ' + token, 'Accept-Encoding':'identity'})


def open_test2(url):
    # return smart_open.open(url, mode='rb')
    token = os.environ['GITHUB_TOKEN']
    return smart_open.http.SeekableBufferedInputBase(url)
    # return smart_open.http.SeekableBufferedInputBase(url, headers={'Authorization': 'token ' + token})

def make_git_url_with_token(url):
    parsed_url = urlparse(url)
    token = os.environ['GITHUB_TOKEN']
    token = 'oath2:%s'%token
    return '%s://%s@%s%s'%(parsed_url.scheme, token, parsed_url.netloc, parsed_url.path)

if __name__ == '__main__':
    url = 'https://github.com/mhb8436/test11/raw/main/workflow/Snakefile'
    new_url = make_github_raw_url_with_token(url)
    # print(new_url)
    # token = os.environ['GITHUB_TOKEN']
    # resp = requests.get(new_url, headers={'Authorization': 'token ' + token})
    # print(resp.text)
    dd = open_test('https://github.com/mhb8436/test4/raw/main/workflow/Snakefile')
    print(dd.read())
    ss = open_test2('https://github.com/mhb8436/test4/raw/main/workflow/Snakefile')
    print(ss.read())
    # url = 'https://github.com/mhb8436/test11.git'
    # new_url = make_git_url_with_token(url)    
    # print(new_url)

