from drf_yasg import openapi

api_info = openapi.Info(
    title="DiaryNotes API",
    default_version='v1',
    description="API documentation for DiaryNotes",
    terms_of_service="Reach out to us for more information",
    contact=openapi.Contact(email="myuo4anya@gmail.com"),
    license=openapi.License(name="MIT License"),
)
