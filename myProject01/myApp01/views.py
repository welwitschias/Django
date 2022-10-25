from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http.response import JsonResponse, HttpResponse
from django.db.models import Q
from myApp01.models import Board, Comment
import urllib.parse
import math

# Create your views here.
UPLOAD_DIR = "C:/python/django/upload/"


def write_form(request):    # Controller 역할
    return render(request, 'board/write.html')


@csrf_exempt    # csrf 방식을 간단히 해제
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


# def list(request):    # 전체보기
#     boardList = Board.objects.all()
#     context = {'boardList': boardList}
#     return render(request, 'board/list.html', context)


def list(request):    # 전체보기 - 검색, 페이징
    page = request.GET.get('page', 1)
    word = request.GET.get('word', '')
    field = request.GET.get('field', 'title')

    # 페이징하기( 123[다음]  [이전]456[다음]  [이전]7 )
    if field == 'all':
        boardCount = Board.objects.filter(Q(title__contains=word) |
                                          Q(writer__contains=word) |
                                          Q(content__contains=word)).count()
    elif field == 'title':
        boardCount = Board.objects.filter(
            Q(title__contains=word)).count()
    elif field == 'writer':
        boardCount = Board.objects.filter(
            Q(writer__contains=word)).count()
    elif field == 'content':
        boardCount = Board.objects.filter(
            Q(content__contains=word)).count()
    else:
        boardCount = Board.objects.all().count()

    pageSize = 5  # 한 화면에 보이는 게시글 수
    blockPage = 3  # 보이는 페이지 수
    currentPage = int(page)

    start = (currentPage - 1) * pageSize
    totalPage = math.ceil(boardCount / pageSize)  # 게시글의 전체 페이지 수
    startPage = math.floor((currentPage - 1) / blockPage) * blockPage + 1
    endPage = startPage + blockPage - 1

    if endPage > totalPage:
        endPage = totalPage

    # 검색하기
    if field == 'all':
        boardList = Board.objects.filter(Q(title__contains=word) |
                                         Q(writer__contains=word) |
                                         Q(content__contains=word)).order_by('-idx')[start: start + pageSize]
    elif field == 'title':
        boardList = Board.objects.filter(
            Q(title__contains=word)).order_by('-idx')[start: start + pageSize]
    elif field == 'writer':
        boardList = Board.objects.filter(
            Q(writer__contains=word)).order_by('-idx')[start: start + pageSize]
    elif field == 'content':
        boardList = Board.objects.filter(
            Q(content__contains=word)).order_by('-idx')[start: start + pageSize]
    else:
        boardList = Board.objects.all().order_by(
            '-idx')[start: start + pageSize]

    context = {'boardList': boardList,
               'startPage': startPage,
               'blockPage': blockPage,
               'endPage': endPage,
               'totalPage': totalPage,
               'boardCount': boardCount,
               'currentPage': currentPage,
               'field': field,
               'word': word,
               'range': range(startPage, endPage+1)}
    return render(request, 'board/list.html', context)


def detail_idx(request):    # 상세보기 방법1
    id = request.GET['idx']
    dto = Board.objects.get(idx=id)
    dto.hit_up()
    dto.save()

    commentList = Comment.objects.filter(board_idx=id).order_by('-idx')
    return render(request, 'board/detail.html', {'dto': dto, 'commentList': commentList})


def detail(request, board_idx):    # 상세보기 방법2
    id = board_idx
    dto = Board.objects.get(idx=id)
    dto.hit_up()
    dto.save()
    
    commentList = Comment.objects.filter(board_idx=id).order_by('-idx')
    return render(request, 'board/detail.html', {'dto': dto, 'commentList': commentList})


def update_form(request, board_idx):    # 수정하기 양식
    dto = Board.objects.get(idx=board_idx)
    return render(request, 'board/update.html', {'dto': dto})


@csrf_exempt
def update(request):    # 수정하기
    id = request.POST['idx']
    dto = Board.objects.get(idx=id)
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
                       #    idx=request.POST['idx'],
                       writer=request.POST['writer'],
                       title=request.POST['title'],
                       content=request.POST['content'],
                       hit=hitcount,
                       filename=fname,
                       filesize=fsize)
    update_dto.save()

    return redirect('/list')


def delete(request, board_idx):    # 삭제하기
    dto = Board.objects.get(idx=board_idx)
    dto.delete()
    return redirect('/list')


def download_count(request):    # 다운로드 횟수
    id = request.GET['idx']
    dto = Board.objects.get(idx=id)
    dto.down_up()
    dto.save()
    count = dto.down
    return JsonResponse({'idx': id, 'count': count})


def download(request):    # 다운로드
    id = request.GET['idx']
    dto = Board.objects.get(idx=id)
    path = UPLOAD_DIR + dto.filename
    filename = urllib.parse.quote(dto.filename)
    with open(path, 'rb') as file:
        response = HttpResponse(
            file.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = "attachment;filename*=UTF-8''{0}".format(
            filename)
    return response


@csrf_exempt
def comment_insert(request):    # 댓글
    id = request.POST['idx']
    dto = Comment(
        board_idx=id, writer='loginUserId', content=request.POST['content'])
    dto.save()
    return redirect('/detail_idx?idx='+id)
