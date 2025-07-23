from drf_spectacular.utils import inline_serializer
from rest_framework import serializers


class BaseErrorSerializer(serializers.Serializer):
    success = serializers.BooleanField(help_text="是否成功")
    message = serializers.CharField(help_text="狀態訊息")
    data = serializers.DictField(help_text="資料")
    errors = serializers.DictField(help_text="錯誤訊息")


class DeleteSuccessSerializer(serializers.Serializer):
    success = serializers.BooleanField(help_text="是否成功")
    message = serializers.CharField(help_text="狀態訊息")
    data = serializers.DictField(required=False)


def SuccessSerializer(data_serializer: serializers.Serializer, name: str):
    return inline_serializer(
        name=name,
        fields={
            "success": serializers.BooleanField(help_text="是否成功", default=True),
            "message": serializers.CharField(help_text="狀態訊息"),
            "data": data_serializer,
        },
    )

