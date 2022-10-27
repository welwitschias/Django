from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse, HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator
from myApp03.models import Board, Comment
from myApp03 import bigdataProcess
import urllib.parse
from .forms import UserForm
from django.contrib.auth import authenticate, login

# Create your views here.
UPLOAD_DIR = "C:/python/django/upload/"


def base(request):
    return render(request, 'base.html')


def insert_form(request):
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

    dto = Board(writer=request.POST['writer'],
                title=request.POST['title'],
                content=request.POST['content'],
                filename=fname,
                filesize=fsize)
    dto.save()
    return redirect('/list')


def list(request):
    page = request.GET.get('page', 1)
    word = request.GET.get('word', '')

    boardCount = Board.objects.filter(Q(writer__contains=word) |
                                      Q(title__contains=word) |
                                      Q(content__contains=word)).count()
    boardList = Board.objects.filter(Q(writer__contains=word) |
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
                       writer=request.POST['writer'],
                       title=request.POST['title'],
                       content=request.POST['content'],
                       hit=hitcount,
                       filename=fname,
                       filesize=fsize)
    update_dto.save()
    return redirect('/list')


def delete(request, board_id):
    dto = Board.objects.get(id=board_id)
    dto.delete()
    return redirect('/list')


@csrf_exempt
def comment_insert(request):
    id = request.POST['id']
    dto = Comment(board_id=id, writer='joker', content=request.POST['comment'])
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
    bigdataProcess.melon_crawling()
    return render(request, 'bigdata/melon.html')
