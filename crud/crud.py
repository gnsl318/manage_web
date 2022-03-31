
from datetime import date
from sqlalchemy import null, update, and_
from sqlalchemy.orm import Session, load_only
from models.base import *
import datetime
import json


def create_part(
    *,
    db : Session,
    part_name:str,
    ):
    
    if db.query(Part).filter(Part.part_name == part_name).first()==None:
        new_part = Part(
            part_name = part_name,
            start_day = null,
            end_day = null,
        )
        db.add(new_part)
        db.commit()
        return new_part
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
        #db.add(new_user)
        #db.commit()
        print(new_user)
        return new_user

def get_all_user(
    *,
    db:Session,
):
    user_info = db.query(User).all()
    return user_info

def get_search_user(
    *,
    db:Session,
    name:str
):
    user_info =db.query(User).filter(User.name==name).first()
    return user_info

def get_parts(
    *,
    db:Session,
):
    part_info=db.query(Part).all()
    return part_info

def get_error_list(
    *,
    db:Session,
):
    error_info=db.query(Error_list).all()
    return error_info
def get_log(
    *,
    db:Session,
    part_id:int
):
    log_info=db.query(Test_log).filter(Test_log.part_id == part_id).all()
    return log_info

def get_log_all(
    *,
    db:Session,
    part:str,
):
    part_id = db.query(Part).filter(Part.s_class == part).first().id
    log_info=db.query(Test_log).filter(and_(Test_log.info != json.dumps("raw_file")),(Test_log.part_id==part_id)).all()
    return log_info

def get_error_all(
    *,
    db:Session,
    part:str,
):
    error_info=db.query(Error).all()

    error_dic={}
    part_id = db.query(Part).filter(Part.s_class == part).first().id
    error_dic["Success"]=len(db.query(Test_log).filter(and_(Test_log.info != json.dumps("raw_file")),(Test_log.part_id==part_id)).all())
    for error in error_info:
        error_name = db.query(Error_list).filter(Error_list.id == error.id).first()
        if error_dic:
            error_dic[error_name] +=1
        else:
            error_dic[error_name] = 1
    return json.dumps(error_dic)

def get_search_log(
    *,
    db:Session,
    part:str,
    name:str,
):
    part_id = db.query(Part).filter(Part.s_class == part).first().id
    name_id = db.query(User).filter(User.name == name).first().id
    log_info=db.query(Test_log).filter(and_(Test_log.info != json.dumps("raw_file")),(Test_log.part_id==part_id),(Test_log.user_id==name_id)).all()
    return log_info 
def get_search_error(
    *,
    db:Session,
    part:str,
    name:str,
):

    error_dic={}
    part_id = db.query(Part).filter(Part.s_class == part).first().id
    user_id = db.query(User).filter(User.name==name).first().id
    error_info=db.query(Error).filter(Error.user_id==user_id).all()
    error_dic["Success"]=len(db.query(Test_log).filter(and_(Test_log.info != json.dumps("raw_file")),(Test_log.part_id==part_id),(Test_log.user_id==user_id)).all())
    for error in error_info:
        error_name = db.query(Error_list).filter(Error_list.id == error.id).first()
        if error_dic:
            error_dic[error_name] +=1
        else:
            error_dic[error_name] = 1
    return json.dumps(error_dic)

def get_part_name(
    *,
    db:Session,
    part:str,
    name:str
): 
    return True

def get_name(
    *,
    db:Session,
    name:str,
):
    if db.query(User).filter(User.name == name).first():
        return True
    else:
        return False

def get_date_search_log(
    *,
    db:Session,
    part:str,
    name:str,
    start_date:date,
    end_date:date,
):
    part_id = db.query(Part).filter(Part.s_class == part).first().id
    name_id = db.query(User).filter(User.name == name).first().id
    log_info=db.query(Test_log).filter(and_(Test_log.info != json.dumps("raw_file")),(Test_log.part_id==part_id),(Test_log.user_id==name_id),(Test_log.work_day>=start_date),(Test_log.work_day<=end_date)).all()
    return log_info 
def get_date_search_error(
    *,
    db:Session,
    part:str,
    name:str,
    start_date:date,
    end_date:date,
):

    error_dic={}
    part_id = db.query(Part).filter(Part.s_class == part).first().id
    user_id = db.query(User).filter(User.name==name).first().id
    error_info=db.query(Error).filter(Error.user_id==user_id).all()
    error_dic["Success"]=len(db.query(Test_log).filter(and_(Test_log.info != json.dumps("raw_file")),(Test_log.part_id==part_id),(Test_log.user_id==user_id),(Test_log.work_day>=start_date),(Test_log.work_day<=end_date)).all())
    for error in error_info:
        error_name = db.query(Error_list).filter(Error_list.id == error.id).first()
        if error_dic:
            error_dic[error_name] +=1
        else:
            error_dic[error_name] = 1
    return json.dumps(error_dic)

def get_session(
    *,
    db:Session,
    email:str
): 
    user = db.query(User).filter(User.email==email).first()
    return user

def update_user_info(
    *,
    db:Session,
    employee_number:str,
    name:str,
    email:str,
    state:str,
    field:str
):
    if state==None:
        state = False
    if field==None:
        field = "미정"
    user = db.query(User).filter(User.employee_number == employee_number).first()
    user.name=name
    user.email=email
    user.state=state
    user.field=field
    #db.commit()
    return user