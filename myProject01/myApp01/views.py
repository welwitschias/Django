from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect

from myApp01.models import Board

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


def list(request):    # 전체보기
    boardList = Board.objects.all()
    context = {'boardList': boardList}
    return render(request, 'board/list.html', context)


def detail_idx(request):    # 상세보기 방법1
    id = request.GET['idx']
    dto = Board.objects.get(idx=id)
    dto.hit_up()
    dto.save()
    return render(request, 'board/detail.html', {'dto': dto})


def detail(request, board_idx):    # 상세보기 방법2
    id = board_idx
    dto = Board.objects.get(idx=id)
    dto.hit_up()
    dto.save()
    return render(request, 'board/detail.html', {'dto': dto})


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
