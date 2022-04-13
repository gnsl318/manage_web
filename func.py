import os
from db.session import *
from crud.crud import *
from crud.check_crud import *
import collections
import pandas as pd
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

def make_df(db,l_class,m_class,s_class,writer,check=None):
    if check==None:
        logs = get_log_all_raw(db=db_session,l_class=l_class,m_class=m_class,s_class=s_class)
    else:
        logs = get_check_log_all_raw(db=db_session,l_class=l_class,m_class=m_class,s_class=s_class)
    dic_count={}
    dic_label={}
    dic_raw={}
    counter = collections.Counter()
    for log in logs:
        data = json.loads(log.info)
        if data == "raw_file":
            try:
                dic_raw[f"{log.user.name}/{log.work_day}"] +=1
            except:
                dic_raw[f"{log.user.name}/{log.work_day}"] =1
        else:
            counter.update(json.loads(log.info))
            try:
                dic_count[f"{log.user.name}/{log.work_day}"] +=1
            except:
                dic_count[f"{log.user.name}/{log.work_day}"] =1
            labels = 0
            for label_count in data.values():
                labels +=label_count
            try:
                dic_label[f"{log.user.name}/{log.work_day}"] +=labels
            except:
                dic_label[f"{log.user.name}/{log.work_day}"] =labels
    name_list=[]
    date_list=[]
    count_list =[]
    label_list=[]
    raw_list=[]
    label = dict(sorted(dict(counter).items()))
    for key,value in dic_raw.items():
        name_list.append(key.split("/")[0])
        date_list.append(key.split("/")[-1])
        count_list.append(dic_count[key])
        label_list.append(dic_label[key])
        raw_list.append(dic_raw[key])
    df = pd.DataFrame()
    df["name"]= name_list
    df["date"] = date_list
    df["raw_count"] = raw_list
    df["work_count"] = count_list
    df["label_total_count"] = label_list
    df["label"]= pd.Series(list(label.keys()))
    df["label_count"]=pd.Series(list(label.values()))
    df.to_excel(writer,sheet_name=f"{l_class}-{m_class}-{s_class}",index=False)