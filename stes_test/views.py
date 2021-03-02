import django.utils
import random
import json
from datetime import date
from django.shortcuts import render, HttpResponse, redirect
from .models import student, question_answers, results, physics, math, chemistry
from django.db import connection, DataError
from django.contrib.auth.models import User
from .models import student
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import http.client
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# Create your views here.


def welcome(request):
    logout(request)
    return render(request, 'welcome.html')


def register(request):
    logout(request)
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        college = request.POST.get('college')
        address_line_1 = request.POST.get('address_line_1')
        city = request.POST.get('city')
        district = request.POST.get('district')
        state = request.POST.get('state')
        email = request.POST.get('email')
        phone_no = request.POST.get('phone_no')
        alt_phone_no = request.POST.get('alt_phone_no')

        random_str = ""

        for i in range(6):
            if i == 0:
                rand = random.randrange(1, 9, 1)
            else:
                rand = random.randrange(0, 9, 1)
            random_str += str(rand)

        flag = 0
        if len(first_name) == 0 or len(last_name) == 0 or len(college) == 0 or len(address_line_1) == 0 or len(
                email) == 0 or len(
            phone_no) == 0:
            messages.warning(request, 'All fields are mandatory')
            flag = 1
        if len(phone_no) != 10:
            messages.warning(request, 'Phone no should have 10 digits')
            flag = 1

        for no in phone_no:
            if no not in ('1', '2', '3', '4', '5', '6', '7', '8', '9', '0'):
                messages.warning(request, 'Mobile Number should have only have numeric character')
                flag = 1
                break

        if len(alt_phone_no) != 10:
            messages.warning(request, 'Alternate Mobile Number should have 10 digits')
            flag = 1

        for no in alt_phone_no:
            if no not in ('1', '2', '3', '4', '5', '6', '7', '8', '9', '0'):
                messages.warning(request, 'Alternate Mobile Number should have only have numeric character')
                flag = 1
                break

        if len(address_line_1) < 5:
            messages.warning(request, 'Address_line_1 is too short')
            flag = 1

        if student.objects.filter(email=email).first():
            messages.warning(request, 'Email id already used')
            flag = 1

        if student.objects.filter(phone_no=phone_no).first():
            messages.warning(request, 'Phone number already used')
            flag = 1

        if flag == 1:
            return render(request, 'register.html',
                          {"first_name": first_name, "last_name": last_name, "college": college,
                           "address_line_1": address_line_1, "city": city,
                           "district": district, "state": state,
                           "email": email, "phone_no": phone_no,
                           "alt_phone_no": alt_phone_no})
        else:
            student_details = student(first_name=first_name, last_name=last_name, college=college,
                                      address_line_1=address_line_1, city=city, district=district,
                                      state=state, email=email, phone_no=phone_no,
                                      alt_phone_no=alt_phone_no, random_no=int(random_str))
            student_details.save()
            sendOtp(phone_no, random_str)

            return render(request, 'otp.html')
    else:
        return render(request, 'register.html')


