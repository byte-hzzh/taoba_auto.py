from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm
from PIL import Image
import time,csv,pymysql,re
conn = pymysql.connect(
                        host = "127.0.0.1",
                        port = 3306,
                        user = "root",
                        password = "root",
                        db = "demo",
                        charset= 'utf8mb4'
)
cursor = conn.cursor()
sql = 'insert into test(title, info,numb,size,status,address,timing) values(%s,%s,%s,%s,%s,%s,%s)'

def cli():
    button = chrome.find_element(By.CSS_SELECTOR,'#tp-bought-root > div.row-mod__row___1aPep.js-actions-row-top > div:nth-child(2) > div > button:nth-child(2)')
    chrome.execute_script('arguments[0].click();', button)
chrome = webdriver.Chrome()
chrome.get('https://login.taobao.com/member/login.jhtml')
chrome.maximize_window()
chrome.implicitly_wait(15)
chrome.find_element(By.CSS_SELECTOR,'#login > div.corner-icon-view.view-type-qrcode > i').click()#扫码登录
input('输入回车键：')
chrome.get('https://buyertrade.taobao.com/trade/itemlist/list_bought_items.htm?spm=a1z09.2.a2109.d1000368.35172e8dQYSzZh&nekot=1470211439694')
chrome.implicitly_wait(15)
t = int(input('输入起始查找日期(例：20200102)：'))
url1 =[]
flag =True
number=0
try:
    while flag:
        total = chrome.find_elements(By.CSS_SELECTOR, 'div.index-mod__order-container___1ur4-.js-order-container')
        for tl in tqdm(total):
            tim = tl.find_element(By.CSS_SELECTOR,'.bought-wrapper-mod__create-time___yNWVS').text
            tim =int(tim.replace('-',''))
            print(tim)
            if tim-t>=0:
                time.sleep(0.5)
                href = tl.find_element(By.LINK_TEXT,'订单详情')
                url1.append(href.get_attribute('href'))
            else:
                print('采集完成')
                flag=False
                break
        cli()
        time.sleep(15)
finally:
    input()
