#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.http import HttpResponse
# from django.http.response import JsonResponse
from django.http import FileResponse
import urllib.parse
import xlwt
import xlrd
import uuid
import os

def get_gen_rule(file):
    wb = xlrd.open_workbook(file)
    trans_rule = {}
    greet_arr = []

    rule_sht = wb.sheet_by_index(0)
    greet_sht = wb.sheet_by_index(1)

    for row_idx in range(rule_sht.nrows):        
        idx = rule_sht.cell_value(row_idx, 0)
        if rule_sht.cell_type(row_idx, 0) == 2:
            idx = int(idx)

        #print(str(idx))
        trans_rule[str(idx)] = rule_sht.cell_value(row_idx, 1)

    for row_idx in range(greet_sht.nrows):
        greet_arr.append(greet_sht.cell_value(row_idx, 0))

    return trans_rule, greet_arr

def gen_study_analysis(raw_content, trans_rule, greet_arr):
    greet_idx = 0

    greet_content = ""
    analy_content = ""

    greet_content = greet_arr[greet_idx]

    if(greet_idx < len(greet_arr) - 1):
        greet_idx += 1
    else:
        greet_idx = 0

    raw_split = raw_content.split()

    is_first = True
    for trans in raw_split:
        if not is_first:
            analy_content += ", "

        if trans in trans_rule:
            analy_content += trans_rule[trans]
        else:
            analy_content += trans

        is_first = False

    return greet_content + ", " + analy_content

def translate_workbook_with_template(wb, rule_file):
    gwb = xlwt.Workbook(encoding='utf-8')

    trans_rule, greet_arr = get_gen_rule(rule_file)

    for sht in wb.sheet_names():
        # print(sht)
        gtb = gwb.add_sheet(sht, cell_overwrite_ok=True)

        tabl = wb.sheet_by_name(sht)
        nrow = tabl.nrows
        #print(nrow, ncol)

        for row_idx in range(nrow):
            ncol = tabl.row_len(row_idx)
            for col_idx in range(ncol):
                tcell = tabl.cell_value(row_idx, col_idx)
                if(row_idx >= 3 and col_idx == ncol - 1):
                    if tabl.cell_type(row_idx, col_idx) == 2:
                        tcell = str(int(tcell))
                    tcell = gen_study_analysis(tcell, trans_rule, greet_arr)

                gtb.write(row_idx, col_idx, tcell)

    return gwb

def gen(request):
    if request.method != 'POST':
        return HttpResponse('别闹了小朋友')

    temp = request.FILES['template']
    rule = request.FILES['rule']

    tid = str(uuid.uuid4())

    store_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'store')

    itname = os.path.join(store_dir, tid + '_' + temp.name)
    irname = os.path.join(store_dir, tid + '_' + rule.name)

    tfp = open(itname, 'wb')
    for line in temp.chunks():
        tfp.write(line)
    tfp.flush()
    tfp.close()

    rfp = open(irname, 'wb')
    for line in rule.chunks():
        rfp.write(line)
    rfp.flush()
    rfp.close()

    fname = os.path.join(store_dir, 'gen_' + tid + '_' + temp.name)

    print(fname)

    wb = translate_workbook_with_template(xlrd.open_workbook(itname), irname)
    wb.save(fname)
    
    fp = open(fname, 'rb')
    response = FileResponse(fp)
    response['Content-Type'] ='application/octet-stream'
    response['Content-Disposition'] = "attachment;filename=" + urllib.parse.quote(os.path.basename(fname))
    
    return response
