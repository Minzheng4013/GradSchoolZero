
from django.shortcuts import render,redirect
from student.models import *
from instructor.models import *
from account.models import *
from django.core.mail import send_mail
from django.conf import settings
from .forms import *
from .models import *
from django.contrib import messages
import csv
import datetime

from bs4 import BeautifulSoup
import requests


def registrarView(request):
	if request.user.is_admin:
		url="https://www1.cuny.edu/mu/forum/"
		r = requests.get(url)
		row=[]
		text=[]
		soup = BeautifulSoup(r.content, 'html5lib')
		for h2 in soup.find_all('h2'):
			for link in h2.find_all('a', href=True):
				row.append(link["href"])
				text.append(link.text)


		registrar=User.objects.get(email=request.user)
		currentTime = datetime.datetime.now()
		if currentTime.hour < 12:
			greeting="Good Morning "
		elif 12 <= currentTime.hour < 18:
			greeting="Good Afternoon "
		else:
			greeting="Good Evening "

		return render(request, "registrar/registrarView.html", {"g":greeting,"r":registrar,"all_data":zip(row,text)})



	else:
		return render(request, "main/forbidden.html",{})

def viewNewUser(request):
	try:
		user=User.objects.filter(email=request.user)
	except:
		return render(request, "main/forbidden.html",{})
	if  user[0].is_admin==True:
		application=Applcation.objects.all()
		jobs=career.objects.all()
		context={'application':application,'jobs':jobs}
		return render(request, "registrar/viewNewUser.html",context)
	else:
		return render(request, "main/forbidden.html",{})

def viewGrad(request):
	if request.user.is_admin:
		return render(request, "registrar/viewGrad.html", {})
	else:
		return render(request, "main/forbidden.html",{})

def viewRating(request):
	if request.user.is_admin:
		rateClass = RateClass.objects.all()
		return render(request, "registrar/viewRating.html", {"rates": rateClass})
	else:
		return render(request, "main/forbidden.html",{})

def setClass(request):
	if request.user.is_admin:
		return render(request, "registrar/setClass.html", {})
	else:
		return render(request, "main/forbidden.html",{})

def tabooList(request):
	if request.user.is_admin:
		if request.method == "POST":
			form = TabooForm(request.POST)
			if form.is_valid():
				form.save()

		taboo = Taboo.objects.all()
		form = TabooForm()
		return render(request, "registrar/tabooList.html", {"form":form, "taboo":taboo})
	else:
		return render(request, "main/forbidden.html",{})

def processStudentComplaint(request, pk=None):
	if request.user.is_admin:
		if request.method == "POST":
			# get the corresponding complaint
			c = StudentComplaint.objects.get(id=pk)

			form = ProcessStudentComplaintForm(request.POST, instance=c)

			if form.is_valid():
				form.save()
				# mark is as completed
				res = StudentComplaint.objects.get(id=pk)
				res.is_completed = True
				res.save()

				# process actions:
				# warn the student
				if res.action == "ws":
					s = Student.objects.get(ID=res.punish_id)
					s.warning += 1
					s.save()
				# warn the instructor
				elif res.action == "wi":
					i = Instructor.objects.get(ID=res.punish_id)
					i.warning += 1
					i.save()

				scomplaint = StudentComplaint.objects.all()
				icomplaint = InstructorComplaint.objects.all()
				return render(request, "registrar/manageComplaint.html", {"sc": scomplaint, "ic": icomplaint})

		form = ProcessStudentComplaintForm()
		return render(request, "registrar/processStudentComplaint.html", {"form":form})
	else:
		return render(request, "main/forbidden.html",{})

def processInstructorComplaint(request, pk=None):
	if request.user.is_admin:
		if request.method == "POST":
			c = InstructorComplaint.objects.get(id=pk)

			form = ProcessInstructorComplaintForm(request.POST, instance=c)

			if form.is_valid():
				form.save()
				# mark is as completed
				res = InstructorComplaint.objects.get(id=pk)
				res.is_completed = True
				res.save()

				# process actions
				# warn the student
				if res.action == "ws":
					s = Student.objects.get(ID=res.punish_id)
					s.warning += 1
					s.save()
				# warn the instructor
				elif res.action == "wi":
					i = Instructor.objects.get(ID=res.punish_id)
					i.warning += 1
					i.save()
				elif res.action == "ds":
					s = Student.objects.get(ID=res.punish_id)
					s.is_suspended = True
					s.save()

				scomplaint = StudentComplaint.objects.all()
				icomplaint = InstructorComplaint.objects.all()
				return render(request, "registrar/manageComplaint.html", {"sc": scomplaint, "ic": icomplaint})

		form = ProcessInstructorComplaintForm()
		return render(request, "registrar/processInstructorComplaint.html", {"form":form})
	else:
		return render(request, "main/forbidden.html",{})

def manageComplaint(request):
	if request.user.is_admin:
		scomplaint = StudentComplaint.objects.all()
		icomplaint = InstructorComplaint.objects.all()
		return render(request, "registrar/manageComplaint.html", {"sc": scomplaint, "ic": icomplaint})
	else:
		return render(request, "main/forbidden.html",{})

