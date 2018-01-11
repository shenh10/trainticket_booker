# -*- coding: utf-8 -*-  
import sys     
reload(sys) # Python2.5 初始化后会删除 sys.setdefaultencoding 这个方法，我们需要重新载入     
sys.setdefaultencoding('utf-8')
import pdb
import time
import pygame
import sys
import configparser
#from splinter.browser import Browser
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from datetime import datetime, timedelta
import pdb

import codecs # 解决 gbk 编码问题

class Ticket(object):
    def __init__(self, config_file):
        ## config parser setting
        self.config_file = config_file
        self.settings = configparser.ConfigParser()
        # self.settings._interpolation = configparser.ExtendedInterpolation()
        # self.settings.read(self.config_file)
        # 解决 gbk 编码问题
        self.settings.readfp(codecs.open(self.config_file, "r", "utf-8-sig"))
        ## environment setting
        self.brower='chrome'
        self.b = webdriver.Chrome() #Browser(driver_name=self.brower) 
        self.station={}
        self.url = "https://kyfw.12306.cn/otn/leftTicket/init"
        # 席别类型(对应列标号)
        self.ticket_index = [
                            '',
                            u'商务座',
                            u'一等座', 
                            u'二等座',
                            u'高级软卧',
                            u'软卧',
                            u'动卧',
                            u'硬卧',
                            u'软座',
                            u'硬座',
                            u'无座'
                            ]
        self.seat_type = ['A', 'B', 'C', 'D', 'E']
        self.username = ''
        self.password = ''
        self.date_format='%Y-%m-%d'
        self.tolerance = -1
        self.blacklist = {}
        self.date = []
        self.isStudent = False
        self.success = 0
        self.find_ticket = 0
        self.config_parser()
        self.playmusic = False
        self.count = 0

    def ConfigSectionMap(self,section):
            dict1 = {}
            options = self.settings.options(section)
            for option in options:
                try:
                    dict1[option] = self.settings.get(section, option)
                    if dict1[option] == -1:
                        DebugPrint("skip: %s" % option)
                except:
                        print("exception on %s!" % option)
                        dict1[option] = None
            return dict1
    def daterange(self, start_date, end_date):
        for n in range(int ((end_date - start_date).days) + 1):
            yield start_date + timedelta(n) 

    def config_parser(self):
        if self.retrieve_station_dict() == -1:
            sys.exit()
        if self.retrieve_book_options() == -1:
            sys.exit()
        
    def retrieve_station_dict(self):
        dict_helper=self.ConfigSectionMap('STATIONCOOKIE')
        for name, value in dict_helper.iteritems():
            self.station[name]=value

    def retrieve_book_options(self):
        login_info=self.ConfigSectionMap('GLOBAL')
        self.username = login_info['username'].strip() 
        self.password = login_info['password'].strip()
        self.brower = login_info['browser']
        book_settings = self.ConfigSectionMap('TICKET')
        self.fromStation = [ station.strip() for station in book_settings['from_station'].split(',')]
        self.toStation = [ station.strip() for station in book_settings['to_station'].split(',')]
        trains = [ train.strip() for train in book_settings['trains'].split(',')]
        if len(trains) == 1 and trains[0] == '':
            self.trains = []
        else:
            self.trains =  trains
        self.ticket_type =[ _type.strip() for _type in book_settings['ticket_type'].split(',')]
        rangeQuery = book_settings['range_query'].strip()
        if rangeQuery == 'Y':
            date = [ d.strip() for d in book_settings['date'].split(',')]
            if len(date) < 2:
                print "未设置正确的起至时间"
                return -1
            else: 
                start_date = datetime.strptime(date[0],self.date_format) 
                end_date = datetime.strptime(date[1],self.date_format) 
                if end_date < start_date:
                    print "查询截止日期不可大于开始日期!"
                    return -1
                for single_date in self.daterange(start_date, end_date): 
                    self.date.append(single_date.strftime(self.date_format))
        else:
            self.date = [ d.strip() for d in book_settings['date'].split(',')]
        if book_settings['student'].strip() == 'Y':
            self.isStudent = True
        self.tolerance = int(book_settings['tolerance'])
        self.people = [ people.strip() for people in book_settings['people'].split(',') ]
        if book_settings['alarm'].strip() == 'Y':
            print('已打开音乐提醒')
            self.playmusic = True

    def login(self):
        self.b.get(self.url)
        tag_name = u"登录"
        self.b.find_element_by_link_text(tag_name).click()
        form = self.b.find_element_by_id("loginForm")
        username = form.find_elements_by_name("loginUserDTO.user_name")[0]
        password = form.find_elements_by_name("userDTO.password")[0]
        username.send_keys(self.username)
        password.send_keys(self.password)
        import pdb
        pdb.set_trace()
    
    def page_has_loaded(self):
        #page_state = self.b.evaluate_script("document.readyState")
        #return page_state == 'complete'
        delay = 3
        try:
            myElem = WebDriverWait(self.b, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'bgc')))
            return True
        except TimeoutException:
            return False

    def switch_to_order_page(self):
        while 1:
            order = self.b.find_element_by_link_text(u"车票预订")
            if isinstance(order, webdriver.remote.webelement.WebElement):
                break
        order.click()

    def checkTicket(self, date, fromStation, toStation):
        print 'date: %s, from %s, to %s'%(date, fromStation, toStation)
        self.b.add_cookie({'name': '_jc_save_fromDate', 'value': date})
        self.b.add_cookie({'name': '_jc_save_fromStation', 'value': self.station[fromStation]})
        self.b.add_cookie({'name': '_jc_save_toStation', 'value': self.station[toStation]})
        #self.b.cookies.all()
        self.b.refresh()
        if self.isStudent:
            self.b.find_element_by_link_text(u'学生').click()
        self.b.find_element_by_link_text(u"查询").click()
        
        if self.page_has_loaded() == False:
            return ''
        all_trains = self.b.find_elements_by_xpath('//table/tbody/tr/td/a[contains(@class, "btn72")]')
        this_train = ''
        for k, train in enumerate(all_trains):
            tds = train.find_elements_by_xpath("../../td")
            if tds and len(tds) >= 10:
                if k + 1 < len(all_trains):
                    this_train = tds[0].text.split('\n')[0] 
                    if len(self.trains) != 0 and this_train not in self.trains:
                        continue
                    if self.tolerance != -1 and this_train in self.blacklist and self.blacklist[this_train] >= self.tolerance:
                        print u"%s 失败 %d 次, 跳过"%(this_train, self.blacklist[this_train])
                        continue
                for cat in self.ticket_type:
                    if cat in self.ticket_index:
                        i = self.ticket_index.index(cat)
                    else:
                        print '无效的席别信息'
                        return 0, ''
                    if tds[i].text != u'无' and tds[i].text != '--':
                        if tds[i].text != u'有':
                            print u'%s 的 %s 有余票 %s 张!'%(this_train, cat ,tds[i].text)
                        else:
                            print u'%s 的 %s 有余票若干张!'%(this_train, cat)
                        self.find_ticket = 1
                        tds[-1].click()
                        break
            if self.find_ticket:
                break
        return this_train

    def book(self, train):
        while self.page_has_loaded() == False:
            continue
        if len(self.people) == 0:
            print '没有选择乘车人!'
            return 1
        try:
            more = self.b.find_element_by_link_text(u"更多")
            more.click()
        except:
            pass
        people = self.people
        assert len(people) > 0, '至少提供一个乘客信息' 
        try:
            person=self.b.find_element_by_xpath('//ul[@id="normal_passenger_id"]/li/label[contains(text(),"%s")]'%people[0])
        except:
            print u'没找到乘客%s'%people[0]
        for p in people:
            self.b.find_element_by_xpath('//ul[@id="normal_passenger_id"]/li/label[contains(text(),"%s")]'%p).click()
            style = self.b.find_element_by_xpath('//div[@id="dialog_xsertcj"]').get_attribute('style')
            if not ('display' in style and 'none' in style):
                self.b.find_element_by_xpath('//div[@id="dialog_xsertcj"]/div/div/div/a[text()="确认"]').click()
        self.b.find_element_by_id('submitOrder_id').click()
        table = self.b.find_element_by_id('checkticketinfo_id')
        if train.startswith('G') or  train.startswith('C') or  train.startswith('D'):
            seats = table.find_element_by_id('id-seat-sel')
            seat_list = seats.find_elements_by_css_selector("div[style='display: block;']")
            for i,p in enumerate(seat_list):
                seat_id = '%d%s'%(i, self.seat_type[i % len(self.seat_type)])
                p.find_element_by_id(seat_id).click()
        table.find_element_by_id('qr_submit_id').click()
        return 1

    def ring(self):
        import pdb
        pdb.set_trace()
        pygame.mixer.pre_init(64000, -16, 2, 4096)
        pygame.init()
        pygame.display.init()
        screen=pygame.display.set_mode([300,300])
        #pygame.display.flip()
        pygame.time.delay(1000)#等待1秒让mixer完成初始化
        tracker=pygame.mixer.music.load("media/sound.ogg")
        #track = pygame.mixer.music.load("sound.ogg")
        pygame.mixer.music.play()
        # while pygame.mixer.music.get_busy():
        #pygame.time.Clock().tick(10)
        running = True
        img=pygame.image.load("media/img.jpg")
        while running:
            screen.blit(img,(0,0))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    running = False
        pygame.quit ()
        return 1
    def executor(self):
        self.login()
        self.switch_to_order_page()
        while self.success == 0:
            self.find_ticket = 0
            while self.find_ticket == 0:
                for date in self.date:
                    try:
                        self.count += 1
                        print "Try %d times" % self.count
                        for fromStation in self.fromStation:
                            for toStation in self.toStation:
                                this_train = self.checkTicket(date, fromStation, toStation)
                                if self.find_ticket:
                                    break
                            if self.find_ticket:
                                break
                        if self.find_ticket:
                            break
                    except KeyboardInterrupt:
                        self.b.find_element_by_link_text(u'退出').click()
                        sys.exit()
                    except {IOError, RuntimeError, TypeError, NameError} as e:
                        print e
                        continue
            # book ticket for target people
            self.find_ticket = 0
            while self.find_ticket == 0:
                try:
                    self.find_ticket = self.book(this_train) 
                except KeyboardInterrupt:
                    self.b.find_element_by_link_text(u'退出').click()
                    sys.exit()
                except:
                    continue
            if self.playmusic:
                self.ring()
            print "订票成功了吗?(Y/N)"
            input_var = ''
            while input_var == '':
                input_var= sys.stdin.read(1)
                if input_var == 'Y' or input_var == 'y':
                    self.success = 1
                elif input_var == 'N' or input_var == 'n':
                    if this_train in self.blacklist:
                        self.blacklist[this_train] += 1
                    else:
                        self.blacklist[this_train] = 1
                    print u"%s 失败 %d 次"%(this_train, self.blacklist[this_train])
                    self.b.get(self.url)
                    #self.b.refresh()
                else:
                    input_var = ''
                    continue
        self.b.find_element_by_link_text(u'退出').click()

if __name__ == '__main__':
    ##start login
    assert len(sys.argv) == 2, 'should provide the path of config file.'
    conf_file = sys.argv[1]
    ticket_theif = Ticket(conf_file) 
    try:
        ticket_theif.executor() 
    except KeyboardInterrupt:
        sys.exit()
