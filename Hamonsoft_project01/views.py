from django.shortcuts import render, redirect
from .models import Test1

from django.views import generic
from django.views import View

import pymysql
import os
import multiprocessing
from functools import partial

class Project_main(generic.TemplateView):
    def get(self, request, *args, **kwargs):
        template_name = 'project_1/index.html'
        return render(request, template_name)

class Show_list(generic.TemplateView):
    def get(self, request, *args, **kwargs):
        template_name = 'project_1/common/show_list.html'
        test1_list = Test1.objects.all()
        return render(request, template_name, {"test1_list" : test1_list})

def getInsert(rows, ip_list):
    for i in ip_list:
        for j in rows:
            if '/udp' in j:
                port_result = getNmap('-sU', j[:-4], i)
            else:
                port_result = getNmap('-sT', j[:-4], i)

            if port_result is None:
                continue

            connectDBInsert(i, port_result)

def getIpAddressList(num):
    command = "nmap -sn" + " 10.1." + num + ".1/24"
    #command = "nmap -sn" + " 10.1." + num + ".1-10"
    process = os.popen(command)
    results = str(process.read())
    arr = results.splitlines()

    real_arr = []
    for a in arr:
        if a.startswith("Nmap scan report for "):
            if a.endswith('10.1.1.209'):
                continue
            real_arr.append(a.split()[4])
    return real_arr

def getNmap(options, port_num, ip_address):
    command = "nmap -T5 " + options + " -p " + port_num + " " + ip_address
    process = os.popen(command)
    results = str(process.read())
    arr = results.splitlines()

    for a in arr:
        if 'tcp' in a or 'udp' in a:
            return a

def connectDBInsert(ip_address, x):
    conn = pymysql.connect(host='localhost', port=3306,
                           user='user', passwd='1234', db='test', charset='utf8')
    cursor = conn.cursor()

    x_arr = x.split()

    #udp's open : open|filtered , tdp's open : open
    if x_arr[1] == 'open' or x_arr[1] == 'open|filtered':
        state = 1
    elif x_arr[1] == 'closed':
        state = 0
    else:
        state = -1

    sql = """INSERT INTO test1(ip, port_num, state) values (%s, %s, %s)"""
    cursor.execute(sql, (ip_address, x_arr[0], state))
    conn.commit()

    cursor.close()
    conn.close()

def main(request):
    conn = pymysql.connect(host='localhost', port=3306,
                           user='user', passwd='1234', db='test', charset='utf8')
    cursor = conn.cursor()

    sql = """SELECT * FROM port1"""
    cursor.execute(sql)

    rows = [item[0] for item in cursor.fetchall()]

    cursor.close()
    conn.close()

    num = ['0', '1', '2', '3']

    pool = multiprocessing.Pool(processes=4)
    ip_list_total = pool.map(getIpAddressList, num)
    pool.close()
    pool.join()

    pool = multiprocessing.Pool(processes=4)
    func = partial(getInsert, rows)
    pool.map(func, ip_list_total)
    pool.close()
    pool.join()

    template_name = 'project_1/common/show_list.html'
    test1_list = Test1.objects.all()
    return render(request, template_name, {"test1_list" : test1_list})