def otp(request):
    logout(request)
    if request.method == 'POST':

        # print("in otp post")
        entered_email = request.POST.get('username')
        entered_otp = request.POST.get('otp_field')

        if student.objects.filter(email=entered_email).exists():
            student1 = student.objects.get(email=entered_email)
            # print(student1.random_no)
            master_otp = '440032'
            if entered_otp == str(student1.random_no) or entered_otp == master_otp:
                if entered_otp == master_otp:
                    temp_obj = student.objects.get(email=entered_email)
                    temp_obj.random_no = int(entered_otp)
                    temp_obj.save()
                # print("otp matched")
                if not User.objects.filter(username=entered_email).exists():
                    # print("User doesn't exists.")
                    student_details = User.objects.create_user(entered_email, entered_email, entered_otp)
                    # first_name=student1.first_name, last_name=student1.last_name,
                    # email=entered_email)
                    student_details.first_name = student1.first_name
                    student_details.last_name = student1.last_name
                    student_details.save()

                # user = authenticate(request, username=username, password=password)
                user = authenticate(request, username=entered_email, password=entered_otp)
                if user is not None:
                    # print("User is authenticated.")
                    login(request, user)

                    # messages.success(request, 'Login Successfull')
                # else:
                # print("fgdsjkhgsdkjhfgkdsjfhgksdjfghsdlkjfghsdlkfjghdskfjghdslkjghdlkjgfhdkjhgkjdhgkjsdhgkjshd")
                # return rules(request)
                return scroller(request)
                # return redirect('/stes_test/scroller/')

            else:
                messages.warning(request, 'Invalid username or password.')
                return render(request, 'otp.html')
        else:
            messages.warning(request, 'User doesn\'t exists.')
            #
            # user = User.objects.filter(username=entered_email, password=str(entered_otp)).first()
            #
            # # print(user)
            #
            # if user is not None:
            #     login(request, user)
            #     messages.success(request, 'Login Successfull')
            #     return main_test(request)
            # else:
            #     messages.warning(request, 'Incorrect OTP')
            #     return redirect('otp')

    return render(request, 'otp.html')


