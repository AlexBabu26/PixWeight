from rest_framework import serializers
from .models import EstimationSession, Question, Answer

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "order", "text", "answer_type", "unit", "options", "required"]

class AnswerSerializer(serializers.ModelSerializer):
    question_id = serializers.UUIDField(source="question.id", read_only=True)

    class Meta:
        model = Answer
        fields = ["id", "question_id", "value_text", "value_number", "value_boolean", "value_json", "created_at"]

class SessionSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)
    image_id = serializers.UUIDField(source="image.id", read_only=True)

    class Meta:
        model = EstimationSession
        fields = [
            "id", "image_id",
            "object_label", "object_summary", "object_json",
            "status",
            "questions", "answers",
            "created_at", "updated_at",
        ]

class CreateSessionFromImageSerializer(serializers.Serializer):
    image_id = serializers.UUIDField()
    user_hint = serializers.CharField(required=False, allow_blank=True, max_length=200)

class SubmitAnswersSerializer(serializers.Serializer):
    answers = serializers.ListField(child=serializers.DictField(), allow_empty=False)

    def validate_answers(self, items):
        for it in items:
            if "question_id" not in it or "value" not in it:
                raise serializers.ValidationError("Each answer must include question_id and value.")
        return items

