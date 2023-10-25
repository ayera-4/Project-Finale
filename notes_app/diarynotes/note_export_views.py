from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from . import serializers, models
import csv
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from openpyxl import Workbook

class ExportCSVView(APIView):
    #permission_classes = [IsAuthenticated]
    #authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="list_of_notes.csv"'

        try:
            #Initiate writing to list_of_notes.csv
            notes_csv = csv.writer(response)

            # Define headers
            notes_csv.writerow(['Date', 'Priority', 'Category', 'Title', 'Content'])

            # Retrieve and add notes to the csv file
            notes = models.Note.objects.all()
            for note in notes:
                notes_csv.writerow([note.created_time, note.priority, note.category, note.title, note.content])

        except Exception:
            return Response({'Error':'CSV file export failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return response


class ExportPDFView(APIView):
    #permission_classes = [IsAuthenticated]
    #authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    def get(self, request):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="list_of_notes.pdf"'

        try:
            # Initiate writing to list_of_notes.pdf
            notes_pdf = canvas.Canvas(response)

            # Retrieve and add notes to the pdf file
            notes = models.Note.objects.all()
            for note in notes:
                notes_pdf.drawString(100, 700, f"Date: {note.created_time}")
                notes_pdf.drawString(100, 680, f"Priority: {note.priority}")
                notes_pdf.drawString(100, 660, f"Category: {note.category}")
                notes_pdf.drawString(100, 640, f"Title: {note.title}")
                notes_pdf.drawString(100, 620, f"Content: {note.content}")
                notes_pdf.showPage()

            #save pdf to response
            notes_pdf.save()

        except Exception:
            return Response({'Error':'PDF file export failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return response


class ExportExcelView(APIView):
    #permission_classes = [IsAuthenticated]
    #authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)

    def get(self, request):
        try:
            # Create an Excel workbook and worksheet
            notes_book = Workbook()
            notes_sheet = notes_book.active

            # Define column headers
            notes_sheet.append(["Date", "Priority", "Category", "Title", "Content"])

            # Retrieve and add notes to the worksheet
            notes = models.Note.objects.all()
            serializer = serializers.NoteSerializer(notes, many=True)
            for item in serializer.data:
                notes_sheet.append([item['created_time'], item['priority'], item['category'], item['title'], item['content']])

        except Exception:
            return Response({'Error': 'Excel file export failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Create an HttpResponse for Excel content
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = 'attachment; filename="list_of_notes.xlsx"'

        # Save the workbook to the response
        notes_xlsx = notes_book.save(response)
        response.write(notes_xlsx)

        return response