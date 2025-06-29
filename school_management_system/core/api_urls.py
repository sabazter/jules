from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SchoolConfigurationViewSet,
    AcademicYearViewSet,
    AcademicPeriodViewSet,
    LevelViewSet,
    GradeLevelViewSet,
    SectionViewSet,
    SubjectViewSet,
    GradingScaleViewSet,
    GradeValueViewSet,
    SubjectAssignmentViewSet
)

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'school-configurations', SchoolConfigurationViewSet, basename='schoolconfiguration')
router.register(r'academic-years', AcademicYearViewSet, basename='academicyear')
router.register(r'academic-periods', AcademicPeriodViewSet, basename='academicperiod')
router.register(r'levels', LevelViewSet, basename='level')
router.register(r'grade-levels', GradeLevelViewSet, basename='gradelevel')
router.register(r'sections', SectionViewSet, basename='section')
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'grading-scales', GradingScaleViewSet, basename='gradingscale')
router.register(r'grade-values', GradeValueViewSet, basename='gradevalue')
router.register(r'subject-assignments', SubjectAssignmentViewSet, basename='subjectassignment')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
