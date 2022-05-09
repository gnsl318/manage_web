
from datetime import date
from sqlalchemy import null, update, and_
from sqlalchemy.orm import Session, load_only
from models.base import *
import datetime
import json
import time

## 파트 생성
def create_part(
    *,
    db : Session,
    l_class:str,
    m_class:str,
    s_class:str,
    max_count:int,
    start_date:date,
    end_date:date,
    ):
    
    if db.query(Part).filter(and_((Part.s_class == s_class),(Part.l_class==l_class),(Part.m_class==m_class))).first()==None:
        new_part = Part(
            l_class=l_class,
            m_class=m_class,
            s_class=s_class,
            max_count = max_count,
            start_day=start_date,
            end_day=end_date,
            state = True,
            check_state = True,
        )
        db.add(new_part)
        db.commit()
        return new_part
    else:
        return False
## 유저 생성
def create_user(
    *,
    db : Session,
    Employee_number:str,
    Name:str,
    email:str,
    field:str
):
    
    if db.query(User).filter((User.employee_number == Employee_number)|(User.email==email)).first()==None:
        new_user = User(
            employee_number = Employee_number,
            name = Name,
            email = email,
            state = True,
            field = field
        )
        db.add(new_user)
        db.commit()
        return new_user
    else:
        return False
## 모든 유저 가져오기
def get_all_user(
    *,
    db:Session,
):
    user_info = db.query(User).order_by(User.employee_number).all()
    return user_info
## 모든 파트 가져오기
def get_all_part(
    *,
    db:Session,
):
    part_info = db.query(Part).all()
    return part_info
## 이름으로 유저 검색
def get_search_user(
    *,
    db:Session,
    name:str
):
    user_info =db.query(User).filter(User.name==name).first()
    return user_info
## 특정파트 검색
def get_search_part(
    *,
    db:Session,
    l_class:str,
    m_class:str,
    s_class:str,
):
    part_info =db.query(Part).filter(and_((Part.s_class == s_class),(Part.l_class==l_class),(Part.m_class==m_class))).first()
    return part_info
## 진행중인 파트 가져오기
def get_parts(
    *,
    db:Session,
):
    part_info=db.query(Part).filter(Part.state == True).all()
    return part_info
## 특정 파트_id로 result_file만 가져오기
def get_log(
    *,
    db:Session,
    part_id:int
):
    log_info=db.query(Logs).filter(and_(Logs.info != json.dumps("raw_file")),(Logs.part_id==part_id)).all()
    return log_info

## 특정 파트 전체 이름으로 result_file만 가져오기
def get_log_all(
    *,
    db:Session,
    l_class:str,
    m_class:str,
    s_class:str,
):  
    part_id = db.query(Part).filter(and_(Part.s_class==s_class,Part.l_class==l_class,Part.m_class==m_class)).first().id
    log_info=db.query(Logs).filter(and_((Logs.info != json.dumps("raw_file")),(Logs.part_id==part_id))).all()
    return log_info
## 특정 파트 전체 이름으로 all_log가져오기
def get_log_all_raw(
    *,
    db:Session,
    l_class:str,
    m_class:str,
    s_class:str,
):
    part_id = db.query(Part).filter(and_((Part.s_class == s_class),(Part.l_class==l_class),(Part.m_class==m_class))).first().id
    log_info=db.query(Logs).filter(Logs.part_id==part_id).all()
    return log_info
## 특정 파트 전체 이름으로 error_log 가져오기
def get_error_all(
    *,
    db:Session,
    l_class:str,
    m_class:str,
    s_class:str,
):
    error_dic={}
    part_info = db.query(Part).filter(and_((Part.s_class == s_class),(Part.l_class==l_class),(Part.m_class==m_class))).first()
    error_info=db.query(Error).filter(and_(Error.part_id==part_info.id,Error.clear_day == None)).all()
    #error_dic['Success']=len(db.query(Logs).filter(and_(Logs.info != json.dumps("raw_file"),Part.s_class == s_class,Part.l_class==l_class,Part.m_class==m_class)).all())
    for i,error in enumerate(error_info):
        error_dic[i] = [error.id,error.user.name,error.part.l_class,error.part.m_class,error.part.s_class,error.file_name,error.error.error,error.error_day]
    return error_dic
