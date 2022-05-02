from fastapi import FastAPI,Request, Form,status
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
import pandas as pd
import time
from routers import checker
from func import *

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(checker.router)
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key="example")


db_session = next(get_db())

templates = Jinja2Templates(directory="templates")
app.mount("/static",StaticFiles(directory="static"),name="static")

@app.get("/favicon.ico")
async def favicon():
	return FileResponse(os.path.join(os.getcwd(),"static/img/logo.ico"))




@app.get("/")
async def home(request:Request):
	request.session["check"]=False
	category = get_category()
	part_info=get_parts(db=db_session)
	data = {}
	mean = {}

	for part in part_info:
		part_id = part.id
		log_info = get_log(db=db_session,part_id=part_id)
		day_work={}
		total_count = 0
		for log in log_info:
			try:
				day_work[log.work_day] +=1
			except:
				day_work[log.work_day] =1
		if len(day_work) != 0:
			mean[f"{part.l_class}-{part.m_class}-{part.s_class}"]=str(int(sum(day_work.values())/len(day_work.keys())))
		else:
			mean[f"{part.l_class}-{part.m_class}-{part.s_class}"]=str(0)
		total_count=sum(day_work.values())
		data[f"{part.l_class}-{part.m_class}-{part.s_class}"]= int((total_count/part.max_count)*100)
	return templates.TemplateResponse('index.html',{'request':request,'data':data,'category':category,'bar_data':json.dumps(mean)})



@app.get("/{part}")
async def part(request:Request,part:str):
	category = get_category()
	l_class = part.split("-")[0]
	m_class = part.split("-")[1]
	s_class = part.split("-")[-1]
	label,work = label_work(l_class=l_class,m_class=m_class,s_class=s_class,name = "total")
	error = get_error_all(db=db_session,l_class=l_class,m_class=m_class,s_class=s_class)
	page_file = f"total_charts.html"
	return templates.TemplateResponse(page_file,{'request':request,'category':category,'bar_data':label,'work':work,'error':error,'l_class':l_class,'m_class':m_class,'s_class':s_class})



@app.get('/{part}/search')
async def serch(request:Request,part:str):
	return RedirectResponse(url=f"/{part}", status_code=302)
@app.post("/{part}/search")
async def search(request:Request,part:str,search_name: str = Form(None),start_date:Optional[date]=Form(None),end_date:Optional[date]=Form(None)):
	category = get_category()
	data={}
	l_class = part.split("-")[0]
	m_class = part.split("-")[1]
	s_class = part.split("-")[-1]
	data['part']=f"{l_class}-{m_class}-{s_class}"
	if search_name!=None:
		if get_name(db=db_session,name=search_name):	
			data['name']=search_name
			if start_date != None and end_date != None:
				label,work = label_work(l_class=l_class,m_class=m_class,s_class=s_class,name=search_name,start_date=start_date,end_date=end_date)
				error = get_date_search_error(db=db_session,l_class=l_class,m_class=m_class,s_class=s_class,name=search_name,start_date=start_date,end_date=end_date)
			else:
				if start_date == None:
					start_date == datetime.date(2022,3,1).strftime("%Y-%m-%d")
				if end_date == None:
					end_date = datetime.date.today().strftime("%Y-%m-%d")
				label,work= label_work(l_class=l_class,m_class=m_class,s_class=s_class,name=search_name,start_date=start_date,end_date=end_date)
				error = get_search_error(db=db_session,l_class=l_class,m_class=m_class,s_class=s_class,name=search_name)
			return templates.TemplateResponse('/search_charts.html',{'request':request,'category':category,'name':search_name,'l_class':l_class,'m_class':m_class,'s_class':s_class,'bar_data':label,'work':work,'error':error})
		else:
			return RedirectResponse(url=f"/{part}", status_code=302)
	else:
		if start_date != None and end_date != None:
			label,work = label_work(l_class=l_class,m_class=m_class,s_class=s_class,name="term",start_date=start_date,end_date=end_date)
			error = get_date_search_error(db=db_session,l_class=l_class,m_class=m_class,s_class=s_class,name="term",start_date=start_date,end_date=end_date)
		else:
			if start_date == None:
				start_date = datetime.date(2022,3,1)
			if end_date == None:
				end_date = datetime.date.today().strftime("%Y-%m-%d")
			label,work= label_work(l_class=l_class,m_class=m_class,s_class=s_class,name="term",start_date=start_date,end_date=end_date)
			error = get_search_error(db=db_session,l_class=l_class,m_class=m_class,s_class=s_class,name="term")
		search_name =f"{start_date}~{end_date}"
		data['name'] = search_name
		print(error)
		return templates.TemplateResponse('/search_charts.html',{'request':request,'category':category,'name':search_name,'l_class':l_class,'m_class':m_class,'s_class':s_class,'bar_data':label,'work':work,'error':error})

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
	request.session.clear()

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

	
@app.post("/main/change_info_do")
async def change_user(request:Request,employee_number: str = Form(...),name: str = Form(...),email: str = Form(...),state: bool = Form(None),field: str = Form(None)):
	try:
		update_user_info(db=db_session,employee_number=employee_number,name=name,email=email,state=state,field=field)
		return RedirectResponse(url="/", status_code=302)
	except:
		return RedirectResponse(url="/main/change_info", status_code=302)

