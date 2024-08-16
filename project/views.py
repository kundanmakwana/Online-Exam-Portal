from django.http import HttpResponse,JsonResponse
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from question.models import question
from teacher.models import teacher
from student.models import student
from batch.models import batch
from exam.models import exam
from result.models import result
from notify.models import notify
from feedback.models import feedback
from head_admin.models import HeadAdmin
import random,datetime,yagmail

EMAIL = "divyamshah2020@gmail.com"
PASSWORD = 'unvrzefgesgpgwbp'


def home(request):
    try:
        request.COOKIES['csrftoken']
        teacher_data = teacher.objects.filter(t_is_logged_in=request.COOKIES['csrftoken'])
        if len(teacher_data) != 0 and teacher_data[0].t_remember == 'on':
            return redirect('teacher_dashboard',teacher_data[0].t_id)
        student_data = student.objects.filter(s_is_logged_in=request.COOKIES['csrftoken'])
        if len(student_data) != 0 and student_data[0].s_remember == 'on':
            return redirect('student_dashboard',student_data[0].s_id)
        headadmin_data = HeadAdmin.objects.filter(h_is_logged_in=request.COOKIES['csrftoken'])
        if len(headadmin_data) != 0 and headadmin_data[0].h_remember == 'on':
            return redirect('head_admin_dashboard',headadmin_data[0].h_id)
    except:
        pass
    return render(request,"index.html")

def feedback_view(request):
    if request.method=="POST":
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        add_feed = feedback(email=email,subject=subject,message=message)
        add_feed.save()
        
        yag = yagmail.SMTP(EMAIL,PASSWORD)
        try:
            yag.send(to="divyamshah1234@gmail.com",subject="Feedback mail",
                     contents=[f"<h3>Mail from : {email}</h3><h3>Mail subject : {subject}</h3><h3>Mail message : {message}</h3>"])
        except:
            pass
        return render(request,"feedback.html",{'sent':1})
    return render(request,"feedback.html",{'sent':0})

# ----------------------- HEAD ADMIN ----------------------- #
# --- Head Admin SignIn --- #
def h_signup(request):       
    if request.method=="POST":
        h_name = request.POST['name']
        h_email = request.POST['email']
        h_password = request.POST['password'] 
        h_pfp = request.FILES['h_pfp']
        HeadAdmin_is = HeadAdmin.objects.filter(h_email=h_email)
        if HeadAdmin_is:
            #user already exist
            return render(request,'headadmin_sign_up.html',{'error':1})
        else:
            new_id=True
            while new_id:
                h_id = random.randint(1111111111,9999999999)
                HeadAdmin_id = HeadAdmin.objects.filter(h_id=h_id)
                if len(HeadAdmin_id) == 0:
                    new_id = False
            add_HeadAdmin=HeadAdmin(h_name=h_name,h_email=h_email,h_password=h_password,h_id=h_id,h_pfp=h_pfp)
            add_HeadAdmin.save()
            return redirect("head_admin-sign-in")
    
    return render(request,"headadmin_sign_up.html",{'error':0})

# --- Head Admin SignIn --- #
def h_signin(request):
    if request.method=="POST":
        h_email = request.POST.get('email')
        h_password = request.POST.get('password')
        h_remember = request.POST.get('remember')
        h_user = HeadAdmin.objects.filter(h_email=h_email)
        if len(h_user) == 0:
            return render(request,'headadmin_sign_in.html',{'error':1})
        if h_user[0].h_password == h_password:
            HeadAdmin.objects.filter(h_email=h_email).update(h_is_logged_in=request.COOKIES['csrftoken'])
            if h_remember is not None:
                HeadAdmin.objects.filter(h_email=h_email).update(h_remember=h_remember)
            return redirect('head_admin_dashboard',h_user[0].h_id)
        else:
            return render(request,'headadmin_sign_in.html',{'error':2})
    return render(request,"headadmin_sign_in.html",{'error':0})

# --- HeadAdmin Dashboard --- #
def head_admin_dashboard(request,id):
    error = 0
    try:
        request.COOKIES['csrftoken']
    except:
        return redirect('head_admin-sign-in')
    logg_in = HeadAdmin.objects.filter(h_id=id)
    if logg_in[0].h_is_logged_in != request.COOKIES['csrftoken']:
        return redirect('head_admin-sign-in')
    
    headadmin_user = HeadAdmin.objects.filter(h_id = id)
    pfp = headadmin_user[0].h_pfp.url
    
    #All Info
    teacher_info = teacher.objects.filter(ha_id = id)
    total_batch = 0        
    total_test = 0    
    if len(teacher_info) == 0:
        final_teacher_info = []
        print("no teacher")
    else:
        final_teacher_info = []
        for teacher_data in teacher_info:
            t_id = teacher_data.t_id
            batch_info = len(batch.objects.filter(t_id = t_id))        
            total_batch = total_batch + batch_info    
            test_info = exam.objects.filter(t_id = t_id)
            total_test = total_test + len(test_info)
            test_table = []
            no_test = 0
            for test_data in test_info:   
                today = datetime.date.today()                          
                exam_date = datetime.date(month=int((test_data.st_time).split('+')[0].split('/')[1]), day=int((test_data.st_time).split('+')[0].split('/')[0]), year=int((test_data.st_time).split('+')[0].split('/')[2]))
                delta = today - exam_date
                day_diff = delta.days
                if day_diff > 3:
                    no_test = 1
                test_info_dict = {
                    'test_name':test_data.e_name,                    
                    'batch_name':test_data.b_name,   
                    'students':len(result.objects.filter(e_id = test_data.e_id)),
                    'date':str(test_data.st_time).split('+')[0],
                }                                
                test_table.append(test_info_dict)
            
            
            
            final_teacher_data_dict = {
                'name':teacher_data.t_name,
                'total_batches':batch_info,
                'total_tests':len(test_info),
                'test_table':test_table,
                'no_test':no_test,
                't_id':teacher_data.t_id,
            }
            final_teacher_info.append(final_teacher_data_dict)
                            
    
    data = {
        'headadmin_user':headadmin_user[0],
        'pfp':pfp,
        'teacher_data':final_teacher_info,
        'total_teacher':int(len(teacher_info)),
        'total_batch':total_batch,
        'total_test':total_test,
    }
    
    return render(request,"headadmin_dashboard.html",data)

