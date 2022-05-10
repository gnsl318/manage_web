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

@router.get("/download/{part}")
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
	return FileResponse(path=file_path,media_type='application/octet-stream',filename=f"{file_name}_{datetime.datetime.now().strftime('%Y/%m/%d %H/%M')}.xlsx")
@router.post("/main/check_error")
async def change_error(request:Request,error_id:str = Form(None)):
	error_data = await request.form()
	try:
		for _,error_id in error_data.items():
			update_check_error_info(db=db_session,error_id=error_id,clear_user=request.session["name"])
	except:
		pass
	return RedirectResponse(url=f"/{request.session['part']}", status_code=302)