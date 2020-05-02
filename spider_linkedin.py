#包引用模块
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import TimeoutException
#定义百度获取领英员工数据的函数
def search(company_name, nums):
    try:
        #定义browser类
        browser = webdriver.Chrome()
        #定义wait类
        wait = WebDriverWait(browser, 10)
        #搜索功能
        browser.get('https://www.baidu.com')
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#kw")))
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#su")))
        input.send_keys(company_name)
        time.sleep(1)
        submit.click()
        time.sleep(2)
        page_num = 1
        print("成功爬取第" + str(page_num) + '页数据')
        #翻页功能
        for i in range(nums):
            #首页翻页css与其他页不同
            if int(page_num) == 1:
                submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#page > a.n")))
                submit.click()
                page = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#page > strong > span.pc")))
                page_num = page.text
            #2页以后的翻页
            elif int(page_num) == (i+1) :
                submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#page > a:nth-child(12)")))
                submit.click()
            #错误处理
            else:
                print(翻页错误)
            time.sleep(3)
            page = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#page > strong > span.pc")))
            page_num = page.text
            print("成功爬取第" + str(page_num) + '页数据')
    except TimeoutException:
        return search(company_name)

#测试模块
company_name = input('请输入公司名称')
nums = int(input("请输入爬取页数")) - 1
search(company_name, nums)

