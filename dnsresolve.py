import dns.resolver
import threadpool
import threading
import os
import sys
import math
import configparser


config = configparser.SafeConfigParser()

if(not os.path.exists('./config.ini')):
    configfile = open('config.ini','w')
    config.add_section('FILES')
    config.set('FILES','DOMAIN_LIST','')
    config.set('FILES','IPSET_OUT','')
    config.set('FILES','ERR_LOG','')
    config.add_section('CONFIG')
    config.set('CONFIG','THREAD','')
    config.set('CONFIG','DNS','')
    config.set('CONFIG','PORT','')
    config.write(configfile)
    configfile.close()
    print('The config.ini is initialized!\nPlease CONFIG and RESTART!')
    os.system('pause')
    exit

config.read('./config.ini')

#线程数，越高速度越快，但是解析失败率越高
THREAD=config.getint('CONFIG','THREAD')
#域名列表
DOMAIN_LIST=config.get('FILES','DOMAIN_LIST')
#输出的IP地址列表
IPSET_OUT=config.get('FILES','IPSET_OUT')
#错误日志
ERR_LOG=config.get('FILES','ERR_LOG')

#DNS地址
DNS=config.get('CONFIG','DNS')
#端口号
PORT=config.getint('CONFIG','PORT')

domainlist = open(DOMAIN_LIST,'r')
result = open(IPSET_OUT,'w')
err_log = open(ERR_LOG,'w')
task_pool=threadpool.ThreadPool(THREAD)
request_list=[]
my_resolver = dns.resolver.Resolver()
my_resolver.nameservers = [DNS]
my_resolver.port = PORT
mutex = threading.Lock()
global total
global cur

def DomainQuery(domain):
    global total
    global cur
    try:
        answer = my_resolver.query(domain)
        mutex.acquire()
        for host in answer:
            print(host.address)
            result.write(host.address+'\n')
        os.system("title Process: %d/%d"%(cur,total))
        cur=cur+1
        mutex.release()
        return
    except Exception as err:
        mutex.acquire()
        print(err)
        err_log.write(str(err)+'\n')
        os.system("title Process: %d/%d"%(cur,total))
        cur += 1
        mutex.release()

data = [domain.strip() for domain in domainlist]
request_list = threadpool.makeRequests(DomainQuery,data)
total=len(data)
cur=0

for req in request_list:
    task_pool.putRequest(req)

task_pool.wait()
domainlist.close()
result.close()
err_log.close()
os.system("pause")