def head_admin_profile(request,id):
    editor = 0
    w_pass = 0
    try:
        request.COOKIES['csrftoken']
    except:
        return redirect('head_admin-sign-in')
    if request.method == "POST":
        editor = 1
        try:
            if request.POST.get('save'):
                if request.POST.get('o_pass') == HeadAdmin.objects.filter(h_id=id)[0].h_password:
                    HeadAdmin.objects.filter(h_id=id).update(h_name=request.POST.get('name'))
                    if request.FILES.get('h_pfp') != None:
                        temp_st = HeadAdmin.objects.get(h_id = id)
                        temp_st.h_pfp = request.FILES.get('h_pfp')
                        temp_st.save()
                    if request.POST.get('n_pass') != '':
                        HeadAdmin.objects.filter(h_id=id).update(h_password=request.POST.get('n_pass'))
                    editor = 0
                else:
                    w_pass = 1
        except:
            pass
        
    logg_in = HeadAdmin.objects.filter(h_id=id)
    if logg_in[0].h_is_logged_in != request.COOKIES['csrftoken']:
        return redirect('head_admin-sign-in')
    
    HeadAdmin_user = HeadAdmin.objects.filter(h_id=id)
    if len(HeadAdmin_user)==0:
        return redirect('home')
        
    HeadAdmin_photo = HeadAdmin_user[0].h_pfp.url  
    user_data = {
        'HeadAdmin':HeadAdmin_user[0],        
        'error':0,
        'HeadAdmin_photo':HeadAdmin_photo,
        'editor':editor,
        'w_pass':w_pass,
    }
    return render(request,"headadmin_profile.html",user_data)

def api_send_mail_alert(request):
    if request.method == 'POST':
        t_id = request.POST.get('t_id')
        t_data = teacher.objects.filter(t_id=t_id)[0]
        t_email = t_data.t_email
        t_name = t_data.t_name
        yag = yagmail.SMTP(EMAIL,PASSWORD)                
        yag.send(to=t_email,subject="Test Alert",
                contents=[f"<h2>Respected {t_name},</h2><br><h3>You haven't took any test in a while, I kindly request that you take the necessary tests as soon as possible</h3>"])
        return JsonResponse({'success': True})
        

def head_mis(request,id):
    error = 0
    try:
        request.COOKIES['csrftoken']
    except:
        return redirect('head_admin-sign-in')
    logg_in = HeadAdmin.objects.filter(h_id=id)
    if logg_in[0].h_is_logged_in != request.COOKIES['csrftoken']:
        return redirect('head_admin-sign-in')
    
    headadmin_user = HeadAdmin.objects.filter(h_id = id)
    pfp = headadmin_user[0].h_pfp.url
    
    #All Info
    teacher_info = teacher.objects.filter(ha_id = id)
    total_batch = 0        
    total_test = 0    
    if len(teacher_info) == 0:
        final_teacher_info = []
        print("no teacher")
    else:
        final_teacher_info = []
        for teacher_data in teacher_info:
            t_id = teacher_data.t_id
            batch_info = len(batch.objects.filter(t_id = t_id))        
            total_batch = total_batch + batch_info    
            test_info = exam.objects.filter(t_id = t_id)
            total_test = total_test + len(test_info)
            test_table = []
            no_test = 0
            for test_data in test_info:   
                today = datetime.date.today()                 
                exam_date = datetime.date(month=int((test_data.st_time).split('+')[0].split('/')[1]), day=int((test_data.st_time).split('+')[0].split('/')[0]), year=int((test_data.st_time).split('+')[0].split('/')[2]))
                delta = today - exam_date
                day_diff = delta.days
                if day_diff > 3:
                    no_test = 1
                test_info_dict = {
                    'test_name':test_data.e_name,                    
                    'batch_name':test_data.b_name,   
                    'students':len(result.objects.filter(e_id = test_data.e_id)),
                    'date':str(test_data.st_time).split('+')[0],
                }                                
                test_table.append(test_info_dict)
            
            
            
            final_teacher_data_dict = {
                'name':teacher_data.t_name,
                'total_batches':batch_info,
                'total_tests':len(test_info),
                'test_table':test_table,
                'no_test':no_test,
            }
            final_teacher_info.append(final_teacher_data_dict)
                            
    
    data = {
        'headadmin_user':headadmin_user[0],
        'pfp':pfp,
        'teacher_data':final_teacher_info,
        'total_teacher':int(len(teacher_info)),
        'total_batch':total_batch,
        'total_test':total_test,
    }
    return render(request,"mis_report.html",data)

def ha_log_out(request,id):
    HeadAdmin.objects.filter(h_id=id).update(h_is_logged_in='')
    HeadAdmin.objects.filter(h_id=id).update(h_remember='')
    return redirect('home')