@app.post("/main/add_project")
async def add_project(request:Request,l_class: str = Form(...),m_class: str = Form(...),s_class: str = Form(...),max_count:int=Form(...),start_date: date = Form(...),end_date: date = Form(...)):
	create_part(db=db_session,l_class=l_class,m_class=m_class,s_class=s_class,max_count=max_count,start_date=start_date,end_date=end_date)
	return RedirectResponse(url="/", status_code=302)

@app.get("/main/change_part")
async def change_info(request:Request):
	page_file = f"change_project.html"
	part_info=get_all_part(db=db_session)
	part_l_class,part_m_class,part_s_class = get_part_name(part_info)
	return templates.TemplateResponse(page_file,{'request':request,'part_l_class':part_l_class,'part_m_class':part_m_class,'part_s_class':part_s_class})

@app.post("/main/change_part_search")
async def change_info_search(request:Request,l_class: str = Form(...),m_class: str = Form(...),s_class: str = Form(...)):

	page_file = f"change_project.html"
	part_info=get_all_part(db=db_session)
	part_l_class,part_m_class,part_s_class = get_part_name(part_info)
	part = get_search_part(db=db_session,l_class=l_class,m_class=m_class,s_class=s_class)
	try:
		if part:
			request.session["part.id"]=part.id
			return templates.TemplateResponse(page_file,{'request':request,'part_l_class':part_l_class,'part_m_class':part_m_class,'part_s_class':part_s_class,'l_class':part.l_class,'m_class':part.m_class,'s_class':part.s_class,'max_count':part.max_count,'start_date':part.start_day,'end_date':part.end_day,'state':part.state,'check_state':part.check_state})
		else:
			return RedirectResponse(url="/main/change_part", status_code=302)
	except:
		return RedirectResponse(url="/main/change_part", status_code=302)

	
@app.post("/main/change_part_do")
async def change_part(request:Request,l_class: str = Form(...),m_class: str = Form(...),s_class: str = Form(...),max_count:int=Form(...),start_date: date = Form(...),end_date: date = Form(...),state:bool = Form(None),check_state:bool = Form(None)):
	try:
		update_part_info(db=db_session,part_id=request.session["part.id"],l_class=l_class,m_class=m_class,s_class=s_class,max_count=max_count,start_date=start_date,end_date=end_date,state=state,check_state=check_state)
		return RedirectResponse(url="/", status_code=302)
	except:
		return RedirectResponse(url="/main/change_part")

@app.post("/main/check_error")
async def change_error(request:Request,error_id:str = Form(None)):
	if error_id ==None:
		pass
	else:
		update_error_info(db=db_session,error_id=error_id,clear_user=request.session["name"])
	return RedirectResponse(url="/", status_code=302)


@app.get("/download/{part}")
def dwonload_file(request:Request,part:str):
	if request.session["check"]:
		if part == "all":
			file_name=f"Check_all_log"
			workbook = xlsxwriter.Workbook(f"{os.getcwd()}/file/{file_name}.xlsx")
			part_list=get_check_parts(db=db_session)
			for part in part_list:
				l_class = part.l_class
				m_class = part.m_class
				s_class = part.s_class
				ws = workbook.add_worksheet(f"{l_class}-{m_class}-{s_class}")
				make_df(db=db_session,l_class=l_class,m_class=m_class,s_class=s_class,ws=ws)
		else:
			file_name=f"Check_{part}_log"
			l_class = part.split("-")[0]
			m_class = part.split("-")[1]
			s_class = part.split("-")[-1]
			workbook = xlsxwriter.Workbook(f"{os.getcwd()}/file/{file_name}.xlsx")
			ws = workbook.add_worksheet(f"{l_class}-{m_class}-{s_class}")
			make_df(db=db_session,l_class=l_class,m_class=m_class,s_class=s_class,ws=ws)
	else:
		if part == "all":
			file_name=f"all_log"
			workbook = xlsxwriter.Workbook(f"{os.getcwd()}/file/{file_name}.xlsx")
			part_list=get_parts(db=db_session)
			for part in part_list:
				l_class = part.l_class
				m_class = part.m_class
				s_class = part.s_class
				ws = workbook.add_worksheet(f"{l_class}-{m_class}-{s_class}")
				make_df(db=db_session,l_class=l_class,m_class=m_class,s_class=s_class,ws=ws)
		else:
			file_name=f"{part}_log"
			l_class = part.split("-")[0]
			m_class = part.split("-")[1]
			s_class = part.split("-")[-1]
			workbook = xlsxwriter.Workbook(f"{os.getcwd()}/file/{file_name}.xlsx")
			ws = workbook.add_worksheet(f"{l_class}-{m_class}-{s_class}")
			make_df(db=db_session,l_class=l_class,m_class=m_class,s_class=s_class,ws=ws)
	workbook.close()
	file_path=os.path.join(os.getcwd(),f"file/{file_name}.xlsx")
	return FileResponse(path=file_path,media_type='application/octet-stream',filename=f"{file_name}_{datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}.xlsx")

    