from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse, HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator
from myApp02.models import Board
import math
import urllib.parse

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
    field = request.GET.get('field', 'title')

    if field == 'all':
        boardCount = Board.objects.filter(Q(writer__contains=word) |
                                          Q(title__contains=word) |
                                          Q(content__contains=word)).count()
    elif field == 'writer':
        boardCount = Board.objects.filter(Q(writer__contains=word)).count()
    elif field == 'title':
        boardCount = Board.objects.filter(Q(title__contains=word)).count()
    elif field == 'content':
        boardCount = Board.objects.filter(Q(content__contains=word)).count()
    else:
        boardCount = Board.objects.all().count()

    pageSize = 5
    blockPage = 3
    currentPage = int(page)

    start = (currentPage - 1) * pageSize
    totalPage = math.ceil(boardCount / pageSize)
    startPage = math.floor((currentPage - 1) / blockPage) * blockPage + 1
    endPage = startPage + blockPage - 1

    if endPage > totalPage:
        endPage = totalPage

    if field == 'all':
        boardList = Board.objects.filter(Q(writer__contains=word) |
                                         Q(title__contains=word) |
                                         Q(content__contains=word)).order_by('-id')[start: start + pageSize]
    elif field == 'writer':
        boardList = Board.objects.filter(
            Q(writer__contains=word)).order_by('-id')[start: start + pageSize]
    elif field == 'title':
        boardList = Board.objects.filter(
            Q(title__contains=word)).order_by('-id')[start: start + pageSize]
    elif field == 'content':
        boardList = Board.objects.filter(
            Q(content__contains=word)).order_by('-id')[start: start + pageSize]
    else:
        boardList = Board.objects.all().order_by(
            '-id')[start: start + pageSize]

    context = {'startPage': startPage,
               'blockPage': blockPage,
               'endPage': endPage,
               'totalPage': totalPage,
               'boardCount': boardCount,
               'boardList': boardList,
               'currentPage': currentPage,
               'field': field,
               'word': word,
               'range': range(startPage, endPage+1)}
    return render(request, 'board/list.html', context)


def list_page(request):
    page = request.GET.get('page', 1)
    word = request.GET.get('word', '')

    boardCount = Board.objects.filter(Q(writer__contains=word) |
                                      Q(title__contains=word) |
                                      Q(content__contains=word)).count()
    boardList = Board.objects.filter(Q(writer__contains=word) |
                                     Q(title__contains=word) |
                                     Q(content__contains=word)).order_by('-id')

    # 페이징 처리
    pageSize = 5
    paginator = Paginator(boardList, pageSize)
    pageList = paginator.get_page(page)

    context = {'pageList': pageList,
               'page': page,
               'word': word,
               'boardCount': boardCount}
    return render(request, 'board/list_page.html', context)


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