def manageSuspension(request):
	if request.user.is_admin:
		return render(request, "registrar/manageSuspension.html", {})
	else:
		return render(request, "main/forbidden.html",{})

def rejectapplications(request,pk=None):
	if request.user.is_admin:
		try:
			if Applcation.objects.get(id=pk)!=None:
				if  float(Applcation.objects.get(id=pk).Gpa)<3:
					Applcation.objects.get(id=pk).delete()
					return redirect("viewNewUser")

				else:
					Applcation.objects.get(id=pk).delete()
					return render(request,"registrar/reasonform.html")
		except:
			return redirect("viewNewUser")
	else:
		return render(request, "main/forbidden.html",{})

def acceptapplications(request,pk=None):
	if request.user.is_admin:
		try:
			if  float(Applcation.objects.get(id=pk).Gpa)>3:
				user=User.objects.last()
				StudentEmail=Applcation.objects.get(id=pk).firstname[0]+Applcation.objects.get(id=pk).lastname+"00"+str(int(user.id)+1)+"@citymail.cuny.edu"
				user=User(email=StudentEmail,username=StudentEmail,first_name=Applcation.objects.get(id=pk).firstname,last_name=Applcation.objects.get(id=pk).lastname,is_student=True,First_login=True)
				user.set_password(StudentEmail)
				user.save()
				ID=20000000+int(user.id)+1
				student=Student(email=StudentEmail,first_name=Applcation.objects.get(id=pk).firstname,last_name=Applcation.objects.get(id=pk).lastname,ID=ID)
				student.save()
				try:
					subject="Congratulations"
					message="Thank you for applying CUNY.After deep consideration, we decide to give you the offer, your CUNY email will be .., and login password will be same."
					email_from=settings.EMAIL_HOST_USER
					recipent_list=[Applcation.objects.get(id=pk).email]
					send_mail(subject,message,email_from,recipent_list)
				except:
					pass

				Applcation.objects.get(id=pk).delete()
				return redirect("viewNewUser")

			else:
				Applcation.objects.get(id=pk).delete()
				return render(request,"registrar/reasonform.html")
		except:
			return redirect("viewNewUser")
	else:
		return render(request, "main/forbidden.html",{})

def reject_job_application(request,pk=None):
	if request.user.is_admin:
		try:
			if career.objects.get(id=pk)!=None:
				try:
					subject="Sorry"
					message="We appreciate your interest in CUNY and the time you’ve invested in applying for instructor role. There has been significant interest in this role At this time, we have made the decision to move forward with other applicants."
					email_from=settings.EMAIL_HOST_USER
					recipent_list=[career.objects.get(id=pk).email]
					send_mail(subject,message,email_from,recipent_list)
				except:
					pass

				career.objects.get(id=pk).delete()
				return redirect("viewNewUser")
		except:
			return redirect("viewNewUser")
	else:
		return render(request, "main/forbidden.html",{})

def accept_job_applications(request,pk=None):
	if request.user.is_admin:
		try:
			if career.objects.get(id=pk)!=None:
				user=User.objects.last()
				ProfesorEmail=career.objects.get(id=pk).firstname[0]+career.objects.get(id=pk).lastname+"00"+str(int(user.id)+1)+"@citymail.cuny.edu"
				user=User(email=ProfesorEmail,username=ProfesorEmail,first_name=career.objects.get(id=pk).firstname,last_name=career.objects.get(id=pk).lastname,is_instructor=True,First_login=True)
				user.set_password(ProfesorEmail)
				user.save()
				ID=10000000+int(user.id)+1
				instructor=Instructor(email=ProfesorEmail,first_name=career.objects.get(id=pk).firstname,last_name=career.objects.get(id=pk).lastname,ID=ID)
				instructor.save()
				try:
					subject="Congratulations"
					message="Thank you for applying CUNY.After deep consideration, we decide to give you the offer, your CUNY email will be .., and login password will be same."
					email_from=settings.EMAIL_HOST_USER
					recipent_list=[career.objects.get(id=pk).email]
					send_mail(subject,message,email_from,recipent_list)
				except:
					pass

				career.objects.get(id=pk).delete()
				return redirect("viewNewUser")
		except:
			return redirect("viewNewUser")
	else:
		return render(request, "main/forbidden.html",{})

