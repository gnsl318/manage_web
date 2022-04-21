import os
from db.session import *
from crud.crud import *
from crud.check_crud import *
import collections
import pandas as pd
import time
import xlsxwriter
db_session = next(get_db())


def get_category(check=None):
    if check==None:
        part_info = get_parts(db=db_session)
    elif check == "check":
        part_info = get_check_parts(db=db_session)
    category={}
    l_class = ""
    m_class = ""
    for part in part_info:
        if l_class != part.l_class:
            l_class = part.l_class
            m_dic={}	
            if m_class != part.m_class:
                m_class = part.m_class
                s_class_list = [part.s_class]
                m_dic[m_class]=s_class_list
            else:
                s_class_list.append(part.s_class)
                m_dic[m_class]=s_class_list
        else:
            if m_class != part.m_class:
                m_class = part.m_class
                s_class_list = [part.s_class]
                m_dic[m_class]=s_class_list
            else:
                s_class_list.append(part.s_class)
                m_dic[m_class]=s_class_list
        category[l_class]=m_dic
    return category
def get_user_name(user_info):
	user_name=[]
	for user in user_info:
		user_name.append(user.name)
	return user_name

def get_part_name(part_info):
	part_l_class=[]
	part_m_class=[]
	part_s_class=[]
	for part in part_info:
		part_l_class.append(part.l_class)
		part_m_class.append(part.m_class)
		part_s_class.append(part.s_class)
	return list(set(part_l_class)),list(set(part_m_class)),sorted(list(set(part_s_class)))

def label_work(**kwargs):
    try:
        if kwargs['check'] == 'check':
            if kwargs['name'] == "total":
                logs = get_check_log_all(db=db_session,l_class=kwargs["l_class"],m_class=kwargs["m_class"],s_class=kwargs["s_class"])
            elif kwargs['start_date'] != None and kwargs['end_date'] != None:
                logs = get_date_search_check_log(db=db_session,l_class=kwargs["l_class"],m_class=kwargs["m_class"],s_class=kwargs["s_class"],name=kwargs['name'],start_date=kwargs['start_date'],end_date=kwargs['end_date'])
            else:
                logs = get_search_check_log(db=db_session,l_class=kwargs["l_class"],m_class=kwargs["m_class"],s_class=kwargs["s_class"],name=kwargs['name'])
    except:
        if kwargs['name'] == "total":
            logs = get_log_all(db=db_session,l_class=kwargs["l_class"],m_class=kwargs["m_class"],s_class=kwargs["s_class"])
        elif kwargs['start_date'] != None and kwargs['end_date'] != None:
            logs = get_date_search_log(db=db_session,l_class=kwargs["l_class"],m_class=kwargs["m_class"],s_class=kwargs["s_class"],name=kwargs['name'],start_date=kwargs['start_date'],end_date=kwargs['end_date'])
        else:
            logs = get_search_log(db=db_session,l_class=kwargs["l_class"],m_class=kwargs["m_class"],s_class=kwargs["s_class"],name=kwargs['name'])
    counter = collections.Counter()
    work={}
    for log in logs:
        if log.info != json.dumps("raw_file"):
            counter.update(json.loads(log.info))
            log_work_day = log.work_day.strftime("%Y-%m-%d")
            try:
                work[log_work_day] +=1
            except:
                work[log_work_day] = 1
    label = dict(sorted(dict(counter).items()))
    return json.dumps(label),json.dumps(work)

def make_df(db,l_class,m_class,s_class,ws,check=None):
    if check==None:
        logs = get_log_all_raw(db=db_session,l_class=l_class,m_class=m_class,s_class=s_class)
    else:
        logs = get_check_log_all_raw(db=db_session,l_class=l_class,m_class=m_class,s_class=s_class)
    headers = ["Name","Date","Raw","Result","Label_total","Label"]
    for i,header in enumerate(headers):
        ws.write(0,i,header)
    dic ={}
    for log in logs:
        data = json.loads(log.info)
        user_name = log.user.name
        work_day = log.work_day
        try:
            if dic[f"{user_name}_{work_day}"]:
                pass
        except:
            dic[f"{user_name}_{work_day}"]=[0,0,0,{}]
        if data == "raw_file":
            dic[f"{user_name}_{work_day}"][0] +=1
        else:
            dic[f"{user_name}_{work_day}"][1] +=1
            labels = 0
            for label,label_count in data.items():
                labels +=label_count
                try:
                    dic[f"{user_name}_{work_day}"][3][label] += label_count
                except:
                    dic[f"{user_name}_{work_day}"][3][label] = label_count
            dic[f"{user_name}_{work_day}"][2] += labels
    row = 1
    for k,v in dic.items():
        ws.write(row,0,k.split("_")[0])
        ws.write(row,1,k.split("_")[1])
        ws.write(row,2,v[0])
        ws.write(row,3,v[1])
        ws.write(row,4,v[2])
        col=5
        v[3] = dict(sorted(dict(v[3]).items()))
        for label,label_count in v[3].items():
            ws.write(row,col,f"{label}:{label_count}")
            col+=1
        row+=1
    return ws

    
