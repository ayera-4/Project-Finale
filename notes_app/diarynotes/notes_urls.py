from django.urls import path
from . import views

urlpatterns = [
    path('category-add/', views.NoteCategoryView.as_view(), name='category-add'),
    path('note-add/', views.NoteAddView.as_view(), name='note-add'),
    path('note-list/', views.NoteListView.as_view(), name='note-list'),
    path('note-detail/<str:pk>/', views.NoteDetailView.as_view(), name='note-detail'),
    path('note-update/<str:pk>/', views.NoteUpdateView.as_view(), name='note-update'),
    path('note-delete/<str:pk>/', views.NoteDeleteView.as_view(), name='note-delete'),
    path('notes-latest/', views.LatestNotesView.as_view(), name='note-latest'),
    path('notes-unfinished/', views.UnfinishedNotesView.as_view(), name='note-unfinished'),
    path('notes-overdue/', views.OverdueNotesView.as_view(), name='note-overdue'),
    path('notes-done/', views.DoneNotesView.as_view(), name='note-done'),
    path('notes-sorted/', views.SortedNotesView.as_view(), name='note-done'),
    path('export/pdf/', views.ExportNotesView.as_view(), name='export-notes-pdf'),
    path('export/csv/', views.ExportNotesView.as_view(), name='export-notes-csv'),
    path('notes-share/', views.ShareNotesView.as_view(), name='share-notes'),
    path('set-reminder/<int:note_id>/', views.SetReminderView.as_view(), name='set-reminder'),


]