def h_change_pass(request):
    otp_sent = 0
    error = 0
    email = ''
    otp = ''
    otp_verified = 0
    if request.method == "POST":
        try:
            if request.POST.get('email-check') == 'email':
                email = request.POST.get('email')
                h_reg = HeadAdmin.objects.filter(h_email = email)
                if len(h_reg) != 0:
                    yag = yagmail.SMTP(EMAIL,PASSWORD)
                    try:
                        otp = random.randint(111111,999999)
                        yag.send(to=email,subject="OTP - Verification",
                                contents=[f"<h3><u>{otp}</u> is your otp to change password.</h3>"])
                        otp_sent = 1
                    except:
                        error = 1
                else:
                    error = 1
            elif request.POST.get('otp-check') == 'otp':
                if request.POST.get('otp-sent') == request.POST.get('otp'):
                    otp_verified = 1
                    otp_sent = 3
                    email = request.POST.get('email')
                else:
                    otp = request.POST.get('otp-sent')
                    email = request.POST.get('email')
                    error = 2
                    otp_sent = 1
            elif request.POST.get('otp-verified') == 'otp':
                HeadAdmin.objects.filter(h_email=request.POST.get('email')).update(h_password = request.POST.get('n_pass'))
                return redirect('head_admin-sign-in')
        except:        
            pass
        
        
        
        
    data = {
        'otp_sent' : otp_sent,
        'email':email,
        'error':error,
        'otp':otp,
        'otp_verified':otp_verified,
    }
    return render(request,'student_change_pass.html',data)

# ----------------------- STUDENT ----------------------- #
# --- Student Register --- #
def s_signup(request):       
    if request.method=="POST":
        s_name = request.POST['name']
        s_email = request.POST['email']
        s_password = request.POST['password'] 
        s_pfp = request.FILES['s_pfp']
        student_is = student.objects.filter(s_email=s_email)
        if student_is:
            #user already exist
            return render(request,'student_sign_up.html',{'error':1})
        else:
            new_id=True
            while new_id:
                s_id = random.randint(1111111111,9999999999)
                student_id = student.objects.filter(s_id=s_id)
                if len(student_id) == 0:
                    new_id = False
            add_student=student(s_name=s_name,s_email=s_email,s_password=s_password,s_id=s_id,s_pfp=s_pfp)
            add_student.save()
            return redirect("student-sign-in")
    
    return render(request,"student_sign_up.html",{'error':0})

# --- Student SignIn --- #
def s_signin(request):
    if request.method=="POST":
        s_email = request.POST.get('email')
        s_password = request.POST.get('password')
        s_remember = request.POST.get('remember')
        s_user = student.objects.filter(s_email=s_email)
        if len(s_user) == 0:
            return render(request,'student_sign_in.html',{'error':1})
        if s_user[0].s_password == s_password:
            student.objects.filter(s_email=s_email).update(s_is_logged_in=request.COOKIES['csrftoken'])
            if s_remember is not None:
                student.objects.filter(s_email=s_email).update(s_remember=s_remember)
            return redirect('student_dashboard',s_user[0].s_id)
        else:
            return render(request,'student_sign_in.html',{'error':2})
    return render(request,"student_sign_in.html",{'error':0})

# --- Student Change Password --- #
def s_change_pass(request):
    otp_sent = 0
    error = 0
    email = ''
    otp = ''
    otp_verified = 0
    if request.method == "POST":
        try:
            if request.POST.get('email-check') == 'email':
                email = request.POST.get('email')
                s_reg = student.objects.filter(s_email = email)
                if len(s_reg) != 0:
                    yag = yagmail.SMTP(EMAIL,PASSWORD)
                    try:
                        otp = random.randint(111111,999999)
                        yag.send(to=email,subject="OTP - Verification",
                                contents=[f"<h3><u>{otp}</u> is your otp to change password.</h3>"])
                        otp_sent = 1
                    except:
                        error = 1
                else:
                    error = 1
            elif request.POST.get('otp-check') == 'otp':
                if request.POST.get('otp-sent') == request.POST.get('otp'):
                    otp_verified = 1
                    otp_sent = 3
                    email = request.POST.get('email')
                else:
                    otp = request.POST.get('otp-sent')
                    email = request.POST.get('email')
                    error = 2
                    otp_sent = 1
            elif request.POST.get('otp-verified') == 'otp':
                student.objects.filter(s_email=request.POST.get('email')).update(s_password = request.POST.get('n_pass'))
                return redirect('student-sign-in')
        except:        
            pass
        
        
        
        
    data = {
        'otp_sent' : otp_sent,
        'email':email,
        'error':error,
        'otp':otp,
        'otp_verified':otp_verified,
    }
    return render(request,'student_change_pass.html',data)

# --- Student Dashboard --- #
def student_dashboard(request,id):
    error = 0
    try:
        request.COOKIES['csrftoken']
    except:
        return redirect('student-sign-in')
    logg_in = student.objects.filter(s_id=id)
    if logg_in[0].s_is_logged_in != request.COOKIES['csrftoken']:
        return redirect('student-sign-in')
    
    if request.method == 'POST':
        b_id = request.POST.get('batch_id')
        batch_id = batch.objects.filter(b_id=b_id)
        already_joined = batch.objects.filter(b_id=b_id,s_id=id)
        if len(batch_id) == 0:
            error=1
        elif len(already_joined) != 0:
            error=2
        
        elif len(already_joined) == 0:
                add_batch = batch(b_id=b_id,s_id=id)
                add_batch.save()
                
  
    student_user = student.objects.filter(s_id=id)
    if len(student_user)==0:
        return redirect('home')
    batch_info = batch.objects.filter(s_id=id)
    batch_names = []
    for b_id in batch_info:
        temp_b_id = b_id.b_id
        batch_name_info = batch.objects.filter(b_id=temp_b_id)
        for batch_temp in batch_name_info:
            temp_name = batch_temp.b_name
            temp_id = batch_temp.b_id
            if temp_name != '':
                temp_t_id = batch_temp.t_id
                t_data = teacher.objects.filter(t_id=temp_t_id)
                t_name = t_data[0].t_name
                temp_batch_dict={'id':temp_id,'b_name':temp_name,'t_name':t_name}
                batch_names.append(temp_batch_dict) 
    student_photo = student_user[0].s_pfp.url 
    exam_data = result.objects.filter(s_id = id)
    result_info = []
    for exam_info in exam_data:
        e_info = exam.objects.filter(e_id=exam_info.e_id)
        e_name = e_info[0].e_name
        b_info = batch.objects.filter(b_id=e_info[0].b_id)
        for b in b_info:
            if b.t_id != "":
                b_name = b.b_name
        result_info.append({'e_name':e_name,'b_name':b_name,'marks':exam_info.marks_obt,'t_marks':exam_info.total_marks,'perct':exam_info.perct})
    user_data = {
        'student':student_user[0],
        'batch_names':batch_names,
        'batch_joined':len(batch_names),
        'student_photo':student_photo,
        'error':error,
        'result_info':result_info,
        'test_given':len(exam_data),
    }
    return render(request,"student_dashboard.html",user_data)

