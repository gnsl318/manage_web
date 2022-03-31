from fastapi import FastAPI,Request, Form
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import FileResponse,RedirectResponse,Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from crud.crud import *
from db.session import *
import json
import collections
from typing import Optional
import smtplib

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key="example")


def get_db():
        db = SessionLocal()
        try:
                yield db
        except:
                db.rollback()
                raise
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
def get_user_name(user_info):
	user_name=[]
	for user in user_info:
		user_name.append(user.name)
	return user_name

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
	label,work = await label_work(part=part,name = "total")
	error = get_error_all(db=db_session,part=part)
	page_file = f"total_charts.html"
	return templates.TemplateResponse(page_file,{'request':request,'category':category,'label':label,'work':work,'error':error,'part':part})

async def label_work(**kwargs):
	if kwargs['name'] == "total":
		logs = get_log_all(db=db_session,part=kwargs['part'])
	elif kwargs['start_date'] != None and kwargs['end_date'] != None:
		logs = get_date_search_log(db=db_session,part=kwargs['part'],name=kwargs['name'],start_date=kwargs['start_date'],end_date=kwargs['end_date'])
	else:
		logs = get_search_log(db=db_session,part=kwargs['part'],name=kwargs['name'])
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


@app.post("/{part}/search")
async def search(request:Request,part:str,search_name: str = Form(...),start_date:Optional[date]=Form(None),end_date:Optional[date]=Form(None)):
	category = get_category()
	if get_name(db=db_session,name=search_name):
		data={}
		data['part']=part
		data['name']=search_name
		if start_date != None and end_date != None:
			label,work = await label_work(part=part,name=search_name,start_date=start_date,end_date=end_date)
			error = get_date_search_error(db=db_session,part=part,name=search_name,start_date=start_date,end_date=end_date)
		else:
			label,work= await label_work(part=part,name=search_name,start_date=start_date,end_date=end_date)
			error = get_search_error(db=db_session,part=part,name=search_name)
		return templates.TemplateResponse('/search_charts.html',{'request':request,'category':category,'name':search_name,'part':part,'label':label,'work':work,'error':error})
	else:
		return RedirectResponse(url=f"/{part}", status_code=302)

@app.get("/main/login")
async def login_page(request:Request):
	page_file = f"login.html"
	return templates.TemplateResponse(page_file,{'request':request})

@app.post("/main/login_check")
async def login_check(request:Request,response:Response,InputEmail: str = Form(...),InputPassword: str = Form(...)):
	smtp = smtplib.SMTP('smtp.cafe24.com',587)   # 587: 서버의 포트번호
	smtp.ehlo()
	#smtp.starttls()   # tls방식으로 접속, 그 포트번호가 587
	try:
		smtp.login(InputEmail, InputPassword)
		user_session = get_session(db=db_session,email=InputEmail)
		request.session["name"]=user_session.name
		request.session["field"]=user_session.field
		return RedirectResponse(url="/", status_code=302)
	except:
		return RedirectResponse(url=f"/main/login", status_code=302)
@app.get("/main/logout")
async def logout(request:Request):
	request.session["name"]=None
	return RedirectResponse(url="/", status_code=302)

@app.post("/main/add_user")
async def add_user(request:Request,Employee_number: str = Form(...),Name: str = Form(...),email: str = Form(...),field: str = Form(...)):
	create_user(db=db_session,Employee_number=Employee_number,Name=Name,email=email,field=field)
	return RedirectResponse(url="/", status_code=302)

@app.get("/main/change_info")
async def change_info(request:Request):
	page_file = f"change_user.html"
	user_info=get_all_user(db=db_session)
	user_name = get_user_name(user_info)
	return templates.TemplateResponse(page_file,{'request':request,'user_name':user_name})

@app.post("/main/change_info_search")
async def change_info_search(request:Request,name: str = Form(None)):
	page_file = f"change_user.html"
	user_info=get_all_user(db=db_session)
	user_name = get_user_name(user_info)
	user = get_search_user(db=db_session,name=name)
	if user:
		return templates.TemplateResponse(page_file,{'request':request,'user_name':user_name,'employee_number':user.employee_number,'name':user.name,'email':user.email,'state':user.state,'field':user.field})
	else:
		return RedirectResponse(url="/main/change_info")

	
@app.post("/main/change")
async def change(request:Request,employee_number: str = Form(...),name: str = Form(...),email: str = Form(...),state: str = Form(None),field: str = Form(None)):
	try:
		update_user_info(db=db_session,employee_number=employee_number,name=name,email=email,state=state,field=field)
		return RedirectResponse(url="/", status_code=302)
	except:
		return RedirectResponse(url="/main/change_info")
