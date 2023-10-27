from rest_framework import generics, status, permissions
from rest_framework.authentication import *
from rest_framework.response import Response
from rest_framework.views import APIView
from . import serializers, models
from . permissions import IsOwner
from django.core.mail import send_mail
from django.utils import timezone

class NoteAddView(generics.CreateAPIView):
    queryset = models.Note.objects.all()
    serializer_class = serializers.NoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)


class NoteListView(generics.ListAPIView):
    queryset = models.Note.objects.all()
    serializer_class = serializers.NoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)

class NoteDetailView(generics.RetrieveAPIView):
    queryset = models.Note.objects.all()
    serializer_class = serializers.NoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)

class NoteUpdateView(generics.UpdateAPIView):
    queryset = models.Note.objects.all()
    serializer_class = serializers.NoteSerializer
    permission_class = [permissions.IsAuthenticated, IsOwner]
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)

class NoteDeleteView(generics.DestroyAPIView):
    queryset = models.Note.objects.all()
    serializer_class = serializers.NoteSerializer
    permission_class = [permissions.IsAuthenticated, IsOwner]
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)

class LatestNotesView(generics.ListAPIView):
    queryset = models.Note.objects.all().order_by('-created_time')
    serializer_class = serializers.NoteSerializer
    permission_class = [permissions.IsAuthenticated]
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)

class UnfinishedNotesView(generics.ListAPIView):
    queryset = models.Note.objects.filter(done=False)
    serializer_class = serializers.NoteSerializer
    permission_class = [permissions.IsAuthenticated]
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)

class OverdueNotesView(generics.ListAPIView):
    queryset = models.Note.objects.filter(due_date__lt=timezone.now())
    serializer_class = serializers.NoteSerializer
    permission_class = [permissions.IsAuthenticated]
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)

class DoneNotesView(generics.ListAPIView):
    queryset = models.Note.objects.filter(done=True)
    serializer_class = serializers.NoteSerializer
    permission_class = [permissions.IsAuthenticated]
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)

class SortedNotesView(generics.ListAPIView):
    queryset = models.Note.objects.all()
    serializer_class = serializers.NoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)

    def get_queryset(self):
        queryset = super().get_queryset()

        # Get sorting criteria from query parameters, with created_time the default
        sort_by = self.request.query_params.get('sort_by', 'created_time')

        # Sort notes based on criteria
        if sort_by == 'due_date':
            queryset = queryset.order_by('due_date')
        elif sort_by == 'priority':
            queryset = queryset.order_by('priority')
        elif sort_by == 'created_time':
            queryset = queryset.order_by('created_time')

        return queryset


class ShareNotesView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)

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
        send_mail(subject, message, 'ayera4test@gmail.com', [recipient_email])

        return Response({"message": "Notes shared via email."})

class SetReminderView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)

    def post(self, request, note_id):
        try:
            # Retrieve the note
            note = models.Note.objects.get(id=note_id)
            serializer = serializers.NoteSerializer(note)

            # Get the reminder time (in minutes) from the request
            reminder_minutes = request.data.get("reminder_minutes")
            recipient_email = request.data.get("recipient_email")

            # Calculate the reminder time
            reminder_time = timezone.now() + timezone.timedelta(minutes=reminder_minutes)

            # Compose the email message
            subject = f"Reminder for Note: {note.title}"
            message = f"Here is a reminder for your note:\n\n"
            message += f"Title: {note.title}\n"
            message += f"Content: {note.content}\n"
            message += f"Due Date: {note.due_date}\n"
            message += f"Priority: {note.priority}\n"
            message += f"Created Time: {note.created_time}\n"
            message += f"Reminder Time: {reminder_time}\n"

            # Send the email reminder
            send_mail(subject, message, 'ayera4test@gmail.com', [recipient_email])

            return Response({"message": "Email reminder set."})
        except Exception as e:
            return Response({"message": str(e)})

