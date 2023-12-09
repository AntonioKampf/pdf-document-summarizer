import os
from PyPDF2 import PdfReader
from django.http import FileResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from textwrap import wrap
from work.forms import FileUploadForm
from work.models import FileProject
from django.conf import settings
from work.summarazy import summarize_text_with_rake, summarize_text_advanced, model
from reportlab.pdfgen import canvas


def index(request):
    return render(request, 'work/index.html')


def create_pdf(file_info):
   response = HttpResponse(content_type='application/pdf')
   response['Content-Disposition'] = f'attachment; filename="{file_info["name"]}_summary.pdf"'

   c = canvas.Canvas(response)
   textobject = c.beginText()
   textobject.setTextOrigin(50, 750)
   textobject.setFont("Helvetica", 14)

   textobject.textLine(f"Name: {file_info['name']}")

   textobject.textLine("Keywords:")
   textobject.textLines("\n".join(wrap(file_info['keywords'], width=60)))

   textobject.textLine("Top Sentences:")
   textobject.textLines("\n".join(wrap(file_info['top_sentences'], width=60)))

   textobject.textLine("Result:")
   textobject.textLines("\n".join(wrap(file_info['result'], width=60)))

   c.drawText(textobject)
   c.showPage()
   c.save()

   return response


def write_info_txt(file_info):
    content = f"Name: {file_info['name']}\n"
    content += f"\nКлючевые слова: {file_info['keywords']}\n"
    content += f"\nКлассическое: {file_info['top_sentences']}\n"
    content += f"\nМашинное обучение: {file_info['result']}\n"

    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename={file_info["name"]}_summary.txt'
    return response


def project_view(request):
    project = FileProject.objects.all()
    file_info = []

    for file in project:
        file_extension = file.file.name.split(".")[-1].lower()
        if file_extension == 'pdf':
            file_path = os.path.join(settings.MEDIA_ROOT, str(file.file))
            try:
                pdf_reader = PdfReader(file_path)
                content = ""
                for page in pdf_reader.pages:
                    content += page.extract_text()
            except FileNotFoundError:
                content = "File not found"

            file_info.append(
                {
                    'id': file.id,
                    'name': str(file.file),
                    'content': content,
                })

    return render(request, 'work/project.html', {'file_info': file_info})


def output_summarazy(request, file_id=None):
    file = FileProject.objects.get(id=file_id)
    file_extension = file.file.name.split(".")[-1].lower()
    if file_extension == 'pdf':
        file_path = os.path.join(settings.MEDIA_ROOT, str(file.file))
        try:
            pdf_reader = PdfReader(file_path)
            content = ""
            for page in pdf_reader.pages:
                content += page.extract_text()
        except FileNotFoundError:
            content = "File not found"

        keywords = summarize_text_with_rake(content)

        top_sentences = summarize_text_advanced(content)

        result = model(content, num_sentences=3)

        file_info = {
            'id': file.id,
            'name': str(file.file),
            'keywords': str(keywords),
            'top_sentences': str(top_sentences),
            'result': str(result)
        }
    return render(request, 'work/project_summarazy.html', {'file_info': file_info})


def print_summarazy(request, file_id=None):
    file = FileProject.objects.get(id=file_id)
    file_extension = file.file.name.split(".")[-1].lower()
    if file_extension == 'pdf':
        file_path = os.path.join(settings.MEDIA_ROOT, str(file.file))
        try:
            pdf_reader = PdfReader(file_path)
            content = ""
            for page in pdf_reader.pages:
                content += page.extract_text()
        except FileNotFoundError:
            content = "File not found"

        keywords = summarize_text_with_rake(content)

        top_sentences = summarize_text_advanced(content)

        result = model(content, num_sentences=3)

        file_info = {
            'id': file.id,
            'name': str(file.file),
            'keywords': str(keywords),
            'top_sentences': str(top_sentences),
            'result': str(result)
        }
        return create_pdf(file_info)


def output_summarazy_txt(request, file_id=None):
    file = FileProject.objects.get(id=file_id)
    file_extension = file.file.name.split(".")[-1].lower()
    if file_extension == 'pdf':
        file_path = os.path.join(settings.MEDIA_ROOT, str(file.file))
        try:
            pdf_reader = PdfReader(file_path)
            content = ""
            for page in pdf_reader.pages:
                content += page.extract_text()
        except FileNotFoundError:
            content = "File not found"

        keywords = summarize_text_with_rake(content)
        top_sentences = summarize_text_advanced(content)
        result = model(content, num_sentences=3)

        file_info = {
            'id': file.id,
            'name': str(file.file),
            'keywords': str(keywords),
            'top_sentences': str(top_sentences),
            'result': str(result)
        }
        return write_info_txt(file_info)


def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save()
            return redirect('home')
    else:
        form = FileUploadForm()
    return render(request, 'work/index.html', {'form': form})


def delete_file(request, file_id):
    file_to_delete = FileProject.objects.get(pk=file_id)
    file_to_delete.file.delete()
    file_to_delete.delete()
    return redirect('home')


def download_file(request, file_id):
    file_object = get_object_or_404(FileProject, pk=file_id)
    response = FileResponse(file_object.file.open(), as_attachment=True)
    return response


def help_text(request):
    return render(request, 'work/help.html')
