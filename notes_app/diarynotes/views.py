from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from . import serializers, models
from . permissions import IsOwner
from django.core.mail import send_mail
from django.utils import timezone
import csv
from django.http import HttpResponse
from reportlab.pdfgen import canvas
#from djangocsv import render_to_csv_repsonse


class NoteAddView(generics.CreateAPIView):
    queryset = models.Note.objects.all()
    serializer_class = serializers.NoteSerializer
    permission_classes = [permissions.IsAuthenticated]

class NoteListView(generics.ListAPIView):
    queryset = models.Note.objects.all()
    serializer_class = serializers.NoteSerializer
    permission_classes = [permissions.IsAuthenticated]

class NoteDetailView(generics.RetrieveAPIView):
    queryset = models.Note.objects.all()
    serializer_class = serializers.NoteSerializer
    permission_classes = [permissions.IsAuthenticated]

class NoteUpdateView(generics.UpdateAPIView):
    queryset = models.Note.objects.all()
    serializer_class = serializers.NoteSerializer
    permission_class = [permissions.IsAuthenticated, IsOwner]

class NoteDeleteView(generics.DestroyAPIView):
    queryset = models.Note.objects.all()
    serializer_class = serializers.NoteSerializer
    permission_class = [permissions.IsAuthenticated, IsOwner]

class LatestNotesView(generics.ListAPIView):
    queryset = models.Note.objects.all().order_by('-created_time')
    serializer_class = serializers.NoteSerializer
    permission_class = [permissions.IsAuthenticated]

class UnfinishedNotesView(generics.ListAPIView):
    queryset = models.Note.objects.filter(unfinished=True)
    serializer_class = serializers.NoteSerializer
    permission_class = [permissions.IsAuthenticated]

class OverdueNotesView(generics.ListAPIView):
    queryset = models.Note.objects.filter(overdue=True)
    serializer_class = serializers.NoteSerializer
    permission_class = [permissions.IsAuthenticated]

class DoneNotesView(generics.ListAPIView):
    queryset = models.Note.objects.filter(done=True)
    serializer_class = serializers.NoteSerializer
    permission_class = [permissions.IsAuthenticated]

class SortedNotesView(generics.ListAPIView):
    queryset = models.Note.objects.all()
    serializer_class = serializers.NoteSerializer
    permission_class = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        sort_by = self.request.query_params.get('sort_by', None)

        if sort_by == 'due_date':
            queryset = queryset.order_by('due_date')
        elif sort_by == 'priority':
            queryset = queryset.order_by('priority')
        elif sort_by == 'created_time':
            queryset = queryset.order_by('created_time')
        else:
            queryset = queryset.oredr_by('created_time')

        return queryset


class ExportNotesView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Add authentication and permissions as needed

    def post(self, request):
        # Retrieve all notes
        notes = models.Note.objects.all()
        serializer = serializers.NoteSerializer(notes, many=True)

        # Generate CSV
        data = [[note['title'], note['content'], note['due_date'], note['priority'], note['created_time']] for note in serializer.data]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="notes.csv"'

        writer = csv.writer(response)
        writer.writerow(["Title", "Content", "Due Date", "Priority", "Created Time"])
        writer.writerows(data)

        return response
"""
    def get(self, request):
        # Retrieve all notes
        notes = models.Note.objects.all()
        serializer = serializers.NoteSerializer(notes, many=True)

        # Generate PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="notes.pdf"'

        p = canvas.Canvas(response)
        p.drawString(100, 800, "List of Notes")
        data = [[note['title'], note['content'], note['due_date'], note['priority'], note['created_time']] for note in serializer.data]
        width, height = A4
        table = Table(data, colWidths=1.8 * inch, rowHeights=0.4 * inch)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        table.wrapOn(p, width, height)
        table.drawOn(p, 10, 650)
        p.showPage()
        p.save()

        return response
"""

class ShareNotesView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Add authentication and permissions as needed

    def post(self, request):
        # Retrieve all notes
        notes = models.Note.objects.all()
        serializer = serializers.NoteSerializer(notes, many=True)

        # Compose the email message
        subject = "Shared Notes"
        message = "Here are the notes you requested:\n\n"
        for note in serializer.data:
            message += f"Title: {note['title']}\n"
            message += f"Content: {note['content']}\n"
            message += f"Due Date: {note['due_date']}\n"
            message += f"Priority: {note['priority']}\n"
            message += f"Created Time: {note['created_time']}\n\n"

        recipient_email = request.data.get("recipient_email")

        # Send the email
        send_mail(subject, message, 'your_email@example.com', [recipient_email])

        return Response({"message": "Notes shared via email."})

class SetReminderView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Add authentication and permissions as needed

    def post(self, request, note_id):
        try:
            # Retrieve the note
            note = models.Note.objects.get(id=note_id)
            serializer = serializers.NoteSerializer(note)

            # Get the reminder time (in minutes) from the request
            reminder_minutes = request.data.get("reminder_minutes")

            # Calculate the reminder time
            reminder_time = timezone.now() + timezone.timedelta(minutes=reminder_minutes)

            # Compose the email message
            subject = f"Reminder for Note: {note.title}"
            message = f"Here is a reminder for your note:\n\n"
            message += f"Title: {note.title}\n"
            message += f"Content: {note.content}\n"
            message += f"Due Date: {note.due_date}\n"
            message += f"Priority: {note.priority}\n"
            message += f"Created Time: {note.created_time}\n\n"
            message += f"Reminder Time: {reminder_time}\n"

            # Send the email reminder
            send_mail(subject, message, 'your_email@example.com', [request.user.email])

            return Response({"message": "Email reminder set."})
        except models.Note.DoesNotExist:
            return Response({"message": "Note not found."})

#Ensure you replace `'your_email@example.com'` with the sender's email address. Also, make sure to provide a valid SMTP server configuration in your Django project's settings.

