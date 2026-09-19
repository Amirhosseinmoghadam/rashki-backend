from rest_framework import serializers

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
    inline_serializer,
)

from addresses.api.v1.serializers import (
    AddressCreateSerializer,
    AddressSerializer,
    AddressUpdateSerializer,
    CitySerializer,
    ProvinceSerializer,
)

from . import examples, responses


ProvinceListResponse = inline_serializer(
    name="ProvinceListResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": ProvinceSerializer(many=True),
    },
)

CityListResponse = inline_serializer(
    name="CityListResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": CitySerializer(many=True),
    },
)

AddressListResponse = inline_serializer(
    name="AddressListResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": AddressSerializer(many=True),
    },
)

AddressDetailResponse = inline_serializer(
    name="AddressDetailResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": AddressSerializer(),
    },
)

AddressDeleteResponse = inline_serializer(
    name="AddressDeleteResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": serializers.JSONField(
            allow_null=True,
        ),
    },
)

AddressErrorResponse = inline_serializer(
    name="AddressErrorResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "errors": serializers.JSONField(
            allow_null=True,
        ),
    },
)


province_list_view_schema = extend_schema(
    tags=["Addresses - Locations"],
    operation_id="province_list",
    summary="List Provinces",
    responses={
        200: OpenApiResponse(
            response=ProvinceListResponse,
            examples=[
                OpenApiExample(
                    name="Success",
                    value=responses.ProvinceListSuccess,
                    response_only=True,
                ),
            ],
        ),
    },
)

city_list_view_schema = extend_schema(
    tags=["Addresses - Locations"],
    operation_id="city_list_by_province",
    summary="List Cities By Province",
    parameters=[
        OpenApiParameter(
            name="province_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=CityListResponse,
            examples=[
                OpenApiExample(
                    name="Success",
                    value=responses.CityListSuccess,
                    response_only=True,
                ),
            ],
        ),
    },
)

address_list_view_schema = extend_schema(
    tags=["Addresses"],
    operation_id="address_list",
    summary="List User Addresses",
    responses={
        200: OpenApiResponse(
            response=AddressListResponse,
            examples=[
                OpenApiExample(
                    name="Success",
                    value=responses.AddressListSuccess,
                    response_only=True,
                ),
            ],
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
    },
)

address_create_view_schema = extend_schema(
    tags=["Addresses"],
    operation_id="address_create",
    summary="Create User Address",
    request=AddressCreateSerializer,
    examples=[
        OpenApiExample(
            name="Request",
            value=examples.AddressCreateRequestExample,
            request_only=True,
        ),
    ],
    responses={
        201: OpenApiResponse(
            response=AddressDetailResponse,
            examples=[
                OpenApiExample(
                    name="Success",
                    value=responses.AddressCreateSuccess,
                    response_only=True,
                ),
            ],
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
    },
)

address_detail_view_schema = extend_schema(
    tags=["Addresses"],
    operation_id="address_detail",
    summary="Get User Address",
    responses={
        200: OpenApiResponse(
            response=AddressDetailResponse,
            examples=[
                OpenApiExample(
                    name="Success",
                    value=responses.AddressDetailSuccess,
                    response_only=True,
                ),
            ],
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
        404: OpenApiResponse(
            response=AddressErrorResponse,
            examples=[
                OpenApiExample(
                    name="Not Found",
                    value=responses.AddressNotFound,
                    response_only=True,
                ),
            ],
        ),
    },
)

address_update_view_schema = extend_schema(
    tags=["Addresses"],
    operation_id="address_update",
    summary="Update User Address",
    request=AddressUpdateSerializer,
    examples=[
        OpenApiExample(
            name="Request",
            value=examples.AddressUpdateRequestExample,
            request_only=True,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=AddressDetailResponse,
            examples=[
                OpenApiExample(
                    name="Success",
                    value=responses.AddressUpdateSuccess,
                    response_only=True,
                ),
            ],
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
        404: OpenApiResponse(
            response=AddressErrorResponse,
        ),
    },
)

address_partial_update_view_schema = extend_schema(
    tags=["Addresses"],
    operation_id="address_partial_update",
    summary="Partially Update User Address",
    request=AddressUpdateSerializer,
    examples=[
        OpenApiExample(
            name="Request",
            value=examples.AddressPartialUpdateRequestExample,
            request_only=True,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=AddressDetailResponse,
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
        404: OpenApiResponse(
            response=AddressErrorResponse,
        ),
    },
)

address_delete_view_schema = extend_schema(
    tags=["Addresses"],
    operation_id="address_delete",
    summary="Delete User Address",
    responses={
        200: OpenApiResponse(
            response=AddressDeleteResponse,
            examples=[
                OpenApiExample(
                    name="Success",
                    value=responses.AddressDeleteSuccess,
                    response_only=True,
                ),
            ],
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
        404: OpenApiResponse(
            response=AddressErrorResponse,
        ),
    },
)

address_set_default_view_schema = extend_schema(
    tags=["Addresses"],
    operation_id="address_set_default",
    summary="Set Default Address",
    request=None,
    responses={
        200: OpenApiResponse(
            response=AddressDetailResponse,
            examples=[
                OpenApiExample(
                    name="Success",
                    value=responses.AddressSetDefaultSuccess,
                    response_only=True,
                ),
            ],
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
        404: OpenApiResponse(
            response=AddressErrorResponse,
        ),
    },
)
