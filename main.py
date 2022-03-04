from http.client import HTTPException
from fastapi import FastAPI,Request,status, Form, Header
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from crud.crud import *
from db import session
import json
import datetime
import collections
app = FastAPI()

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

db_session = next(session.get_db())

templates = Jinja2Templates(directory="templates")
app.mount("/static",StaticFiles(directory="static"),name="static")


part_info = get_parts(db=db_session)
category={}
l_class=""
m_dic={}
m_class=""
for part in part_info:
	if l_class == part.l_class:
		if m_class == part.m_class:
			s_class_list.append(part.s_class)
			m_dic[m_class]=s_class_list
		else:
			s_class_list=[part.s_class]
			m_class=part.m_class
		m_dic[m_class]= s_class_list
		category[l_class]=m_dic
	else:
		
		if m_class == part.m_class:
			s_class_list.append(part.s_class)
			m_dic[m_class]=s_class_list
		else:
			s_class_list=[part.s_class]
			m_class=part.m_class
		m_dic[m_class]= s_class_list
		l_class=part.l_class
		category[l_class]=m_dic




@app.get("/")
async def home(request:Request):
	part_info=get_parts(db=db_session)
	data = {}
	for part in part_info:
		part_id = part.id
		log_info = get_log(db=db_session,part_id=part_id)
		work_count =0
		for log in log_info:
			if json.loads(log.info) != "raw_file":
				work_count +=1
		data[part.s_class]= int((work_count/part.max_count)*100)
	return templates.TemplateResponse('index.html',{'request':request,'data':data,'category':category})

@app.get("/chart")
async def chart(request:Request):
	return templates.TemplateResponse('charts.html',{'request':request,'category':category})

@app.get("/Abdomen")
async def Abdomen(request:Request):
	logs = get_log_all(db=db_session)
	work={}
	work_day = ""
	counter = collections.Counter()
	for log in logs:
		counter.update(json.loads(log.info))
		if work_day != log.work_day:
			work_count =1
			work_day = log.work_day
		else:
			work_count +=1
			work[log.work_day]=work_count
	label=dict(counter)
	print(label)
	print(work)
	label_list = list(label.keys())
	label_count = list(label.values())
	return templates.TemplateResponse('charts.html',{'request':request,'category':category,'label_list':label_list,'label_count':label_count})