## 특정 파트 전체이름 과 유저 이름으로 result_file만 가져오기
def get_search_log(
    *,
    db:Session,
    l_class:str,
    m_class:str,
    s_class:str,
    name:str,
):
    part_id = db.query(Part).filter(and_((Part.s_class == s_class),(Part.l_class==l_class),(Part.m_class==m_class))).first().id
    name_id = db.query(User).filter(User.name == name).first().id
    log_info=db.query(Logs).filter(and_((Logs.info != json.dumps("raw_file")),(Logs.part_id==part_id),(Logs.user_id==name_id))).all()
    return log_info 
## 특정 파트 전체이름과 유저 이름으로 error_log 가져오기
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
        error_info=db.query(Error).filter(Error.clear_day != null).all()
    else:
        user_info = db.query(User).filter(User.name==name).first()
        error_info=db.query(Error).filter(and_(Error.user_id==user_info.id,Error.part_id==part_id,Error.clear_day == None)).all()
    for i,error in enumerate(error_info):
        error_dic[i] = [error.id,error.user.name,error.part.l_class,error.part.m_class,error.part.s_class,error.file_name,error.error.error,error.error_day]
    return error_dic

## 특정 유저 유무 검색
def get_name(
    *,
    db:Session,
    name:str,
):
    if db.query(User).filter(User.name == name).first():
        return True
    else:
        return False
## 특정 파트 전체이름/ 특정 날짜/ 이름 으로 result_file만 가져오기
def get_date_search_log(
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
        log_info=db.query(Logs).filter(and_(Logs.info != json.dumps("raw_file")),(Logs.part_id==part_id),(Logs.work_day>=start_date),(Logs.work_day<=end_date)).all()
    else:
        name_id = db.query(User).filter(User.name == name).first().id
        log_info=db.query(Logs).filter(and_(Logs.info != json.dumps("raw_file")),(Logs.part_id==part_id),(Logs.user_id==name_id),(Logs.work_day>=start_date),(Logs.work_day<=end_date)).all()       
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
        error_info=db.query(Error).filter(and_(Error.error_day>=start_date,Error.error_day<=end_date,Error.part_id==part_id,Error.clear_day == None)).all()
    else:
        user_id = db.query(User).filter(User.name==name).first().id
        error_info=db.query(Error).filter(and_(Error.user_id==user_id,Error.error_day>=start_date,Error.error_day<=end_date,Error.part_id==part_id,Error.clear_day != null)).all()
    for i,error in enumerate(error_info):
        error_dic[i] = [error.id,error.user.name,error.part.l_class,error.part.m_class,error.part.s_class,error.file_name,error.error.error,error.error_day]
    return error_dic
## 이메일로 유저 정보 가졍괴
def get_session(
    *,
    db:Session,
    email:str
): 
    user = db.query(User).filter(User.email==email).first()
    return user
## 유저 정보 업데이트
def update_user_info(
    *,
    db:Session,
    employee_number:str,
    name:str,
    email:str,
    state:str,
    field:str
):
    user = db.query(User).filter(User.employee_number == employee_number).first()
    user.name=name
    user.email=email
    user.state=state
    user.field=field
    db.commit()
    return user
## 파트 정보 업데이트
def update_part_info(
    *,
    db : Session,
    part_id:int,
    l_class:str,
    m_class:str,
    s_class:str,
    max_count:int,
    start_date:date,
    end_date:date,
    state:str,
    check_state:str,
):
    part = db.query(Part).filter(Part.id == part_id).first()
    part.l_class =l_class
    part.m_class = m_class
    part.s_class= s_class
    part.max_count = max_count,
    part.start_day = start_date,
    part.end_day = end_date,
    if state==None:
        state=True
    if check_state == None:
        state=True
    part.state = state
    part.check_state = check_state
    db.commit()
    return part

def update_error_info(
    *,
    db:Session,
    error_id:int,
    clear_user:str,
):
    error = db.query(Error).filter(Error.id == error_id).first()
    clear_user_id = db.query(User).filter(User.name == clear_user).first().id
    error.clear_day = date.today().strftime("%Y%m%d")
    error.clear_user_id = clear_user_id
    db.commit()
    return error