# --- Student Profile --- #
def student_profile(request,id):
    editor = 0
    w_pass = 0
    try:
        request.COOKIES['csrftoken']
    except:
        return redirect('student-sign-in')
    if request.method == "POST":
        editor = 1
        try:
            if request.POST.get('save'):
                if request.POST.get('o_pass') == student.objects.filter(s_id=id)[0].s_password:
                    student.objects.filter(s_id=id).update(s_name=request.POST.get('name'))
                    if request.FILES.get('s_pfp') != None:
                        temp_st = student.objects.get(s_id = id)
                        temp_st.s_pfp = request.FILES.get('s_pfp')
                        temp_st.save()
                    if request.POST.get('n_pass') != '':
                        student.objects.filter(s_id=id).update(s_password=request.POST.get('n_pass'))
                    editor = 0
                else:
                    w_pass = 1
        except:
            pass
        
    logg_in = student.objects.filter(s_id=id)
    if logg_in[0].s_is_logged_in != request.COOKIES['csrftoken']:
        return redirect('student-sign-in')
    
    student_user = student.objects.filter(s_id=id)
    if len(student_user)==0:
        return redirect('home')
    batch_info = batch.objects.filter(s_id=id)
    batch_names = []
    for id in batch_info:
        temp_b_id = id.b_id
        batch_name_info = batch.objects.filter(b_id=temp_b_id)
        for batch_temp in batch_name_info:
            temp_name = batch_temp.b_name
            temp_id = batch_temp.b_id
            if temp_name != '':
                temp_t_id = batch_temp.t_id
                t_data = teacher.objects.filter(t_id=temp_t_id)
                t_name = t_data[0].t_name
                temp_batch_dict={'id':temp_id,'b_name':temp_name,'t_name':t_name}
                batch_names.append(temp_batch_dict)  
    student_photo = student_user[0].s_pfp.url  
    user_data = {
        'student':student_user[0],
        'batch_names':batch_names,
        'num_batch':len(batch_names),
        'error':0,
        'student_photo':student_photo,
        'editor':editor,
        'w_pass':w_pass,
    }
    return render(request,"student_profile.html",user_data)

# --- Student Batch View --- #
def batch_student(request,s_id,b_id):
    try:
        request.COOKIES['csrftoken']
    except:
        return redirect('student-sign-in')
    logg_in = student.objects.filter(s_id=s_id)
    if logg_in[0].s_is_logged_in != request.COOKIES['csrftoken']:
        return redirect('student-sign-in')
    check_user = batch.objects.filter(s_id=s_id,b_id=b_id)
    if len(check_user)==0:
        return redirect('home')
    student_user = student.objects.filter(s_id=s_id)
    if len(student_user)==0:
        return redirect('home')
    batch_info = batch.objects.filter(s_id=s_id)
    batch_names = []
    for id in batch_info:
        temp_b_id = id.b_id
        batch_name_info = batch.objects.filter(b_id=temp_b_id)
        for batch_temp in batch_name_info:
            temp_name = batch_temp.b_name
            temp_id = batch_temp.b_id
            if temp_name != '':
                temp_t_id = batch_temp.t_id
                t_data = teacher.objects.filter(t_id=temp_t_id)
                t_name = t_data[0].t_name
                temp_batch_dict={'id':temp_id,'b_name':temp_name,'t_name':t_name}
                batch_names.append(temp_batch_dict)    
    batch_data = batch.objects.filter(b_id=b_id)
    batch_info_data = []
    for batch_i in batch_data:
        if batch_i.b_name != '':
            t_data = teacher.objects.filter(t_id=temp_t_id)
            temp_batch_info_dict={'id':batch_i.b_id,'b_name':batch_i.b_name,'t_name':t_data[0].t_name}
            batch_info_data.append(temp_batch_info_dict)
            print(t_data[0].t_name)
            
    exam_data = exam.objects.filter(b_id=b_id)
    notify_data = notify.objects.filter(b_id=b_id)
    student_photo = student_user[0].s_pfp.url
    

    user_data = {
        'student':student_user[0],
        'batch_names':batch_names,
        'batch_data':batch_info_data[0],
        'exam_data':exam_data,
        'notify_data':notify_data,
        'student_photo':student_photo,

    }
    return render(request,'batch_student.html',user_data)

