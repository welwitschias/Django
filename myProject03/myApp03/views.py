from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse, HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator
from myApp03.models import Board, Comment, Forecast
from myApp03 import bigdataProcess
import urllib.parse
from .forms import UserForm
from django.contrib.auth import authenticate, login
from django.db.models.aggregates import Count
import pandas as pd
from django.contrib.auth.decorators import login_required

# Create your views here.
UPLOAD_DIR = "C:/python/django/upload/"


def base(request):
    return render(request, 'base.html')


@login_required(login_url="/login")
def insert_form(request):   # 로그인 된 사용자만 사용할 수 있도록 설정
    return render(request, 'board/insert.html')


@csrf_exempt
def insert(request):
    fname = ''
    fsize = 0

    if 'file' in request.FILES:
        file = request.FILES['file']
        fname = file.name
        fsize = file.size

        fp = open('%s%s' % (UPLOAD_DIR, fname), 'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()

    dto = Board(writer=request.user,
                title=request.POST['title'],
                content=request.POST['content'],
                filename=fname,
                filesize=fsize)
    dto.save()
    return redirect('/list')


def list(request):
    page = request.GET.get('page', 1)
    word = request.GET.get('word', '')

    boardCount = Board.objects.filter(Q(writer__username__contains=word) |
                                      Q(title__contains=word) |
                                      Q(content__contains=word)).count()
    
    boardList = Board.objects.filter(Q(writer__username__contains=word) |
                                     Q(title__contains=word) |
                                     Q(content__contains=word)).order_by('-id')

    pageSize = 5
    paginator = Paginator(boardList, pageSize)
    pageList = paginator.get_page(page)
    rowNo = boardCount - (int(page)-1) * pageSize

    context = {'pageList': pageList,
               'boardCount': boardCount,
               'page': page,
               'word': word,
               'rowNo': rowNo}
    return render(request, 'board/list.html', context)


def download_count(request):
    id = request.GET['id']
    dto = Board.objects.get(id=id)
    dto.down_up()
    dto.save()
    count = dto.down
    return JsonResponse({'id': id, 'count': count})


def download(request):
    id = request.GET['id']
    dto = Board.objects.get(id=id)
    path = UPLOAD_DIR + dto.filename
    filename = urllib.parse.quote(dto.filename)
    with open(path, 'rb') as file:
        response = HttpResponse(
            file.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = "attachment;filename*=UTF-8''{0}".format(
            filename)
    return response


def detail(request, board_id):
    dto = Board.objects.get(id=board_id)
    dto.hit_up()
    dto.save()

    context = {'dto': dto}
    return render(request, 'board/detail.html', context)


@login_required(login_url="/login")
def update_form(request, board_id):
    dto = Board.objects.get(id=board_id)
    return render(request, 'board/update.html', {'dto': dto})


@csrf_exempt
def update(request):
    id = request.POST['id']
    dto = Board.objects.get(id=id)
    fname = dto.filename
    fsize = dto.filesize
    hitcount = dto.hit

    if 'file' in request.FILES:
        file = request.FILES['file']
        fname = file.name
        fsize = file.size

        fp = open('%s%s' % (UPLOAD_DIR, fname), 'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()

    update_dto = Board(id,
                       writer=request.user,
                       title=request.POST['title'],
                       content=request.POST['content'],
                       hit=hitcount,
                       filename=fname,
                       filesize=fsize)
    update_dto.save()
    return redirect('/list')


@login_required(login_url="/login")
def delete(request, board_id):
    dto = Board.objects.get(id=board_id)
    dto.delete()
    return redirect('/list')


@csrf_exempt
@login_required(login_url="/login")
def comment_insert(request):
    id = request.POST['id']
    board = get_object_or_404(Board, pk=id)
    dto = Comment(board=board,
                  writer=request.user,
                  content=request.POST['comment'])
    dto.save()
    return redirect('/detail/'+id)


def signup(request):    # 회원가입
    if request.method == "POST":    # 회원가입 성공
        form = UserForm(request.POST)
        if form.is_valid():
            print('signup POST valid')
            form.save()

            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)

            return redirect('/')
        else:
            print('signup POST unvalid')

    else:   # 회원가입 폼으로 이동
        form = UserForm()
    return render(request, 'common/signup.html', {'form': form})


def melon(request):
    datas = []
    bigdataProcess.melon_crawling(datas)
    return render(request, 'bigdata/melon_chart.html', {'datas': datas})


def weather(request):
    last_date = Forecast.objects.values('tmef').order_by('-tmef')[:1]
    weather = {}
    bigdataProcess.weather_crawling(last_date, weather)

    # insert db
    for i in weather:
        for j in weather[i]:
            dto = Forecast(city=i, tmef=j[0], wf=j[1], tmn=j[2], tmx=j[3])
            dto.save()

    # 부산 select
    result = Forecast.objects.filter(city='부산')
    result1 = Forecast.objects.filter(city='부산').values(
        'wf').annotate(dcount=Count('wf')).values('dcount', 'wf')

    # print sql
    print("-"*100)
    print('result :', str(result.query))
    print("-"*100)
    print('result1 :', str(result1.query))
    print("-"*100)

    df = pd.DataFrame(result1)
    image_dic = bigdataProcess.weather_make_chart(result, df.wf, df.dcount)

    return render(request, 'bigdata/weather_chart.html', {'img_data': image_dic})
