
from datetime import date
from sqlalchemy import null, update, and_
from sqlalchemy.orm import Session, load_only
from models.base import *
import datetime
import json
## 특정 파트_id로 check_log / result_file만 가져오기
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

## 특정 파트 전체 이름으로 error_log 가져오기
def get_check_error_all(
    *,
    db:Session,
    l_class:str,
    m_class:str,
    s_class:str,
):
    error_dic={}
    part_info = db.query(Part).filter(and_((Part.s_class == s_class),(Part.l_class==l_class),(Part.m_class==m_class))).first()
    error_info=db.query(Check_Error).filter(and_(Check_Error.part_id==part_info.id,Check_Error.clear_day == None)).all()
    #error_dic['Success']=len(db.query(Logs).filter(and_(Logs.info != json.dumps("raw_file"),Part.s_class == s_class,Part.l_class==l_class,Part.m_class==m_class)).all())
    for i,error in enumerate(error_info):
        error_dic[i] = [error.id,error.user.name,error.part.l_class,error.part.m_class,error.part.s_class,error.file_name,error.error.error,error.error_day]
    return error_dic

def get_search_error(
    *,
    db:Session,
    l_class:str,
    m_class:str,
    s_class:str,
    name:str,
):

    error_dic={}
    part_id = db.query(Part).filter(and_((Part.s_class == s_class),(Part.l_class==l_class),(Part.m_class==m_class))).first().id
    if name =="term":
        error_info=db.query(Check_Error).filter(Check_Error.clear_day == None).all()
    else:
        user_info = db.query(User).filter(User.name==name).first()
        error_info=db.query(Check_Error).filter(and_(Check_Error.user_id==user_info.id,Check_Error.part_id==part_id,Check_Error.clear_day == None)).all()
    for i,error in enumerate(error_info):
        error_dic[i] = [error.id,error.user.name,error.part.l_class,error.part.m_class,error.part.s_class,error.file_name,error.error.error,error.error_day]
    return error_dic

## 특정 파트 전체이름 과 유저 이름으로 result_file만 가져오기
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
        log_info=db.query(Check_Logs).filter(and_(Check_Logs.info != json.dumps("raw_file")),(Check_Logs.part_id==part_id),(Check_Logs.user_id==name_id),(Check_Logs.work_day>=start_date),(Check_Logs.work_day<=end_date)).all()       
    return log_info 
## 특정 파트 전체이름/ 특정 날짜/ 이름 으로 error_log만 가져오기
def get_date_search_error(
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
        error_info=db.query(Check_Error).filter(and_(Check_Error.error_day>=start_date,Check_Error.error_day<=end_date,Check_Error.part_id==part_id,Check_Error.clear_day == None)).all()
    else:
        user_id = db.query(User).filter(User.name==name).first().id
        error_info=db.query(Check_Error).filter(and_(Check_Error.user_id==user_id,Check_Error.error_day>=start_date,Check_Error<=end_date,Check_Error.part_id==part_id,Check_Error.clear_day != null)).all()
    for i,error in enumerate(error_info):
        error_dic[i] = [error.id,error.user.name,error.part.l_class,error.part.m_class,error.part.s_class,error.file_name,error.error.error,error.error_day]
    return error_dic


## 특정 파트 전체 이름으로 all_log가져오기
def get_check_log_all_raw(
    *,
    db:Session,
    l_class:str,
    m_class:str,
    s_class:str,
):
    part_id = db.query(Part).filter(and_((Part.s_class == s_class),(Part.l_class==l_class),(Part.m_class==m_class))).first().id
    log_info=db.query(Check_Logs).filter(Check_Logs.part_id==part_id).all()
    return log_info

def update_check_error_info(
    *,
    db:Session,
    error_id:int,
    clear_user:str,
):
    error = db.query(Check_Error).filter(Check_Error.id == error_id).first()
    clear_user_id = db.query(User).filter(User.name == clear_user).first().id
    error.clear_day = date.today().strftime("%Y%m%d")
    error.clear_user_id = clear_user_id
    db.commit()
    return error