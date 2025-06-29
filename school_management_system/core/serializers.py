from rest_framework import serializers
from .models import (
    SchoolConfiguration,
    AcademicYear,
    AcademicPeriod,
    Level,
    GradeLevel,
    Section,
    Subject,
    GradingScale,
    GradeValue,
    SubjectAssignment
)

class SchoolConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolConfiguration
        fields = '__all__'

class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = '__all__'

class AcademicPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicPeriod
        fields = '__all__'

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = '__all__'

class GradeLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeLevel
        fields = '__all__'

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class GradingScaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradingScale
        fields = '__all__'

class GradeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeValue
        fields = '__all__'

class SubjectAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectAssignment
        fields = '__all__'