# --- Student Test View --- #
def test_student(request,s_id,b_id,e_id):
    try:
        request.COOKIES['csrftoken']
    except:
        return redirect('student-sign-in')
    logg_in = student.objects.filter(s_id=s_id)
    if logg_in[0].s_is_logged_in != request.COOKIES['csrftoken']:
        return redirect('student-sign-in')
    if request.method == 'POST':
        marks_obt = 0
        que_num = exam.objects.filter(e_id=e_id)
        que_qty = que_num[0].e_q_num
        marks_per = que_num[0].e_marks
        total_marks = marks_per*que_qty
        for que in range(que_qty):
            que_i = que+1
            que_text = request.POST.get(f'que_{que_i}')
            que_info = question.objects.filter(q_text=que_text)
            que_ans = que_info[0].ans.title()
            user_ans = request.POST.get(f'ans_{que_i}')
            if user_ans == que_ans:
                marks_obt += marks_per
        perct = (marks_obt*100)/total_marks
        perct = round(perct,2)
        result_add = result(s_id=s_id,e_id=e_id,marks_obt=marks_obt,total_marks=total_marks,perct=perct)
        result_add.save()
    student_user = student.objects.filter(s_id=s_id)
    if len(student_user)==0:
        return redirect('home')
    mark_info = {}
    test_not_started = 0
    test_ended = 0
    st_time = exam.objects.filter(e_id=e_id)
    st_time = st_time[0].st_time
    st_time = st_time.split('+')
    st_time_info = st_time[1]
    st_date_data = st_time[0].split('/')
    st_date_info = st_time[0].split('/')[0]
    st_time_hour = (st_time_info.split(':'))[0]
    st_time_min = (st_time_info.split(':'))[1]
    now_hour = datetime.datetime.now().strftime("%H")
    now_min = datetime.datetime.now().strftime("%M")
    now_date = datetime.datetime.now().strftime("%d")
    if int(st_date_info+st_time_hour+st_time_min) > int(now_date+now_hour+now_min):
        test_not_started = 1
    
    end_time = exam.objects.filter(e_id=e_id)
    end_time = end_time[0].end_time
    end_time = end_time.split('+')
    end_time_info = end_time[1]
    end_date_info = end_time[0].split('/')[0]
    end_time_hour = (end_time_info.split(':'))[0]
    end_time_min = (end_time_info.split(':'))[1]
    if int(end_date_info+end_time_hour+end_time_min) < int(now_date+now_hour+now_min):
        test_ended = 1
    
    already_given = result.objects.filter(e_id=e_id,s_id=s_id)
    if len(already_given)>0:
        test_already_given = 1
        marks = already_given[0].marks_obt
        tot_marks = already_given[0].total_marks
        percentage = already_given[0].perct
        mark_info = {'marks_obt':marks,'total_marks':tot_marks,'perct':percentage}
    else:
        test_already_given = 0
    batch_info = batch.objects.filter(s_id=s_id)
    batch_names = []
    for id in batch_info:
        temp_b_id = id.b_id
        batch_name_info = batch.objects.filter(b_id=temp_b_id)
        for batch_temp in batch_name_info:
            temp_name = batch_temp.b_name
            temp_id = batch_temp.b_id
            if temp_name != '':
                temp_t_id = batch_temp.t_id
                t_data = teacher.objects.filter(t_id=temp_t_id)
                t_name = t_data[0].t_name
                temp_batch_dict={'id':temp_id,'b_name':temp_name,'t_name':t_name}
                batch_names.append(temp_batch_dict)  
    exam_info = exam.objects.filter(e_id=e_id) 
    batch_data = batch.objects.filter(b_id=b_id,s_id='') 
    test_info = question.objects.filter(e_id=e_id)
    if len(test_info) > 0:
        question_are_there = 1
    else:
        question_are_there = 0
    test_data = datetime.datetime(year=int(st_date_data[2]),month=int(st_date_data[1]),
                                  day=int(st_date_data[0]),hour=int(st_time_hour),minute=int(st_time_min))
    test_data = {'date':test_data.strftime("%d %B,%Y"),'time':test_data.strftime("%I:%M %p")}
    student_photo = student_user[0].s_pfp.url

    user_data = {
        'student':student_user[0],
        'batch_names':batch_names,
        'error':0,
        'exam_info':exam_info[0],
        'batch_data':batch_data[0],
        'question_info':test_info,
        'question_are_there':question_are_there,
        'test_already_given':test_already_given,
        'mark_info':mark_info,
        'test_not_started':test_not_started,
        'test_ended':test_ended,
        'test_data':test_data,
        'student_photo':student_photo,

    }
    return render(request,'student_test.html',user_data)

# --- Student LogOut --- #
def s_log_out(request,s_id):
    student.objects.filter(s_id=s_id).update(s_is_logged_in='')
    student.objects.filter(s_id=s_id).update(s_remember='')
    return redirect('home')

# ----------------------- TEACHER ----------------------- #
# --- Teacher Register --- #
def t_signup(request):
    if request.method=="POST":
        t_name = request.POST['name']
        t_email = request.POST['email']
        t_password = request.POST['password']
        t_pfp = request.FILES['t_pfp']
        ha_id = request.POST.get('admin_id')
        ha_is = HeadAdmin.objects.filter(h_id = ha_id)
        teacher_is = teacher.objects.filter(t_email=t_email)
        if teacher_is:
            #user already exist
            return render(request,'teacher_sign_up.html',{'error':1})
        elif len(ha_is) == 0:
            return render(request,'teacher_sign_up.html',{'error':2})            
            
        else:
            new_id=True
            while new_id:
                t_id = random.randint(1111111111,9999999999)
                teacher_id = teacher.objects.filter(t_id=t_id)
                if len(teacher_id) == 0:
                    new_id = False
            add_teacher=teacher(t_name=t_name,t_email=t_email,t_password=t_password,t_id=t_id,t_pfp=t_pfp,ha_id=ha_id)
            add_teacher.save()
            return redirect("teacher-sign-in")
    
    return render(request,"teacher_sign_up.html",{'error':0})