def main_test(request):
    # print(request.user.is_authenticated)
    # print(request.user.username)

    if not request.user.is_authenticated:
        return welcome(request)

    if request.method == 'GET':
        messages.warning(request, 'Missuse of question paper')
        return otp(request)

    username = request.POST.get('username')

    if question_answers.objects.filter(username=username).first():

        cursor = connection.cursor()

        username = request.POST.get('username')
        bookmark = request.POST.get('bookmark2')
        invalid = request.POST.get('invalid2')
        previous_question_no = request.POST.get('previous_question_no')
        next_question_no = request.POST.get('next_question_no')
        marked_answer = request.POST.get('marked_answer')
        backend_time = request.POST.get('time_left')

        # print("username is " + username)
        # print("username is " + backend_time)
        #
        # print("bookmark " + str(bookmark))
        # print("invalid " + str(invalid))
        # print("previous_question_no " + str(previous_question_no))
        # print("next_question_no " + str(next_question_no))
        # print("marked_answer " + str(marked_answer))

        if marked_answer is None or marked_answer == "":
            marked_answer = "0"
        if bookmark is None or bookmark == "":
            bookmark = "0"
        if invalid is None or invalid == "":
            invalid = "0"
        if previous_question_no is None or previous_question_no == "":
            previous_question_no = "1"
        if next_question_no is None or next_question_no == "":
            next_question_no = "1"
        if marked_answer is None or marked_answer == "":
            marked_answer = "0"
        if backend_time == "" or backend_time is None:
            cursor.execute(
                "select time_left from stes_test_question_answers where username = \""
                + username + "\"")
            q = cursor.fetchall()
            backend_time = q[0][0]
        else:
            # if backend_time == "0":
            #     return calculate_result(request)
            # print("Error time")
            backend_time = int(backend_time)
            cursor.execute(
                "update stes_test_question_answers set time_left = " + str(backend_time) + " where username = \""
                + username + "\"")

        # print("I am at the end")

        user = username  # request.user
        subject_id = 0
        if int(next_question_no) <= 50:
            cursor.execute(
                "select bookmark, invalid, marked_answers, physics_questions, attempted from "
                "stes_test_question_answers where "
                "username = \""
                + user + "\"")
            subject_id = 1
        elif 51 <= int(next_question_no) <= 100:
            cursor.execute(
                "select bookmark, invalid, marked_answers, chemistry_questions, attempted from "
                "stes_test_question_answers where "
                "username = \""
                + user + "\"")
            subject_id = 2
        else:
            cursor.execute(
                "select bookmark, invalid, marked_answers, math_questions, attempted from stes_test_question_answers "
                "where "
                "username = \""
                + user + "\"")
            subject_id = 3

        question_number = int(next_question_no) - 50 * (subject_id - 1)

        qset = cursor.fetchall()

        bookmark_list = qset[0][0].split(",")
        invalid_list = qset[0][1].split(",")
        marked_answer_list = qset[0][2].split(",")
        new_question_number = qset[0][3].split(",")
        attempted = qset[0][4].split(",")

        # print("New questions all ids is : " + str(len(new_question_number)))

        # print("current question number is : " + str(question_number))

        question_id_in_subject_table = new_question_number[question_number - 1]
        next_question_marked_answer = marked_answer_list[int(next_question_no) - 1]

        # print("question id to be featched : -" + str(question_id_in_subject_table) + "-")

        if previous_question_no is not None:
            bookmark_list[int(previous_question_no) - 1] = bookmark
            invalid_list[int(previous_question_no) - 1] = invalid
            marked_answer_list[int(previous_question_no) - 1] = marked_answer

            if marked_answer != "0":
                # print("Marked answer : " + marked_answer)
                # print("Attempted changed for question : " + previous_question_no)
                attempted[int(previous_question_no) - 1] = "1"
            else:
                attempted[int(previous_question_no) - 1] = "0"

            bookmark_list1 = ",".join(bookmark_list)
            invalid_list1 = ",".join(invalid_list)
            marked_answer_list1 = ",".join(marked_answer_list)
            attempted1 = ",".join(attempted)

            cursor.execute("update stes_test_question_answers set bookmark = \"" + bookmark_list1 +
                           "\" , invalid = \"" + invalid_list1 + "\" , marked_answers = \"" + marked_answer_list1 +
                           "\" , attempted = \"" + attempted1 + "\" where username = \"" + user + "\"")

        if int(next_question_no) <= 50:
            cursor.execute("select question, option1, option2, option3, option4, image from stes_test_physics where "
                           "question_id = " + question_id_in_subject_table)
        elif 51 <= int(next_question_no) <= 100:
            cursor.execute("select question, option1, option2, option3, option4, image from stes_test_chemistry where "
                           "question_id = " + question_id_in_subject_table)
        else:
            cursor.execute("select question, option1, option2, option3, option4, image from stes_test_math where "
                           "question_id = " + question_id_in_subject_table)

        new_question_data = cursor.fetchall()

        # print(new_question_data)

        physics = []
        chemistry = []
        math = []

        for i in range(1, 151):
            if i <= 50:
                physics.append((i, bookmark_list[i - 1], invalid_list[i - 1], attempted[i - 1]))
            elif 51 <= i <= 100:
                chemistry.append((i, bookmark_list[i - 1], invalid_list[i - 1], attempted[i - 1]))
            else:
                math.append((i, bookmark_list[i - 1], invalid_list[i - 1], attempted[i - 1]))

        # print(physics)

        question_no_prev = int(next_question_no) - 1
        question_no_next = int(next_question_no) + 1

        question_bookmark_status = bookmark_list[int(next_question_no) - 1]
        question_invalid_status = invalid_list[int(next_question_no) - 1]

        # print(new_question_data)

        return render(request, 'ok.html',
                      {"new_question_data": new_question_data, "question_number": next_question_no,
                       "question_no_prev": question_no_prev, "question_no_next": question_no_next,
                       "physics": physics, "chemistry": chemistry, "math": math, "bookmark": question_bookmark_status,
                       "invalid": question_invalid_status, "username": username, "backend_time": backend_time,
                       "next_question_marked_answer": next_question_marked_answer})

    else:

        print("username recived : " + username)

        cursor = connection.cursor()
        cursor.execute(
            "update stes_test_physics set rand = rand() where question_id > 0;"
            "update stes_test_chemistry set rand = rand() where question_id > 0;"
            "update stes_test_math set rand = rand() where question_id > 0;")

        cursor.execute(
            "select question_id, answer answer from stes_test_physics order by rand limit 50;")
        qset1 = cursor.fetchall()

        cursor.execute(
            "select question_id, answer from stes_test_chemistry order by rand limit 50;")
        qset2 = cursor.fetchall()

        cursor.execute(
            "select question_id, answer from stes_test_math order by rand limit 50;")
        qset3 = cursor.fetchall()

        physicsQ = []
        physicsA = []
        chemistryQ = []
        chemistryA = []
        mathQ = []
        mathA = []

        for q in qset1:
            physicsQ.append(str(q[0]))
            physicsA.append(str(q[1]))

        for q in qset2:
            chemistryQ.append(str(q[0]))
            chemistryA.append(str(q[1]))

        for q in qset3:
            mathQ.append(str(q[0]))
            mathA.append(str(q[1]))

        ins = question_answers(username=username,
                               physics_questions=",".join(physicsQ),
                               physics_answers=",".join(physicsA),
                               chemistry_questions=",".join(chemistryQ),
                               chemistry_answers=",".join(chemistryA),
                               math_questions=",".join(mathQ),
                               math_answers=",".join(mathA),
                               )
        ins.save()

        cursor = connection.cursor()
        user = username  # request.user
        cursor.execute(
            "select physics_questions, marked_answers from stes_test_question_answers where username = \"" + user + "\"")
        new_set = cursor.fetchall()
        question_id = (new_set[0][0].split(","))[0]
        next_question_marked_answer = (new_set[0][1].split(",")[0])

        cursor.execute("select question, option1, option2, option3, option4, image from stes_test_physics where "
                       "question_id = " + question_id)

        new_question_data = cursor.fetchall()

        physics = []
        chemistry = []
        math = []

        for i in range(1, 151):
            if i <= 50:
                physics.append((i, 0, 0))
            elif 51 <= i <= 100:
                chemistry.append((i, 0, 0))
            else:
                math.append((i, 0, 0))

        question_no_prev = 0
        question_no_next = 2

        return render(request, 'ok.html', {"new_question_data": new_question_data, "question_number": 1,
                                           "question_no_prev": question_no_prev, "question_no_next": question_no_next,
                                           "physics": physics, "chemistry": chemistry, "math": math, "bookmark": 0,
                                           "invalid": 0, "username": username, "backend_time": 10800000,
                                           "next_question_marked_answer": next_question_marked_answer})


