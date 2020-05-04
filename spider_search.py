from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import TimeoutException
from pyquery import PyQuery as pq
import random
from dbconfig import *
import pymongo

#定义数据库
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

#定义浏览器
browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)

def search(company_name):
    """执行百度搜索公司名称"""
    try:
        #搜索功能
        browser.get('https://www.baidu.com')
        #等待搜索框和搜索按键完成加载
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#kw")))
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#su")))
        #输入搜索内容并完成搜索
        input.send_keys(company_name + " site:linkedin.com")
        time.sleep(1)
        submit.click()
        time.sleep(2)
        wait.until(EC.presence_of_all_elements_located)
        return ''
    except TimeoutException:
        return search(company_name)

def next_page(page_num): 
    """执行翻页"""
    try:
        #第一页与第二页翻页按钮对应的CSS不同
        if page_num == '1':
            submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#page > a.n")))
            submit.click()
        else:
            submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#page > a:nth-child(12)")))
            submit.click()
        cu_num = int(page_num) + 1
        #检验翻页是否成功
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#page > strong > span.pc"), str(cu_num)))
    except TimeoutException:
        next_page(page_num)
    
def get_doc():
    """获取html并用pyquery解析"""
    wait.until(EC.presence_of_all_elements_located)
    html = browser.page_source
    doc = pq(html)
    return doc

def get_result(page_num, doc):
    """获取百度搜索内容"""
    #解析各内容对应的位置信息
    for i in range((int(page_num) - 1)*10 + 1, int(page_num)*10 + 1):
        pos_title = '#' + str(i) +' .t'
        pos_href = '#' + str(i) +' .f13 a'
        pos_taget = '#' + str(i) +' .t em'
        pos_intro = '#' + str(i) +' .c-abstract'
        pos_showlink = '#' + str(i) +' .f13 a'
        result = {
            '标题': doc(pos_title).text(),
            '链接': doc(pos_href).attr('href'),
            '摘要': doc(pos_intro).text(),
            't': doc(pos_taget).text(),
            'cshowurl': doc(pos_showlink).text().split(' ')[0]
        }
        save_to_mongo(result)

def get_result(page_num, doc):
    """获取百度搜索内容"""
    #解析各内容对应的位置信息
    for i in range((int(page_num) - 1)*10 + 1, int(page_num)*10 + 1):
        pos_title = '#' + str(i) +' .t'
        pos_href = '#' + str(i) +' .f13 a'
        pos_taget = '#' + str(i) +' .t em'
        pos_intro = '#' + str(i) +' .c-abstract'
        pos_showlink = '#' + str(i) +' .f13 a'
        result = {
            '标题': doc(pos_title).text(), 
            '链接': doc(pos_href).attr('href'),
            '摘要': doc(pos_intro).text(),
            't': doc(pos_taget).text(),
            'cshowurl': doc(pos_showlink).text().split(' ')[0]
        }
        save_to_mongo(result)

def save_to_mongo(result):
    """检验是否存储到数据库"""
    try:
        if db[MONGO_TABLE].insert(result):
            print('存储到MINGODB成功', result)
    except Exception:
        print('存储到MONGODB失败',result)

def main():
    """搜索指定页码，制定公司的数据并存储到数据库"""
    #输入页码和公司
    total = int(input("请输入查看页数"))
    company_name = input("请输入公司名称")
    
    #由于第一页和后续页按键css不同所以分别处理
    if total == 1:
        search(company_name)
        page = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#page > strong > span.pc")))
        page_num = page.text    
        doc = get_doc()
        get_result(page_num, doc)
    elif total > 1:
        search(company_name)
        page = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#page > strong > span.pc")))
        page_num = page.text   
        doc = get_doc()
        get_result(page_num, doc)
        for i in range(2, total+1):
            next_page(page_num)
            page = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#page > strong > span.pc")))
            page_num = page.text    
            doc = get_doc()
            get_result(page_num, doc)

if __name__ == '__main__':
    main()
