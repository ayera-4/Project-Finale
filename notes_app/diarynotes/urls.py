from django.urls import path
from . import views, user_views

urlpatterns = [
    path('register/', user_views.UserRegistrationView.as_view(), name="user-registration"),
    path('login/', user_views.UserLoginView.as_view(), name="user-login"),
    path('logout/', user_views.UserLogoutView.as_view(), name="user-logout"),
    path('password-reset/', user_views.PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset/confirm/<str:uidb64>/<str:token>/', user_views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),

    path('note-add/', views.NoteAddView.as_view(), name='note-add'),
    path('note-list/', views.NoteListView.as_view(), name='note-list'),
    path('note-detail/<str:pk>/', views.NoteDetailView.as_view(), name='note-detail'),
    path('note-update/<str:pk>/', views.NoteUpdateView.as_view(), name='note-update'),
    path('note-delete/<str:pk>/', views.NoteDeleteView.as_view(), name='note-delete'),
    path('note-latest/', views.LatestNotesView.as_view(), name='note-latest'),
    path('note-unfinished/', views.UnfinishedNotesView.as_view(), name='note-unfinished'),
    path('note-overdue/', views.OverdueNotesView.as_view(), name='note-overdue'),
    path('note-done/', views.DoneNotesView.as_view(), name='note-done'),
    path('note-sort/', views.SortedNotesView.as_view(), name='note-done'),
    path('export/pdf/', views.ExportNotesView.as_view(), name='export-notes-pdf'),
    path('export/csv/', views.ExportNotesView.as_view(), name='export-notes-csv'),
    path('note-share/', views.ShareNotesView.as_view(), name='share-notes'),
    path('set-reminder/<int:note_id>/', views.SetReminderView.as_view(), name='set-reminder'),


]