from fastapi import APIRouter,Request,Form
from starlette.responses import FileResponse,RedirectResponse,Response
from fastapi.templating import Jinja2Templates
from typing import Optional
import os
from func import *
from db.session import *
from crud.crud import *
from crud.check_crud import *



router = APIRouter(
    prefix="/checker",
    tags=["checker"]
)
db_session = next(get_db())
templates = Jinja2Templates(directory="templates")

@router.get("/")
async def re_home(request:Request):
    return RedirectResponse(url=f"/checker/main", status_code=302)
@router.get("/main")
async def home(request:Request):
	request.session["check"]=True
	category = get_category(check="check")
	part_info=get_check_parts(db=db_session)
	data = {}
	mean = {}
	for part in part_info:
		part_id = part.id
		log_info = get_check_log(db=db_session,part_id=part_id)
		day_work={}
		total_count = 0
		for log in log_info:
			try:
				day_work[log.work_day] +=1
			except:
				day_work[log.work_day] =1
		if len(day_work) != 0:
			mean[f"{part.m_class}-{part.s_class}"]=str(int(sum(day_work.values())/len(day_work.keys())))
		else:
			mean[f"{part.m_class}-{part.s_class}"]=str(0)
		total_count=sum(day_work.values())
		data[f"{part.m_class}-{part.s_class}"]= int((total_count/part.max_count)*100)
	return templates.TemplateResponse('index.html',{'request':request,'data':data,'category':category,'bar_data':json.dumps(mean)})

@router.get("/{part}")
async def part(request:Request,part:str):
	category = get_category(check="check")
	l_class = part.split("-")[0]
	m_class = part.split("-")[1]
	s_class = part.split("-")[-1]
	label,work = label_work(l_class=l_class,m_class=m_class,s_class=s_class,name = "total",check="check")
	error = get_check_error_all(db=db_session,l_class=l_class,m_class=m_class,s_class=s_class)
	page_file = f"total_charts.html"
	request.session['part']=part
	return templates.TemplateResponse(page_file,{'request':request,'category':category,'bar_data':label,'work':work,'error':error,'l_class':l_class,'m_class':m_class,'s_class':s_class})



@router.get('/{part}/search')
async def serch(request:Request,part:str):
	return RedirectResponse(url=f"/chekcer/{part}", status_code=302)

@router.post("/{part}/search")
async def search(request:Request,part:str,search_name: str = Form(None),start_date:Optional[date]=Form(None),end_date:Optional[date]=Form(None)):
	category = get_category(check="check")
	data={}
	l_class = part.split("-")[0]
	m_class = part.split("-")[1]
	s_class = part.split("-")[-1]
	data['part']=f"{l_class}-{m_class}-{s_class}"
	if search_name!=None:
		if get_name(db=db_session,name=search_name):	
			data['name']=search_name
			if start_date != None and end_date != None:
				label,work = label_work(l_class=l_class,m_class=m_class,s_class=s_class,name=search_name,start_date=start_date,end_date=end_date,check="check")
				error = get_date_search_error(db=db_session,l_class=l_class,m_class=m_class,s_class=s_class,name=search_name,start_date=start_date,end_date=end_date)
			else:
				if start_date == None:
					start_date == datetime.date(2022,3,1).strftime("%Y-%m-%d")
				if end_date == None:
					end_date = datetime.date.today().strftime("%Y-%m-%d")
				label,work= label_work(l_class=l_class,m_class=m_class,s_class=s_class,name=search_name,start_date=start_date,end_date=end_date,check="check")
				error = get_search_error(db=db_session,l_class=l_class,m_class=m_class,s_class=s_class,name=search_name)
			return templates.TemplateResponse('search_check_charts.html',{'request':request,'category':category,'name':search_name,'l_class':l_class,'m_class':m_class,'s_class':s_class,'bar_data':label,'work':work,'error':error})
		else:
			return RedirectResponse(url=f"/checker/{part}", status_code=302)
	else:
		if start_date != None and end_date != None:
			label,work = label_work(l_class=l_class,m_class=m_class,s_class=s_class,name="term",start_date=start_date,end_date=end_date,check="check")
			error = get_date_search_error(db=db_session,l_class=l_class,m_class=m_class,s_class=s_class,name="term",start_date=start_date,end_date=end_date)
		else:
			if start_date == None and end_date == None:
				return RedirectResponse(url=f"/checker/{part}", status_code=302)
			if start_date == None:
				start_date = datetime.date(2022,3,1)
			if end_date == None:
				end_date = datetime.date.today().strftime("%Y-%m-%d")
			label,work= label_work(l_class=l_class,m_class=m_class,s_class=s_class,name="term",start_date=start_date,end_date=end_date,check="check")
			error = get_search_error(db=db_session,l_class=l_class,m_class=m_class,s_class=s_class,name="term")
		search_name =f"{start_date}~{end_date}"
		data['name'] = search_name
		return templates.TemplateResponse('search_check_charts.html',{'request':request,'category':category,'name':search_name,'l_class':l_class,'m_class':m_class,'s_class':s_class,'bar_data':label,'work':work,'error':error})