def PeriodSetup(request):
	if request.user.is_admin:
		if request.method=='POST':
			form=Periodsetup(request.POST)
			period=Period.objects.last()
			class_setup=request.POST.get('is_class_setup')
			course_registration=request.POST.get('is_course_registration')
			class_running_period=request.POST.get('is_class_running_period')
			grading_period=request.POST.get('is_grading_period')
			if class_setup=='on':
				period.is_class_setup=True
				period.is_course_registration=False
				period.is_class_running_period=False
				period.is_grading_period=False
			if course_registration =='on':
				period.is_course_registration=True
				period.is_class_setup=False
				period.is_class_running_period=False
				period.is_grading_period=False

			if class_running_period=='on':
				period.is_class_running_period=True
				period.is_class_setup=False
				period.is_course_registration=False
				period.is_grading_period=False

			if 	grading_period=='on':
				period.is_grading_period=True
				period.is_class_setup=False
				period.is_class_running_period=False
				period.is_course_registration=False
			period.save()


			return render(request, "registrar/periodsetup.html", {"form":form,"period":period})
		else :
			period=Period.objects.last()
			form=Periodsetup()
			return render(request, "registrar/periodsetup.html",{"form":form,"period":period})
	else:
		return render(request, "main/forbidden.html",{})

def processClass(request, pk=None):
	if request.user.is_admin:
		if request.method == "POST":
			c = Course.objects.get(id=pk)
			form = SetClassForm(request.POST, instance=c)
			start_time1=c.start_time if not request.POST['start_time'] else request.POST['start_time']
			end_time1=c.end_time		if not request.POST['end_time'] else request.POST['end_time']
			meeting_date1=c.meeting_date if not request.POST['meeting_date'] else request.POST['meeting_date']
			max_size1=c.maxt_size  if not request.POST['max_size'] else request.POST['max_size']
			instructor1=User.objects.get(email=c.instructor).id  if not request.POST['instructor'] else request.POST['instructor']
			is_open1=True if  request.POST.get('is_open')=='on' else False

			if form.is_valid():
				form.save()



				c.start_time=start_time1
				c.end_time=end_time1
				c.meeting_date=meeting_date1
				c.max_size=max_size1
				c.is_open=is_open1
				c.instructor=Instructor.objects.get(email=User.objects.get(id=instructor1).email)
				c.save()
				try:
					cr=course_record.objects.filter(course_name=c.name,semester=Period.objects.last().term_info+ str(Period.objects.last().year),Instructor_email="TBD")

					for i in cr:
						cr.Instructor_email=c.instructor
						i.save()
				except:
					pass
				c = Course.objects.all()
				return render(request, "registrar/setClass.html", {"c": c})


		form = SetClassForm()
		return render(request, "registrar/processClass.html", {"form":form})
	else:
		return render(request, "main/forbidden.html",{})

def setClass(request):
	if request.user.is_admin:
		c = Course.objects.all()
		return render(request, "registrar/setClass.html", {"c": c})
	else:
		return render(request, "main/forbidden.html",{})
def honor(request):
	if request.user.is_admin:
		if not Period.objects.last().is_grading_period:
		
			list1=Student.objects.filter(yearinschool__gte=2,GPA__gte=3.5)
			

			semester=Period.objects.last().term_info+ str(Period.objects.last().year)
			courserecord=course_record.objects.filter(semester=semester).all().exclude(grade="").order_by("student_email")
			
			studentlist={n.student_email:[0,0]  for n in courserecord}
			g={"A":4,"B":3.5,"C":3,"D":2.5,"F":0,"W":0}
			for i in courserecord:
				studentlist[i.student_email][0]+=g[i.grade]
				studentlist[i.student_email][1]+=1
			list2=[]
			gpa=[]
			for i in studentlist:
				if studentlist[i][0]/studentlist[i][1]>=3.75:
					
					list2.append(Student.objects.get(email=i))
				
					gpa.append(studentlist[i][0]/studentlist[i][1])
			

			
			return render(request, "registrar/honorstudents.html",{"list1":list1,"list2":zip(list2,gpa),"semester":semester})
		else:
			return render(request, "registrar/honorstudents.html")
	else:
		return render(request, "main/forbidden.html",{})
def assignhonor(request):
	if request.user.is_admin:
		if not Period.objects.last().is_grading_period:
			
				list1=Student.objects.filter(yearinschool__gte=2,GPA__gte=3.5)
				for i in list1:
					if i.warning>0:
						i.wanrning-=1
						i.save()
					else:
						i.Honors+=1
						i.save()

				semester=Period.objects.last().term_info+ str(Period.objects.last().year)
				courserecord=course_record.objects.filter(semester=semester).all().exclude(grade="").order_by("student_email")
				
				studentlist={n.student_email:[0,0]  for n in courserecord}
				g={"A":4,"B":3.5,"C":3,"D":2.5,"F":0,"W":0}
				for i in courserecord:
					studentlist[i.student_email][0]+=g[i.grade]
					studentlist[i.student_email][1]+=1
				list2=[]
				gpa=[]
				for i in studentlist:
					if studentlist[i][0]/studentlist[i][1]>=3.75:
						
						list2.append(Student.objects.get(email=i))
					
						gpa.append(studentlist[i][0]/studentlist[i][1])
				for i in list2:
					if i.warning>0:
						i.wanrning-=1
						i.save()
					else:
						i.Honors+=1
						i.save()

				
				return redirect("honorlist")
		else:
				return redirect("honorlist")
	else:
		return render(request, "main/forbidden.html",{})