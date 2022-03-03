
from datetime import date
from sqlalchemy import null, update
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



def get_parts(
    *,
    db:Session,
):
    part_info=db.query(Part).all()
    return part_info


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
):
    log_info=db.query(Test_log).filter(Test_log.info != json.dumps("raw_file")).all()
    return log_info