# --- Teacher SignIn --- #
def t_signin(request):    
    if request.method=="POST":
        t_email = request.POST.get('email')
        t_password = request.POST.get('password')
        t_remember = request.POST.get('remember')
        t_user = teacher.objects.filter(t_email=t_email)
        if len(t_user) == 0:
            return render(request,'teacher_sign_in.html',{'error':1})
        if t_user[0].t_password == t_password:
            teacher.objects.filter(t_email=t_email).update(t_is_logged_in=request.COOKIES['csrftoken'])
            if t_remember is not None:
                teacher.objects.filter(t_email=t_email).update(t_remember=t_remember)
            return redirect('teacher_dashboard',t_user[0].t_id)
        else:
            return render(request,'teacher_sign_in.html',{'error':2})
    return render(request,"teacher_sign_in.html",{'error':0})

# --- Teacher Change Password --- #
def t_change_pass(request):
    otp_sent = 0
    error = 0
    email = ''
    otp = ''
    otp_verified = 0
    if request.method == "POST":
        try:
            if request.POST.get('email-check') == 'email':
                email = request.POST.get('email')
                t_reg = teacher.objects.filter(t_email = email)
                if len(t_reg) != 0:
                    yag = yagmail.SMTP(EMAIL,PASSWORD)
                    try:
                        otp = random.randint(111111,999999)
                        yag.send(to=email,subject="OTP - Verification",
                                contents=[f"<h3><u>{otp}</u> is your otp to change password.</h3>"])
                        otp_sent = 1
                    except:
                        error = 1
                else:
                    error = 1
            elif request.POST.get('otp-check') == 'otp':
                if request.POST.get('otp-sent') == request.POST.get('otp'):
                    otp_verified = 1
                    otp_sent = 3
                    email = request.POST.get('email')
                else:
                    otp = request.POST.get('otp-sent')
                    email = request.POST.get('email')
                    error = 2
                    otp_sent = 1
            elif request.POST.get('otp-verified') == 'otp':
                teacher.objects.filter(t_email=request.POST.get('email')).update(t_password = request.POST.get('n_pass'))
                return redirect('teacher-sign-in')
        except:        
            pass
        
        
        
        
    data = {
        'otp_sent' : otp_sent,
        'email':email,
        'error':error,
        'otp':otp,
        'otp_verified':otp_verified,
    }
    return render(request,'teacher_change_pass.html',data)

# --- Teacher Dashboard --- #
def teacher_dashboard(request,id):
    try:
        request.COOKIES['csrftoken']
    except:
        return redirect('teacher-sign-in')
    logg_in = teacher.objects.filter(t_id=id)
    if logg_in[0].t_is_logged_in != request.COOKIES['csrftoken']:
        return redirect('teacher-sign-in')
    if request.method == 'POST':
        b_name = request.POST.get('batch_name')
        new_id=True
        while new_id:
            b_id = random.randint(1111111111,9999999999)
            batch_id = batch.objects.filter(b_id=b_id)
            if len(batch_id) == 0:
                new_id = False
        add_batch = batch(b_id=b_id,b_name=b_name,t_id=id)
        add_batch.save()
        date = datetime.date.today().strftime("%d %B %Y")
        add_notify_new = notify(b_id=b_id,notify_text=f"Created on {date}",notify_time=date)
        add_notify_new.save()
    teacher_user = teacher.objects.filter(t_id=id)
    batch_info = batch.objects.filter(t_id=id)
    test_info = exam.objects.filter(t_id=id)
    if len(teacher_user)==0:
        return redirect('home')
    teacher_photo = teacher_user[0].t_pfp.url
    total_student=[]
    for b in batch_info:
        b_info = batch.objects.filter(b_id=b.b_id)
        for b_data in b_info:
            if b_data.s_id != "":
                total_student.append(b_data.s_id)
    user_data = {
        'teacher_photo':teacher_photo,
        'teacher':teacher_user[0],
        'batch_info':batch_info,
        'batch_created':len(batch_info),
        'test_created':len(test_info),
        'total_student':len(total_student),
    }
    return render(request,"teacher_dashboard.html",user_data)

# --- Teacher Profile --- #
def teacher_profile(request,id):
    editor = 0
    w_pass= 0
    try:
        request.COOKIES['csrftoken']
    except:
        return redirect('teacher-sign-in')
    if request.method == "POST":
        editor = 1
        try:
            if request.POST.get('save'):
                if request.POST.get('o_pass') == teacher.objects.filter(t_id=id)[0].t_password:
                    teacher.objects.filter(t_id=id).update(t_name=request.POST.get('name'))
                    if request.FILES.get('t_pfp') != None:                    
                        temp_t = teacher.objects.get(t_id = id)
                        temp_t.t_pfp = request.FILES.get('t_pfp')
                        temp_t.save()
                    if request.POST.get('n_pass') != '':
                        teacher.objects.filter(t_id=id).update(t_password=request.POST.get('n_pass'))
                    editor = 0
                else:
                    w_pass = 1
        except:
            pass
        
        
    logg_in = teacher.objects.filter(t_id=id)
    if logg_in[0].t_is_logged_in != request.COOKIES['csrftoken']:
        return redirect('teacher-sign-in')
    teacher_user = teacher.objects.filter(t_id=id)
    batch_info = batch.objects.filter(t_id=id)
    if len(teacher_user)==0:
        return redirect('home')
    teacher_photo = teacher_user[0].t_pfp.url
    user_data = {
        'teacher_photo':teacher_photo,
        'teacher':teacher_user[0],
        'batch_info':batch_info,
        'num_batch':len(batch_info),
        'editor':editor,
        'w_pass':w_pass,
    }
    return render(request,"teacher_profile.html",user_data)

