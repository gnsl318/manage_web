
from datetime import date
from sqlalchemy import null, update, and_
from sqlalchemy.orm import Session, load_only
from models.base import *
import datetime
import json
## 특정 파트_id로 chekc_log / result_file만 가져오기
def get_check_log(
    *,
    db:Session,
    part_id:int
):
    log_info=db.query(Check_Logs).filter(and_(Check_Logs.info != json.dumps("raw_file")),(Check_Logs.part_id==part_id)).all()
    return log_info

def get_check_parts(
    *,
    db:Session,
):
    part_info=db.query(Part).filter(and_(Part.state == True,Part.check_state == True)).all()
    return part_info
def get_check_log_all(
    *,
    db:Session,
    l_class:str,
    m_class:str,
    s_class:str,
):  
    part_id = db.query(Part).filter(and_(Part.s_class==s_class,Part.l_class==l_class,Part.m_class==m_class)).first().id
    log_info=db.query(Check_Logs).filter(and_((Check_Logs.info != json.dumps("raw_file")),(Check_Logs.part_id==part_id))).all()
    return log_info
def get_search_check_log(
    *,
    db:Session,
    l_class:str,
    m_class:str,
    s_class:str,
    name:str,
):
    part_id = db.query(Part).filter(and_((Part.s_class == s_class),(Part.l_class==l_class),(Part.m_class==m_class))).first().id
    name_id = db.query(User).filter(User.name == name).first().id
    log_info=db.query(Check_Logs).filter(and_((Check_Logs.info != json.dumps("raw_file")),(Check_Logs.part_id==part_id),(Check_Logs.user_id==name_id))).all()
    return log_info 

## 특정 파트 전체이름/ 특정 날짜/ 이름 으로 result_file만 가져오기
def get_date_search_check_log(
    *,
    db:Session,
    l_class:str,
    m_class:str,
    s_class:str,
    name:str,
    start_date:date,
    end_date:date,
):
    part_id = db.query(Part).filter(and_((Part.s_class == s_class),(Part.l_class==l_class),(Part.m_class==m_class))).first().id
    if name =="term":
        log_info=db.query(Check_Logs).filter(and_(Check_Logs.info != json.dumps("raw_file")),(Check_Logs.part_id==part_id),(Check_Logs.work_day>=start_date),(Check_Logs.work_day<=end_date)).all()
    else:
        name_id = db.query(User).filter(User.name == name).first().id
        log_info=db.query(Check_Logs).filter(and_(Check_Logs.info != json.dumps("raw_file")),(Check_Logs.part_id==part_id),(Check_Logs.user_id==name_id),(Check_Logs.work_day>=start_date),(LoCheck_Logsgs.work_day<=end_date)).all()       
    return log_info 
## 특정 파트 전체이름/ 특정 날짜/ 이름 으로 error_log만 가져오기
def get_date_search_check_error(
    *,
    db:Session,
    l_class:str,
    m_class:str,
    s_class:str,
    name:str,
    start_date:date,
    end_date:date,
):
    error_dic={}
    part_id = db.query(Part).filter(and_((Part.s_class == s_class),(Part.l_class==l_class),(Part.m_class==m_class))).first().id
    if name =="term":
        error_info=db.query(Error).all()
        error_dic["Success"]=len(db.query(Check_Logs).filter(and_(Check_Logs.info != json.dumps("raw_file")),(Check_Logs.part_id==part_id),(Check_Logs.work_day>=start_date),(Check_Logs.work_day<=end_date)).all())
    else:
        user_id = db.query(User).filter(User.name==name).first().id
        error_info=db.query(Error).filter(Error.user_id==user_id).all()
        error_dic["Success"]=len(db.query(Check_Logs).filter(and_(Check_Logs.info != json.dumps("raw_file")),(Check_Logs.part_id==part_id),(Check_Logs.user_id==user_id),(Check_Logs.work_day>=start_date),(Check_Logs.work_day<=end_date)).all())
    for error in error_info:
        error_name = db.query(Error_list).filter(Error_list.id == error.id).first()
        if error_dic:
            error_dic[error_name] +=1
        else:
            error_dic[error_name] = 1
    return json.dumps(error_dic)