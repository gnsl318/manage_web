from http.client import HTTPException
from fastapi import FastAPI,Request,status, Form, Header,Response
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from crud.crud import *
from db.session import *
import json
import datetime
import collections
from fastapi import Depends
from typing import Generator

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


db_session = next(get_db())

templates = Jinja2Templates(directory="templates")
app.mount("/static",StaticFiles(directory="static"),name="static")

@app.get("/favicon.ico")
async def favicon():
	return FileResponse(os.path.join(os.getcwd(),"static/img/logo.ico"))

def get_category():
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
	return category




@app.get("/")
async def home(request:Request):
	category = get_category()
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

@app.get("/{part}")
async def part(request:Request,part:str):
	category = get_category()
	label,work = await label_work()
	error = get_error_all(db=db_session)
	page_file = f"{part}_charts.html"
	return templates.TemplateResponse(page_file,{'request':request,'category':category,'label':label,'work':work,'error':error})

async def label_work():
	logs = get_log_all(db=db_session)
	counter = collections.Counter()
	for log in logs:
		counter.update(json.loads(log.info))
	label = dict(sorted(dict(counter).items()))
	work={}
	work_day = ""
	for log in logs:
		log_work_day = log.work_day.strftime("%Y-%m-%d")
		if work_day != log_work_day:
			work_count =1
			work_day = log_work_day
		else:
			work_count +=1
		work[log_work_day]=str(work_count)
	return json.dumps(label),json.dumps(work)


# @app.get("/{part}/{data}/")
# async def data(part:str,data:str):
# 	label = await label_work(data)
# 	return label

# @app.get("/{part}/error")
# async def error(part:str):
# 	error = get_error_all(db=db_session)
# 	return error

@app.post("/search")
async def search(request:Request,search_name: str = Form(...)):
	category = get_category()
	part = str(request.url).split("/")[-2]
	print(part)
	data={}
	data['part']=part
	data['name']=search_name
	return templates.TemplateResponse('search_charts.html',{'request':request,'category':category,'data':data})

@app.get("/{part}/search/{name}")
async def search_name(part:str,name:str):
	info = get_part_name(db=db_session,part=part,name=name)
