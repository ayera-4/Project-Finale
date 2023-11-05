#from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Note, CustomUser
from django.utils import timezone
from PyPDF2 import PdfReader
from openpyxl import load_workbook
import io
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

class DiaryNotesAPITestCase(APITestCase):

    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(username='tungauser', email='tungauser@example.com', password='tungapass')
        self.token = Token.objects.create(user=self.user)
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))

    """
    Below are test cases for the user related views
    """
    def test_user_registration_view(self):
        # Compose a POST request to register a new user
        data = {
            "email": "tungauser@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "tungapass"
        }
        response = self.client.post("/user/register/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Check if the response contains the user's data.

        self.assertIn("email", response.data)
        self.assertEqual(response.data["email"], "tungauser@example.com")

        self.assertIn("first_name", response.data)
        self.assertEqual(response.data["first_name"], "Test")

        self.assertIn("last_name", response.data)
        self.assertEqual(response.data["last_name"], "User")

    def test_user_login_view_with_existing_user(self):
        # Compose a POST request to log in an existing user
        data = {
            "email": "tungauser@example.com",
            "password": "tungapass"
        }
        response = self.client.post("/user/login/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the response content or structure as needed
        # For example, you can check if the response contains the user's data and a token.

        self.assertIn("token", response.data)
        self.assertEqual(response.data["user_id"], self.user.pk)
        self.assertEqual(response.data["email"], self.user.email)

    def test_user_logout_view(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        # Make a GET request to the UserLogoutView to log out the user
        response = self.client.get("/user/logout/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the response contains a success message.
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "User Successfully logged out")

    def test_password_reset_request_view(self):
        # Compose a POST request to request a password reset
        data = {
            "email": "tungauser@example.com"
        }
        response = self.client.post("/user/password-reset/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the response contains a success message.
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "Password reset email sent if the email exists")

    def test_password_reset_confirm_view_with_valid_data(self):
        # Compose a POST request to confirm a password reset
        data = {
            "new_password": "newpassword"
        }
        response = self.client.post(f"/api/password-reset-confirm/{self.uidb64}/{self.token}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the response contains a success message.
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "Password reset successfully")

        # Verify that the user's password has been updated
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword"))

    """
        Below are test cases for the notes related views
    """
    def test_create_note_endpoint(self):
        # Test the endpoint for creating a new note
        self.client.force_authenticate(user=self.user)
        data = {'title': 'Test Note', 'content': 'This is a test note', 'due_date': '2023-10-31', 'priority': 'High'}
        response = self.client.post('/note/note-add/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_view_notes_endpoint(self):
        # Test the endpoint for viewing all notes
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/note/note-list/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_view_one_note_endpoint(self):
        # Test the endpoint for viewing all notes
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/note/note-detail/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Note.objects.count(), 1)

    def test_update_note_endpoint(self):
        # Test the endpoint for updating a note
        self.client.force_authenticate(user=self.user)
        data = {'title': 'Updated Note'}
        response = self.client.put('/note/note-update/1/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Note.objects.count(), 1)

    def test_delete_note_endpoint(self):
        # Test the endpoint for deleting a note
        self.client.force_authenticate(user=self.user)
        response = self.client.delete('/note/note-delete/1/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_latest_notes_view(self):
        self.client.force_authenticate(user=self.user)

        # Make a GET request to the LatestNotesView
        response = self.client.get("/note/notes-latest/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #Check if the response is ordered by 'created_time' in descending order
        created_times = [note['created_time'] for note in response.data]
        self.assertEqual(created_times, sorted(created_times, reverse=True))

    def test_unfinished_notes_view(self):
        self.client.force_authenticate(user=self.user)

        # Make a GET request to the UnfinishedNotesView
        response = self.client.get("/note/notes-unfinished/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #Check if all notes in the response are unfinished
        for note in response.data:
            self.assertFalse(note['done'])

    def test_done_notes_view(self):
        self.client.force_authenticate(user=self.user)

        # Make a GET request to the UnfinishedNotesView
        response = self.client.get("/note/notes-done/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #Check if all notes in the response are unfinished
        for note in response.data:
            self.assertTrue(note['done'])

    def test_overdue_notes_view(self):
        self.client.force_authenticate(user=self.user)

        # Make a GET request to the OverdueNotesView
        response = self.client.get("/note/notes-overdue/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #Check if all notes in the response are overdue
        for note in response.data:
            self.assertTrue(note['due_date'] < timezone.now())

    def test_sorted_due_date_view(self):
        self.client.force_authenticate(user=self.user)

        # Make a GET request to the SortedNotesView with query parameters for sorting
        response = self.client.get("/note/notes-sorted/?sort_by=due_date")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #Check if notes are sorted by 'due_date'
        dates = [note['due_date'] for note in response.data]
        self.assertEqual(dates, sorted(dates))

    def test_sorted_created_time_view(self):
        self.client.force_authenticate(user=self.user)

        # Make a GET request to the SortedNotesView with query parameters for sorting
        response = self.client.get("/note/notes-sorted/?sort_by=created_time")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #Check if notes are sorted by 'created_time'
        times = [note['created_time'] for note in response.data]
        self.assertEqual(times, sorted(times))

    def test_sorted_priority_view(self):
        self.client.force_authenticate(user=self.user)

        # Make a GET request to the SortedNotesView with query parameters for sorting
        response = self.client.get("/note/notes-sorted/?sort_by=priority")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #Check if notes are sorted by 'priority'
        ranks = [note['priority'] for note in response.data]
        self.assertEqual(ranks, sorted(ranks))

    def test_share_notes_view(self):
        self.client.force_authenticate(user=self.user)

        # Compose a POST request to share notes via email
        data = {
            "recipient_email": "recipient@example.com"
        }
        response = self.client.post("/note/notes-share/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #check if the response contains a success message.
        self.assertEqual(response.data, {"message": "Notes shared via email."})

    def test_set_reminder_view(self):
        self.client.force_authenticate(user=self.user)

        note_id = 1  # Replace with the actual ID of the note
        # Compose a POST request to set an email reminder for a note
        data = {
            "reminder_minutes": 30,  # Set a reminder for 30 minutes from now
            "recipient_email": "recipient@example.com"
        }
        response = self.client.post(f"/note/set-reminder/{note_id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #check if the response contains a success message.
        self.assertEqual(response.data, {"message": "Email reminder set."})

    def test_export_csv_view(self):
        self.client.force_authenticate(user=self.user)

        # Make a GET request to the ExportCSVView
        response = self.client.get("/note/export/csv/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertTrue('attachment; filename="list_of_notes.csv"' in response['Content-Disposition'])

        # Check if the response contains CSV data.
        response_lines = response.content.decode('utf-8').split('\n')
        headers = response_lines[0].strip().split(',')
        self.assertEqual(headers, ['Date', 'Priority', 'Category', 'Title', 'Content'])

    def test_export_pdf_view(self):
        self.client.force_authenticate(user=self.user)

        # Make a GET request to the ExportPDFView
        response = self.client.get("/note/export/pdf/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue('attachment; filename="list_of_notes.pdf"' in response['Content-Disposition'])

        # Check if the response contains a valid PDF.
        try:
            pdf = PdfReader(response.content)
            # Check if the PDF has at least one page (your notes)
            self.assertGreaterEqual(pdf.getNumPages(), 1)
        except Exception as e:
            self.fail(f"Invalid PDF response: {e}")

    def test_export_excel_view(self):
        self.client.force_authenticate(user=self.user)

        # Make a GET request to the ExportExcelView
        response = self.client.get("/note/export/excel/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.assertTrue('attachment; filename="list_of_notes.xlsx"' in response['Content-Disposition'])

        # Check if the response contains a valid Excel file.
        try:
            # Load the Excel workbook from the response content
            notes_xlsx = load_workbook(filename=io.BytesIO(response.content))
            notes_sheet = notes_xlsx.active

            # Check if the worksheet contains at least one row of data (your notes)
            self.assertGreaterEqual(len(notes_sheet.rows), 2)
        except Exception as e:
            self.fail(f"Invalid Excel response: {e}")

