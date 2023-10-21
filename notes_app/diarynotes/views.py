from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from . import serializers, models
from .permissions import IsOwner
from django.contrib.auth import authenticate, get_user_model, update_session_auth_hash
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils import timezone
import csv
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from djangocsv import render_to_csv_repsonse


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UserLoginView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserLoginSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        email = data.get('email')
        password = data.get('password')
        user = None
        if '@' in email:
            try:
                user = User.objects.get(email=email)
            except ObjectDoesNotExist:
                return Response({'error': 'User does not exist!'}, status=status.HTTP_404_NOT_FOUND)

        if not user:
            user = authenticate(username=email, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user_id': user.pk, 'email': user.email}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class UserLogoutView(APIView):
    #permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        #Get the user's token
        #token, _ = Token.objects.get_or_create(user=request.user)
        #token, _ = Token.objects.get_or_create(user=request.data)
        try:
            request.user.auth_token.delete()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        """
        if token:
            try:
                # Expire the token
                token.delete()
                return Response({'message': 'User Successfully logged out'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'error': 'No token detected'}, status=status.HTTP_404_NOT_FOUND)
        """


class PasswordResetRequestView(APIView):
    serializer_class = serializers.PasswordResetSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = get_user_model().objects.filter(email=email).first()
        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"https://example.com/reset-password/{uid}/{token}/"
            subject = 'Password Reset Request'
            message = f'You can Reset your password by clicking this link: {reset_link}'
            from_email = 'noreply@example.com'
            recipient_list = [email]

            send_mail(subject, message, from_email, recipient_list)

        return Response({'message': 'Password reset email sent if the email exists'})

class PasswordResetConfirmView(APIView):
    serializer_class = serializers.PasswordResetConfirmSerializer

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_user_model().objects.get(pk=uid)

            if default_token_generator.check_token(user, token):
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)

                new_password = serializer.validated_data['new_password']
                user.set_password(new_password)
                user.save()

                return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            return Response({'message': 'Invalid user or token'}, status=status.HTTP_400_BAD_REQUEST)

class NoteAddView(generics.CreateAPIView):
    queryset = models.Note.objects.all()
    serializer_class = serializers.NoteSerializer
    #permission_classes = [permissions.IsAuthenticated]

class NoteListView(generics.ListAPIView):
    queryset = models.Note.objects.all()
    serializer_class = serializers.NoteSerializer
    #permission_classes = [permissions.IsAuthenticated]

class NoteDetailView(generics.RetrieveAPIView):
    queryset = models.Note.objects.all()
    serializer_class = serializers.NoteSerializer
    #permission_classes = [permissions.IsAuthenticated]

class NoteUpdateView(generics.UpdateAPIView):
    queryset = models.Note.objects.all()
    serializer_class = serializers.NoteSerializer
    #permission_class = [permissions.is_authenticated, IsOwner]

class NoteDeleteView(generics.DestroyAPIView):
    queryset = models.Note.objects.all()
    serializer_class = serializers.NoteSerializer
    #permission_class = [permissions.is_authenticated, IsOwner]2

class LatestNotesView(generics.ListAPIView):
    queryset = models.Note.objects.all().order_by('-created_time')
    serializer_class = serializers.NoteSerializer
    #permission_class = [permissions.IsAuthenticated]

class UnfinishedNotesView(generics.ListAPIView):
    queryset = models.Note.objects.filter(status='unfinished')
    serializer_class = serializers.NoteSerializer
    # permission_class = [permissions.IsAuthenticated]

class OverdueNotesView(generics.ListAPIView):
    queryset = models.Note.objects.filter(due_date__lt=timezone.now(), status='overdue')
    serializer_class = serializers.NoteSerializer
    # permission_class = [permissions.IsAuthenticated]

class DoneNotesView(generics.ListAPIView):
    queryset = models.Note.objects.filter(status='done')
    serializer_class = serializers.NoteSerializer
    # permission_class = [permissions.IsAuthenticated]

class SortedNotesView(generics.ListAPIView):
    queryset = models.Note.objects.all()
    serializer_class = serializers.NoteSerializer
    #permission_class = [IsAuthenticated]

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