print(f'一共收集{len(url1)}个网站')
for m in tqdm(url1):
    print(f'第{number}个商品')
    print(m)
    chrome.get(m)
    chrome.implicitly_wait(10)
    title=[]
    number+=1
    # if len(chrome.find_elements(By.CSS_SELECTOR,'#appOrders > div > table > tbody > tr > td > ul > li > table > tbody > tr > td.header-status > div > a'))!=0:
    #     continue
    if len(chrome.find_elements(By.CSS_SELECTOR,'.item-meta .item-link'))!=0:
        title = [a.text for a in chrome.find_elements(By.CSS_SELECTOR,'.item-meta .item-link')]
        print(title)
        # if title.find('购物金')!=-1 or title.find('优惠券')!=-1:
        if len(chrome.find_elements(By.CSS_SELECTOR,'#appStepbar > div > ol > li.step-first > div > div.step-time > div'))!=0:
            for c in title:
                if c.find('购物金')==-1 and c.find('券')==-1 and c.find('有价')==-1 and c.find('大额')==-1 and c.find('1000')==-1:
                    info = [b.text for b in chrome.find_elements(By.CSS_SELECTOR, '.item-c2m')]
                    numb = [c.text for c in chrome.find_elements(By.CSS_SELECTOR,'#appOrders > div > table > tbody > tr > td > ul > li > table > tbody > tr > td.header-count.font-high-light')]
                    size = [d.text for d in chrome.find_elements(By.CSS_SELECTOR,'#appOrders > div > table > tbody > tr > td > ul > li > table > tbody > tr > td.header-item.order-item-info > div > div.item-meta > div.item-title > span:nth-child(2) > span.item-title-descrip > span')]
                    status = [e.text for e in chrome.find_elements(By.CSS_SELECTOR,'.font-black .ui-trade-label')]
                    timing = chrome.find_element(By.CSS_SELECTOR,'#appStepbar > div > ol > li.step-first > div > div.step-time > div').text
                    timing= [timing]*len(title)
                    address = chrome.find_element(By.CSS_SELECTOR,'#J_trade_imfor > div > ul > li:nth-child(1) > div.trade-imfor-dd > span').text
                    address = address.replace(' ,000000', '')
                    address = address.replace(' ','-')
                    address = re.sub(r'^[\u4e00-\u9fa5]{2,3},86-(\d{3})\d{4}(\d{4})(.*)',r'**,86-\1****\2\3',address)
                    address = [address]*len(title)
                    data_list =[]
                    for x,y,z,t,k,l,m in zip(title, info,numb,size,status,address,timing):
                        v={}
                        v['title']=x
                        v['info']=y
                        v['numb']=z
                        v['size']=t
                        v['status'] = k
                        v['address'] = l
                        v['timing'] = m
                        data_list.append(v)
                        # csv_writer.writerow(['title','info','address','timing'])
                    print(data_list)
                    for nl in data_list:
                        # writer.writerow(nl.values()
                        # print(nl.values())
                        cursor.execute(sql,(nl['title'],nl['info'],data_list[0]['numb'],nl['size'],nl['status'],nl['address'],nl['timing']))
                    conn.commit()
                    print(f'{title}, {info}, {numb},{size},{status},{address},{timing}')
                    break
    elif len(chrome.find_elements(By.XPATH,"//div[@class='name']/a"))!=0:
        ll = [other for other in chrome.find_elements(By.CSS_SELECTOR,'tr.order-item')]
        timing=chrome.find_element(By.CSS_SELECTOR,'#detail-panel > div > div.app-mod__tabs-container___199zJ > div:nth-child(2) > div > div > div > div.order-info-container-mod__order-info-container___3diAC > div.misc-info-mod__misc-info___2Z-Sl > div:nth-child(2) > span:nth-child(4) > span.misc-info-mod__content___1iLHM > span').text
        address = chrome.find_element(By.CSS_SELECTOR,'#detail-panel > div > div.app-mod__tabs-container___199zJ > div:nth-child(2) > div > div > div > div.address-memo-mod__address-note___2pDUJ > div:nth-child(1) > dl:nth-child(1) > dd').text
        address = address.replace(' 000000', '')
        address = address.replace(' ', '-')
        address = re.sub(r'^[\u4e00-\u9fa5]{2,3},86-(\d{3})\d{4}(\d{4})(.*)', r'**,86-\1****\2\3', address)
        for l in ll:
            if l.find_element(By.CSS_SELECTOR,"div.desc div.name a").text =='保险服务':
                continue
            elif l.find_elements(By.CSS_SELECTOR, "td:nth-child(3) div:nth-child(1) span")==[]:
                continue
            else:
                title = [te.text for te in l.find_elements(By.CSS_SELECTOR,"div.desc div.name a")]
                info = [io.text for io in l.find_elements(By.CSS_SELECTOR,"span.sku-mod__namevalue___17t3N:nth-child(1) span span")]
                size = [iot.text for iot in l.find_elements(By.CSS_SELECTOR,"span.sku-mod__namevalue___17t3N:nth-child(2) span span")]
                status = [q.text for q in l.find_elements(By.CSS_SELECTOR, "td:nth-child(3) div:nth-child(1) span")]
                numb =[e.text for e in l.find_elements(By.CSS_SELECTOR,"td:nth-child(6)")]
                cursor.execute(sql, (title[0],info[0],numb[0],size[0],status[0],address,timing))
                # print(len(title),len(info),len(numb),len(size),len(status))
                print(f'{title}, {info}, {numb},{size},{status},{address},{timing}')
            conn.commit()

        # print(title,12345678)
    elif len(chrome.find_elements(By.CSS_SELECTOR,'#detail-panel > div > div.app-mod__tabs-container___199zJ > div:nth-child(2) > div > div > div > div.order-info-container-mod__order-info-container___3diAC > div.order-info-mod__order-info___2F_JJ > table > tbody > tr:nth-child(2) > td.item-mod__item___2tBS0 > div.item-mod__text-info___2N9pN > div > div.name > a'))!=0:
        ls = chrome.find_elements(By.CSS_SELECTOR,'tr.order-item')
        timing = chrome.find_element(By.CSS_SELECTOR,'#J_TabView > div > div > div > table:nth-child(1) > tbody.misc-info > tr:nth-child(4) > td:nth-child(1) > span.trade-time').text
        address = chrome.find_element(By.CSS_SELECTOR,'table.simple-list.logistics-list tr:nth-child(3) td:nth-child(2)').text
        address = address.replace(' ,000000', '')
        address = address.replace(' ', '-')
        address = re.sub(r'^[\u4e00-\u9fa5]{2,3},86-(\d{3})\d{4}(\d{4})(.*)', r'**,86-\1****\2\3', address)
        for s in ls:
            title = s.find_element(By.CSS_SELECTOR,'span.name a').text
            if title =='保险服务':
                break
            if title.find('购物金') == -1 and title.find('券') == -1 and title.find('有价') == -1 and title.find('大额') == -1 and title.find('1000') == -1:
                info = [b.text for b in s.find_elements(By.CSS_SELECTOR, 'td:nth-child(2) span:nth-child(1)')]
                numb = [c.text for c in s.find_elements(By.CSS_SELECTOR,'td:nth-child(2) span:nth-child(1)')]
                size = [d.text for d in s.find_elements(By.CSS_SELECTOR,'td:nth-child(2) span:nth-child(2)')]
                status = [e.text for e in s.find_elements(By.CSS_SELECTOR, 'td:nth-child(3) ')]
                cursor.execute(sql, (title[0], info[0], numb[0], size[0], status[0], address, timing))
                print(f'{title}, {info}, {numb},{size},{status},{address},{timing}')
            conn.commit()

    else:
        continue
cursor.close()
conn.close()
# f.close()
input()
chrome.quit()