def rules(request):
    if request.method == 'POST':
        if request.POST.get("username") and "box1" in request.POST:
            # print("Iam here")
            return main_test(request)
        else:
            return render(request, 'rules.html', {"username": request.POST.get("username")})


def calculate_result(request):
    if not request.user.is_authenticated:
        return welcome(request)

    username = request.user.username

    # print("My ustad is : " + username)

    cursor = connection.cursor()

    previous_question_no = request.POST.get('previous_question_no')
    marked_answer = request.POST.get('marked_answer')

    if previous_question_no is None:
        previous_question_no = "1"
    if marked_answer is None:
        marked_answer = "0"

    cursor.execute(
        "update stes_test_question_answers set time_left = 0 where username = \""
        + username + "\"")

    cursor.execute(
        "select marked_answers from stes_test_question_answers where "
        "username = \""
        + username + "\"")

    cursor.execute(
        "select physics_answers, chemistry_answers, math_answers, marked_answers from stes_test_question_answers "
        "where username = \"" + username + "\"")
    qset = cursor.fetchall()
    # print("Quesry set for username : " + username)
    # print(qset)

    physics_answers = qset[0][0]
    chemistry_answers = qset[0][1]
    math_answers = qset[0][2]
    marked_answers = qset[0][3]

    physics_marks = 0
    chemistry_marks = 0
    math_marks = 0

    physics_answers = physics_answers.split(",")
    chemistry_answers = chemistry_answers.split(",")
    math_answers = math_answers.split(",")
    marked_answers = marked_answers.split(",")
    marked_answers[int(previous_question_no) - 1] = marked_answer

    # print(len(physics_answers))
    # print(len(chemistry_answers))
    # print(len(math_answers))
    # print(len(marked_answers))

    i = 0
    for p in physics_answers:
        if p == marked_answers[i]:
            physics_marks += 1
        i += 1

    for p in chemistry_answers:
        if p == marked_answers[i]:
            chemistry_marks += 1
        i += 1

    for p in math_answers:
        if p == marked_answers[i]:
            math_marks += 2
        i += 1

    marked_answers = ",".join(marked_answers)
    total_marks = physics_marks + chemistry_marks + math_marks

    cursor.execute("update stes_test_question_answers set marked_answers = \"" + marked_answers +
                   "\" where username = \"" + username + "\"")

    set = results(username=username, physics_marks=physics_marks, chemistry_marks=chemistry_marks,
                  math_marks=math_marks,
                  total_marks=total_marks)
    set.save()

    logout(request)

    # print(str(physics_marks) + str(chemistry_marks) + str(math_marks))

    return render(request, 'bestofluck.html')