# --- Teacher Batch View --- #
def batch_teacher(request,t_id,b_id):
    try:
        request.COOKIES['csrftoken']
    except:
        return redirect('teacher-sign-in')
    logg_in = teacher.objects.filter(t_id=t_id)
    if logg_in[0].t_is_logged_in != request.COOKIES['csrftoken']:
        return redirect('teacher-sign-in')
    if request.method == 'POST':
        if request.POST.get('message'):
            mes_text = request.POST.get('message')
            date = datetime.date.today().strftime("%d %B %Y")
            add_notify = notify(b_id=b_id,notify_text=mes_text,notify_time=date)
            add_notify.save()

        else:
            e_name = request.POST.get('test_name')
            e_q_num = request.POST.get('tot_que')
            e_marks = request.POST.get('tot_marks')
            st_date = f"{(str(request.POST.get('st_date')).replace('-','/').split('/')[2])}/{(str(request.POST.get('st_date')).replace('-','/').split('/')[1])}/{(str(request.POST.get('st_date')).replace('-','/').split('/')[0])}"

            st_time = request.POST.get('st_time')
            if 'PM' in st_time:
                st_time = str(st_time)
                st_time = st_time.replace('PM','').split(':')
                if int(st_time[0]) !=12:
                    st_time_hour = int(st_time[0]) + 12
                else:
                    st_time_hour = int(st_time[0]) - 12
                st_time_mins = st_time[1]
                st_time = datetime.time(hour=st_time_hour,minute=int(st_time_mins))
            else:
                st_time = str(st_time)
                st_time = st_time.replace('AM','').split(':')
                st_time = datetime.time(hour=int(st_time[0]),minute=int(st_time[1]))
                
            end_date = f"{(str(request.POST.get('end_date')).replace('-','/').split('/')[2])}/{(str(request.POST.get('end_date')).replace('-','/').split('/')[1])}/{(str(request.POST.get('end_date')).replace('-','/').split('/')[0])}"

            end_time = request.POST.get('end_time')
            if 'PM' in end_time:
                end_time = str(end_time)
                end_time = end_time.replace('PM','').split(':')
                if int(end_time[0]) !=12:
                    end_time_hour = int(end_time[0]) + 12
                else:
                    end_time_hour = int(end_time[0]) - 12
                end_time_mins = end_time[1]
                end_time = datetime.time(hour=end_time_hour,minute=int(end_time_mins))
            else:
                end_time = str(end_time)
                end_time = end_time.replace('AM','').split(':')
                end_time = datetime.time(hour=int(end_time[0]),minute=int(end_time[1]))
            st_datetime = f'{str(st_date)}+{str(st_time)}'
            end_datetime = f'{str(end_date)}+{str(end_time)}'
            check_st_time = st_datetime.replace('/','').replace(':','').replace('+','')
            check_end_time = end_datetime.replace('/','').replace(':','').replace('+','')
            if int(check_end_time) <= int(check_st_time):
                error = 1
                check_user = batch.objects.filter(t_id=t_id,b_id=b_id)
                if len(check_user)==0:
                    return redirect('home')
                teacher_user = teacher.objects.filter(t_id=t_id)
                batch_info = batch.objects.filter(t_id=t_id)
                if len(teacher_user)==0:
                    return redirect('home')
                batch_data = batch.objects.filter(b_id=b_id)
                batch_info_data = []
                student_info_data = []
                for batch_i in batch_data:
                    if batch_i.s_id != '':
                        student_info = student.objects.filter(s_id=batch_i.s_id)
                        student_info = {
                            'name':student_info[0].s_name,
                            'pic':student_info[0].s_pfp.url,
                        }
                        student_info_data.append(student_info)
                    if batch_i.b_name != '':
                        temp_batch_info_dict={'id':batch_i.b_id,'b_name':batch_i.b_name}
                        batch_info_data.append(temp_batch_info_dict)
                exam_data = exam.objects.filter(b_id=b_id)
                teacher_photo = teacher_user[0].t_pfp.url
                user_data = {
                    'teacher_photo':teacher_photo,
                    'teacher':teacher_user[0],
                    'batch_info':batch_info,
                    'batch_data':batch_info_data[0],
                    'exam_data':exam_data,
                    'student_info_data':student_info_data,
                    'total_students':len(student_info_data),
                    'total_test':len(exam_data),
                    'error':error,
                    'e_name' : request.POST.get('test_name'),
                    'e_q_num' : request.POST.get('tot_que'),
                    'e_marks' : request.POST.get('tot_marks'),
                    'st_date' : request.POST.get('st_date'),
                    'st_time' : request.POST.get('st_time'),
                    'end_date' : request.POST.get('end_date'),
                    'end_time' : request.POST.get('end_time'),
                }
                return render(request,"batch_teacher.html",user_data)
                
            new_id=True
            while new_id:
                e_id = random.randint(1111111111,9999999999)
                exam_id = exam.objects.filter(e_id=e_id)
                if len(exam_id) == 0:
                    new_id = False
            batch_name = batch.objects.filter(b_id = b_id)[0].b_name
            add_exam = exam(e_name=e_name,e_q_num=e_q_num,e_marks=e_marks,t_id=t_id,e_id=e_id,b_id=b_id,b_name=batch_name,st_time=st_datetime,end_time=end_datetime)
            add_exam.save()
            return redirect('teacher_test',t_id,b_id,e_id)
            
    check_user = batch.objects.filter(t_id=t_id,b_id=b_id)
    if len(check_user)==0:
        return redirect('home')
    teacher_user = teacher.objects.filter(t_id=t_id)
    batch_info = batch.objects.filter(t_id=t_id)
    if len(teacher_user)==0:
        return redirect('home')
    batch_data = batch.objects.filter(b_id=b_id)
    batch_info_data = []
    student_info_data = []
    for batch_i in batch_data:
        if batch_i.s_id != '':
            student_info = student.objects.filter(s_id=batch_i.s_id)
            student_info = {
                'name':student_info[0].s_name,
                'pic':student_info[0].s_pfp.url,
            }
            student_info_data.append(student_info)
        if batch_i.b_name != '':
            temp_batch_info_dict={'id':batch_i.b_id,'b_name':batch_i.b_name}
            batch_info_data.append(temp_batch_info_dict)
    exam_data = exam.objects.filter(b_id=b_id)
    teacher_photo = teacher_user[0].t_pfp.url
    user_data = {
        'teacher_photo':teacher_photo,
        'teacher':teacher_user[0],
        'batch_info':batch_info,
        'batch_data':batch_info_data[0],
        'exam_data':exam_data,
        'student_info_data':student_info_data,
        'total_students':len(student_info_data),
        'total_test':len(exam_data),
    }
    return render(request,"batch_teacher.html",user_data)

