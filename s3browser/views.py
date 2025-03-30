import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from .operations import *
from accounts.decorators import login_is_required
"fetch the directories within the selected folder"


def get_folder_items(request, main_folder, sort_a_z):
    json_string = get_folder_with_items(main_folder, sort_a_z)
    return HttpResponse(json.dumps(json_string), content_type="application/json")


@csrf_exempt
def upload(request):
    file = request.FILES.get('file')
    upload_file(request.POST['loc'], file)
    return HttpResponse(json.dumps(file.name), content_type="application/json", status=200)


@csrf_exempt
def create_folder(request):
    create_folder_item(request.POST['loc'], request.POST['folder_name'])
    return HttpResponse(json.dumps("OK"), content_type="application/json", status=200)


@csrf_exempt
def download(request):
    file = request.GET.get('file')
    if file.startswith('/') == False:
        file = '/' + file
    result = download_file(file)
    response = HttpResponse(result['Body'].read())
    response['Content-Type'] = result['ContentType']
    response['Content-Length'] = result['ContentLength']
    response['Content-Disposition'] = 'attachment; filename=' + file
    response['Accept-Ranges'] = 'bytes'
    return response


@csrf_exempt
def rename_file(request):
    file_name = rename(request.POST['loc'], request.POST['file'], request.POST['new_name'])
    return HttpResponse(json.dumps(file_name), content_type="application/json", status=200)


@csrf_exempt
def paste_file(request):
    paste(request.POST['loc'], request.POST.getlist('file_list[]'))
    return HttpResponse(json.dumps("OK"), content_type="application/json", status=200)


@csrf_exempt
def move_file(request):
    move(request.POST['loc'], request.POST.getlist('file_list[]'))
    return HttpResponse(json.dumps("OK"), content_type="application/json", status=200)


@csrf_exempt
def delete_file(request):
    delete(request.POST.getlist('file_list[]'))
    return HttpResponse(json.dumps("OK"), content_type="application/json", status=200)


@login_is_required
def s3_input(request):
    print('s3_input', request.GET.get('folder'))
    folder = request.GET.get('folder')
    if folder is None:
        folder = "/input_folders/"
    if folder.startswith('/') == False:
        folder = '/' + folder
    file_list = get_folder_with_items(folder, "true")
    print(file_list)
    return render(
        request,
        "s3browser/input.html",
        {
            "files": file_list,
            "page_title": "S3 Input Files"
        }
    )

@login_is_required
def s3_output(request):
    print('s3_output', request.GET.get('folder'))
    folder = request.GET.get('folder')
    if folder is None:
        folder = "/output_folders/"
    if folder.startswith('/') == False:
        folder = '/' + folder
    file_list = get_folder_with_items(folder, "true")
    print(file_list)
    return render(
        request,
        "s3browser/output.html",
        {
            "files": file_list,
            "page_title": "S3 Ouput Files"
        }
    )
    
@login_is_required
def s3_download(request):
    print('s3_download')
    return download(request)


input_loc = '/input_folders/'
output_loc = '/output_folders/'

def create_project(project_name):
    # project_name = project_name.replace(" ", "_")
    try:
        create_folder_item(input_loc, project_name)
        create_folder_item(output_loc, project_name)
    except:
        pass


def create_workflow(project_name, workflow_name):
    # project_name = project_name.replace(" ", "_")
    # workflow_name = workflow_name.replace(" ", "_")
    try:
        create_folder_item(input_loc, project_name + "/" + workflow_name)
        create_folder_item(output_loc, project_name + "/" +workflow_name)
    except:
        pass