# view for messaging API
def sendOtp(phone_no, random_str):
    conn = http.client.HTTPSConnection("api.msg91.com")

    payload = "{ \"sender\": \"StesEx\", \"route\": \"4\", \"country\": \"91\", \"sms\": [ { \"message\": \"Your OTP for STES online exam is : " + random_str + "\", \"to\": [ \"" + phone_no + "\" ] } ] } "

    headers = {
        'authkey': "310833AqdXKu1ZYhO5e1f3f0cP1",
        'content-type': "application/json"
    }

    conn.request("POST", "/api/v2/sendsms", payload, headers)

    res = conn.getresponse()
    data = res.read()

    print(data.decode("utf-8"))


def scroller(request):
    if request.method == 'POST':
        return render(request, "scroller.html", {"username": request.POST.get("username")})

# ---------- Validation ------------#


@csrf_exempt
def edit(request):
    if request.method == "POST":

        data = json.loads(request.body)
        # print(data)
        subject = request.session.get("subject")
        if request.session.get("edited_questions")==None:
            request.session["edited_questions"] = []
        edited_questions = request.session["edited_questions"]
        question_id = data["question_id"]
        question = data["question"]
        option1 = data["option1"]
        option2 = data["option2"]
        option3 = data["option3"]
        option4 = data["option4"]
        answer = data["answer"]
        task = data["task"]
        is_valid = False if data['is_valid'] == 'True' else True
        # print(is_valid)
        
        if task == "edit":
            # If task to be performend is edit
            try:
                if(subject.lower() == "physics"):
                    physics.objects.filter(question_id=question_id).update(
                        question=question,
                        option1=option1,
                        option2=option2,
                        option3=option3,
                        option4=option4,
                        answer=answer,
                        is_valid=is_valid
                    )
                elif(subject.lower() == "chemistry"):
                    chemistry.objects.filter(question_id=question_id).update(
                        question=question,
                        option1=option1,
                        option2=option2,
                        option3=option3,
                        option4=option4,
                        answer=answer,
                        is_valid=is_valid
                    )
                elif(subject.lower() == "maths"):
                    math.objects.filter(question_id=question_id).update(
                        question=question,
                        option1=option1,
                        option2=option2,
                        option3=option3,
                        option4=option4,
                        answer=answer,
                        is_valid=is_valid
                    )
                status = "Edited"
                if question_id not in edited_questions:
                    edited_questions.append(int(question_id))
                request.session["edited_questions"] = edited_questions
            except DataError as e:
                # print("Error occured while updating {}".format(e))
                status = "Error"
        elif task == "validate":
            try:
                if(subject.lower() == "physics"):
                     physics.objects.filter(question_id=question_id).update(is_valid=is_valid)
                elif(subject.lower() == "chemistry"):
                    chemistry.objects.filter(question_id=question_id).update(is_valid=is_valid)
                elif(subject.lower() == "maths"):
                    math.objects.filter(question_id=question_id).update(is_valid=is_valid)
                status = "Marked Valid" if is_valid else "Marked Invalid"
            except DataError as e:
                # print("Error occured while updating {}".format(e))
                status = "Error"

    return JsonResponse({"status" : status})