# --- Teacher Test View --- #
def test_teacher(request,t_id,b_id,e_id):
    que_info=0
    try:
        request.COOKIES['csrftoken']
    except:
        return redirect('teacher-sign-in')
    logg_in = teacher.objects.filter(t_id=t_id)
    if logg_in[0].t_is_logged_in != request.COOKIES['csrftoken']:
        return redirect('teacher-sign-in')
    if request.method == "POST":
        if request.POST.get('edit_question'):
            que_info = question.objects.filter(e_id=e_id)    
        elif request.POST.get('q_id_1'):
            que = exam.objects.filter(b_id=b_id,e_id=e_id)
            que_qty = int(que[0].e_q_num)
            for q in range(que_qty):
                q_num = q+1                
                q_id = request.POST.get(f'q_id_{q_num}')
                edit_que = question.objects.get(id=q_id)                
                edit_que.q_text = str(request.POST.get(f'que_{q_num}')).strip()
                edit_que.op_a = request.POST.get(f'op_a_{q_num}')
                edit_que.op_b = request.POST.get(f'op_b_{q_num}')
                edit_que.op_c = request.POST.get(f'op_c_{q_num}')
                edit_que.op_d = request.POST.get(f'op_d_{q_num}')
                edit_que.ans = request.POST.get(f'ans_{q_num}')
                edit_que.save()
                
                
        else:
            que = exam.objects.filter(b_id=b_id,e_id=e_id)
            que_qty = int(que[0].e_q_num)
            for q in range(que_qty):
                q_num = q+1
                q_text = str(request.POST.get(f'que_{q_num}')).strip()
                q_op_a = request.POST.get(f'op_a_{q_num}')
                q_op_b = request.POST.get(f'op_b_{q_num}')
                q_op_c = request.POST.get(f'op_c_{q_num}')
                q_op_d = request.POST.get(f'op_d_{q_num}')
                q_ans = request.POST.get(f'ans_{q_num}')
                add_que = question(q_text=q_text,op_a=q_op_a,op_b=q_op_b,op_c=q_op_c,op_d=q_op_d,ans=q_ans,b_id=b_id,e_id=e_id)
                add_que.save()
    check_user = batch.objects.filter(t_id=t_id,b_id=b_id)
    if len(check_user)==0:
        return redirect('home')
    teacher_user = teacher.objects.filter(t_id=t_id)
    batch_info = batch.objects.filter(t_id=t_id)
    if len(teacher_user)==0:
        return redirect('home')
    batch_data = batch.objects.filter(b_id=b_id)
    batch_info_data = []
    for batch_i in batch_data:
        if batch_i.b_name != '':
            temp_batch_info_dict={'id':batch_i.b_id,'b_name':batch_i.b_name}
            batch_info_data.append(temp_batch_info_dict)
    exam_data = exam.objects.filter(b_id=b_id)
    exam_info = exam.objects.filter(b_id=b_id,e_id=e_id)
    que_num = exam_info[0].e_q_num
    questions_are = question.objects.filter(e_id=e_id)
    if len(questions_are) > 0:
        questions_are_there = 1
    else:
        questions_are_there = 0
    question_info = question.objects.filter(b_id=b_id,e_id=e_id)
    result_info = result.objects.filter(e_id=e_id)
    result_data=[]
    for student_info in result_info:
        s_id = student_info.s_id
        s_info = student.objects.filter(s_id=s_id)
        s_name = s_info[0].s_name
        marks_obt = student_info.marks_obt
        total_marks = student_info.total_marks
        perct = student_info.perct
        pic = s_info[0].s_pfp.url
        result_data.append({'s_name':s_name,'marks_obt':marks_obt,'total_marks':total_marks,'perct':perct, 'pic':pic})
    teacher_photo = teacher_user[0].t_pfp.url
    user_data = {
        'teacher_photo':teacher_photo,   
        'teacher':teacher_user[0],
        'batch_info':batch_info,
        'batch_data':batch_info_data[0],
        'exam_data':exam_data,
        'exam_info':exam_info[0],
        'que_num':range(que_num),
        'questions_are_there':questions_are_there,
        'question_info':question_info,
        'result_info':result_data,
        'que_info':que_info,
    }
    return render(request,'teacher_test.html',user_data)

# --- Teacher LogOut --- #
def t_log_out(request,t_id):
    teacher.objects.filter(t_id=t_id).update(t_is_logged_in='')
    teacher.objects.filter(t_id=t_id).update(t_remember='')
    return redirect('home')

# ----------------------- ADMIN DELETE ALL RECORDS ----------------------- #
def delete(request):
    batch.objects.all().delete()
    exam.objects.all().delete()
    notify.objects.all().delete()
    question.objects.all().delete()
    result.objects.all().delete()
    student.objects.all().delete()
    teacher.objects.all().delete()
    feedback.objects.all().delete()
    
    return redirect('/admin')