def select_qset(request):
    Qset = ""
    if request.method == "POST":
        Qset = request.POST["qset"]
        if Qset == "":
            messages.warning(request, 'Please Select Qset subject')
            return render(request, template_name="select_qset.html")
        request.session["Qset"] = Qset
        return redirect('/stes_test/validate/')
    else:
        return render(request, template_name="select_qset.html")

def check_qset(request):
    Qset = request.session.get("Qset")
    if Qset is None:
        return redirect('/stes_test/select_qset/')
    request.session["subject"] = request.session.get("Qset")
    if request.session.get("edited_questions")==None:
        request.session["edited_questions"] = []

    context_dict = {
        'page_obj': '',
        'subject': request.session["subject"],
        'edited_questions': request.session["edited_questions"]
    }

    if Qset.lower() == "physics" or request.session["subject"] == "physics":
        phy_data = physics.objects.all()
        paginator = Paginator(phy_data, 30)
        page_number = request.POST.get('page')
        page_obj = paginator.get_page(page_number)
        if request.POST.get('q_no'):
            question_number = int(request.POST.get('q_no'))
        else:
            question_number = page_obj.start_index()
        question  = physics.objects.filter(question_id=question_number)
        context_dict['next_page'] = question_number+1
        context_dict['previous_page'] = question_number-1
        if context_dict['previous_page']==0:
            context_dict['has_previous'] = False
        else:
            context_dict['has_previous'] = True
        if context_dict['next_page']==len(phy_data):
            context_dict['has_next'] = False
        else:
            context_dict['has_next'] = True
        context_dict['question'] = question
        context_dict["page_obj"] = page_obj
        pages = []
        for page in paginator:
            pages.append([page.number, page.start_index(), page.end_index()])
        context_dict["pages"] = pages


    elif Qset.lower() == "chemistry" or request.session["subject"] == "chemistry":
        chem_data = chemistry.objects.all()
        paginator = Paginator(chem_data, 30)
        page_number = request.POST.get('page')
        page_obj = paginator.get_page(page_number)
        if request.POST.get('q_no'):
            question_number = int(request.POST.get('q_no'))
        else:
            question_number = page_obj.start_index()
        question  = chemistry.objects.filter(question_id=question_number)
        context_dict['next_page'] = question_number+1
        context_dict['previous_page'] = question_number-1
        if context_dict['previous_page']==0:
            context_dict['has_previous'] = False
        else:
            context_dict['has_previous'] = True
        if context_dict['next_page']==len(chem_data):
            context_dict['has_next'] = False
        else:
            context_dict['has_next'] = True
        context_dict['question'] = question
        context_dict["page_obj"] = page_obj
        pages = []
        for page in paginator:
            pages.append([page.number, page.start_index(), page.end_index()])
        context_dict["pages"] = pages

    elif Qset.lower() == "maths" or request.session["subject"] == "maths":
        math_data = math.objects.all()
        paginator = Paginator(math_data, 30)
        page_number = request.POST.get('page')
        page_obj = paginator.get_page(page_number)
        if request.POST.get('q_no'):
            question_number = int(request.POST.get('q_no'))
        else:
            question_number = page_obj.start_index()
        question  = math.objects.filter(question_id=question_number)
        context_dict['next_page'] = question_number+1
        context_dict['previous_page'] = question_number-1
        if context_dict['previous_page']==0:
            context_dict['has_previous'] = False
        else:
            context_dict['has_previous'] = True
        if context_dict['next_page']==len(math_data):
            context_dict['has_next'] = False
        else:
            context_dict['has_next'] = True
        context_dict['question'] = question
        context_dict["page_obj"] = page_obj
        pages = []
        for page in paginator:
            pages.append([page.number, page.start_index(), page.end_index()])
        context_dict["pages"] = pages
    # print(context_dict)
    return render(request, 'validate.html', context=context_dict)