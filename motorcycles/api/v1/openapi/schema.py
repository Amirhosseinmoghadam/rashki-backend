from rest_framework import serializers

from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from motorcycles.api.v1.serializers import (
    MotorcycleBrandListSerializer,
    MotorcycleBrandDetailSerializer,
    MotorcycleBrandCreateUpdateSerializer,
    MotorcycleModelListSerializer,
    MotorcycleModelDetailSerializer,
    MotorcycleModelCreateUpdateSerializer,
)

from . import examples
from . import responses


# =========================================================
# Brand Response Serializers
# =========================================================


MotorcycleBrandListResponseSerializer = (
    inline_serializer(
        name="MotorcycleBrandListResponse",
        fields={
            "success": (
                serializers.BooleanField()
            ),
            "message": (
                serializers.CharField()
            ),
            "count": (
                serializers.IntegerField()
            ),
            "data": (
                MotorcycleBrandListSerializer(
                    many=True
                )
            ),
        },
    )
)


MotorcycleBrandDetailResponseSerializer = (
    inline_serializer(
        name="MotorcycleBrandDetailResponse",
        fields={
            "success": (
                serializers.BooleanField()
            ),
            "message": (
                serializers.CharField()
            ),
            "data": (
                MotorcycleBrandDetailSerializer()
            ),
        },
    )
)


MotorcycleBrandDeleteResponseSerializer = (
    inline_serializer(
        name="MotorcycleBrandDeleteResponse",
        fields={
            "success": (
                serializers.BooleanField()
            ),
            "message": (
                serializers.CharField()
            ),
            "data": serializers.JSONField(
                allow_null=True,
            ),
        },
    )
)


MotorcycleBrandProtectedResponseSerializer = (
    inline_serializer(
        name=(
            "MotorcycleBrandProtectedResponse"
        ),
        fields={
            "success": (
                serializers.BooleanField()
            ),
            "message": (
                serializers.CharField()
            ),
            "errors": serializers.JSONField(
                allow_null=True,
            ),
        },
    )
)


# =========================================================
# Model Response Serializers
# =========================================================


MotorcycleModelListResponseSerializer = (
    inline_serializer(
        name="MotorcycleModelListResponse",
        fields={
            "success": (
                serializers.BooleanField()
            ),
            "message": (
                serializers.CharField()
            ),
            "count": (
                serializers.IntegerField()
            ),
            "data": (
                MotorcycleModelListSerializer(
                    many=True
                )
            ),
        },
    )
)


MotorcycleModelDetailResponseSerializer = (
    inline_serializer(
        name=(
            "MotorcycleModelDetailResponse"
        ),
        fields={
            "success": (
                serializers.BooleanField()
            ),
            "message": (
                serializers.CharField()
            ),
            "data": (
                MotorcycleModelDetailSerializer()
            ),
        },
    )
)


MotorcycleModelDeleteResponseSerializer = (
    inline_serializer(
        name=(
            "MotorcycleModelDeleteResponse"
        ),
        fields={
            "success": (
                serializers.BooleanField()
            ),
            "message": (
                serializers.CharField()
            ),
            "data": serializers.JSONField(
                allow_null=True,
            ),
        },
    )
)


MotorcycleModelProtectedResponseSerializer = (
    inline_serializer(
        name=(
            "MotorcycleModelProtectedResponse"
        ),
        fields={
            "success": (
                serializers.BooleanField()
            ),
            "message": (
                serializers.CharField()
            ),
            "errors": serializers.JSONField(
                allow_null=True,
            ),
        },
    )
)


# =========================================================
# Motorcycle Brand List
# =========================================================


motorcycle_brand_list_view_schema = extend_schema(
    tags=[
        "Motorcycle Brands",
    ],
    auth=[],
    operation_id="motorcycle_brand_list",
    summary="List Motorcycle Brands",
    description=(
        "Returns all active motorcycle brands. "
        "The endpoint is public."
    ),
    parameters=[
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location=(
                OpenApiParameter.QUERY
            ),
            required=False,
            description=(
                "Search motorcycle brands "
                "by name."
            ),
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=(
                MotorcycleBrandListResponseSerializer
            ),
            examples=[
                OpenApiExample(
                    name="Motorcycle Brands",
                    value=(
                        responses
                        .MotorcycleBrandListSuccess
                    ),
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# Motorcycle Brand Detail
# =========================================================


motorcycle_brand_detail_view_schema = extend_schema(
    tags=[
        "Motorcycle Brands",
    ],
    auth=[],
    operation_id=(
        "motorcycle_brand_detail"
    ),
    summary="Get Motorcycle Brand",
    responses={
        200: OpenApiResponse(
            response=(
                MotorcycleBrandDetailResponseSerializer
            ),
            examples=[
                OpenApiExample(
                    name="Motorcycle Brand",
                    value=(
                        responses
                        .MotorcycleBrandDetailSuccess
                    ),
                    response_only=True,
                ),
            ],
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    name="Not Found",
                    value=(
                        responses
                        .MotorcycleBrandNotFound
                    ),
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# Motorcycle Brand Create
# =========================================================


motorcycle_brand_create_view_schema = extend_schema(
    tags=[
        "Motorcycle Brands",
    ],
    operation_id=(
        "motorcycle_brand_create"
    ),
    summary="Create Motorcycle Brand",
    request=(
        MotorcycleBrandCreateUpdateSerializer
    ),
    examples=[
        OpenApiExample(
            name="Create Motorcycle Brand",
            value=(
                examples
                .MOTORCYCLE_BRAND_CREATE_EXAMPLE
            ),
            request_only=True,
        ),
    ],
    responses={
        201: OpenApiResponse(
            response=(
                MotorcycleBrandDetailResponseSerializer
            ),
            examples=[
                OpenApiExample(
                    name="Brand Created",
                    value=(
                        responses
                        .MotorcycleBrandCreateSuccess
                    ),
                    response_only=True,
                ),
            ],
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    name="Duplicate Brand",
                    value=(
                        responses
                        .MotorcycleBrandDuplicateName
                    ),
                    response_only=True,
                ),
            ],
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    name="Authentication Required",
                    value=(
                        responses
                        .MotorcycleAuthenticationRequired
                    ),
                    response_only=True,
                ),
            ],
        ),
        403: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    name="Permission Denied",
                    value=(
                        responses
                        .MotorcyclePermissionDenied
                    ),
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# Motorcycle Brand Update
# =========================================================


motorcycle_brand_update_view_schema = extend_schema(
    tags=[
        "Motorcycle Brands",
    ],
    operation_id=(
        "motorcycle_brand_update"
    ),
    summary="Update Motorcycle Brand",
    request=(
        MotorcycleBrandCreateUpdateSerializer
    ),
    examples=[
        OpenApiExample(
            name="Update Motorcycle Brand",
            value=(
                examples
                .MOTORCYCLE_BRAND_UPDATE_EXAMPLE
            ),
            request_only=True,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=(
                MotorcycleBrandDetailResponseSerializer
            ),
            examples=[
                OpenApiExample(
                    name="Brand Updated",
                    value=(
                        responses
                        .MotorcycleBrandUpdateSuccess
                    ),
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
        403: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
    },
)


# =========================================================
# Motorcycle Brand Partial Update
# =========================================================


motorcycle_brand_partial_update_view_schema = (
    extend_schema(
        tags=[
            "Motorcycle Brands",
        ],
        operation_id=(
            "motorcycle_brand_partial_update"
        ),
        summary=(
            "Partially Update Motorcycle Brand"
        ),
        request=(
            MotorcycleBrandCreateUpdateSerializer
        ),
        examples=[
            OpenApiExample(
                name="Deactivate Brand",
                value=(
                    examples
                    .MOTORCYCLE_BRAND_PARTIAL_UPDATE_EXAMPLE
                ),
                request_only=True,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=(
                    MotorcycleBrandDetailResponseSerializer
                ),
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
            ),
            401: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
            ),
            403: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
            ),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
            ),
        },
    )
)


# =========================================================
# Motorcycle Brand Delete
# =========================================================


motorcycle_brand_delete_view_schema = extend_schema(
    tags=[
        "Motorcycle Brands",
    ],
    operation_id=(
        "motorcycle_brand_delete"
    ),
    summary="Delete Motorcycle Brand",
    request=None,
    responses={
        200: OpenApiResponse(
            response=(
                MotorcycleBrandDeleteResponseSerializer
            ),
            examples=[
                OpenApiExample(
                    name="Brand Deleted",
                    value=(
                        responses
                        .MotorcycleBrandDeleteSuccess
                    ),
                    response_only=True,
                ),
            ],
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
        403: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
        409: OpenApiResponse(
            response=(
                MotorcycleBrandProtectedResponseSerializer
            ),
            examples=[
                OpenApiExample(
                    name="Protected Brand",
                    value=(
                        responses
                        .MotorcycleBrandDeleteProtected
                    ),
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# Motorcycle Model List
# =========================================================


motorcycle_model_list_view_schema = extend_schema(
    tags=[
        "Motorcycles",
    ],
    auth=[],
    operation_id="motorcycle_list",
    summary="List Motorcycles",
    description=(
        "Returns active motorcycles whose "
        "motorcycle brand is also active."
    ),
    parameters=[
        OpenApiParameter(
            name="brand",
            type=OpenApiTypes.INT,
            location=(
                OpenApiParameter.QUERY
            ),
            required=False,
            description=(
                "Filter by motorcycle brand ID."
            ),
        ),
        OpenApiParameter(
            name="engine_volume",
            type=OpenApiTypes.INT,
            location=(
                OpenApiParameter.QUERY
            ),
            required=False,
            description=(
                "Filter by engine volume in CC."
            ),
        ),
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location=(
                OpenApiParameter.QUERY
            ),
            required=False,
            description=(
                "Search by motorcycle model, "
                "brand or description."
            ),
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=(
                MotorcycleModelListResponseSerializer
            ),
            examples=[
                OpenApiExample(
                    name="Motorcycles",
                    value=(
                        responses
                        .MotorcycleModelListSuccess
                    ),
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# Motorcycle Model Detail
# =========================================================


motorcycle_model_detail_view_schema = extend_schema(
    tags=[
        "Motorcycles",
    ],
    auth=[],
    operation_id="motorcycle_detail",
    summary="Get Motorcycle",
    responses={
        200: OpenApiResponse(
            response=(
                MotorcycleModelDetailResponseSerializer
            ),
            examples=[
                OpenApiExample(
                    name="Motorcycle",
                    value=(
                        responses
                        .MotorcycleModelDetailSuccess
                    ),
                    response_only=True,
                ),
            ],
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    name="Not Found",
                    value=(
                        responses
                        .MotorcycleModelNotFound
                    ),
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# Motorcycle Model Create
# =========================================================


motorcycle_model_create_view_schema = extend_schema(
    tags=[
        "Motorcycles",
    ],
    operation_id="motorcycle_create",
    summary="Create Motorcycle",
    request=(
        MotorcycleModelCreateUpdateSerializer
    ),
    examples=[
        OpenApiExample(
            name="Create Motorcycle",
            value=(
                examples
                .MOTORCYCLE_MODEL_CREATE_EXAMPLE
            ),
            request_only=True,
        ),
    ],
    responses={
        201: OpenApiResponse(
            response=(
                MotorcycleModelDetailResponseSerializer
            ),
            examples=[
                OpenApiExample(
                    name="Motorcycle Created",
                    value=(
                        responses
                        .MotorcycleModelCreateSuccess
                    ),
                    response_only=True,
                ),
            ],
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    name="Duplicate Model",
                    value=(
                        responses
                        .MotorcycleModelDuplicateName
                    ),
                    response_only=True,
                ),
                OpenApiExample(
                    name="Invalid Year",
                    value=(
                        responses
                        .MotorcycleModelInvalidYear
                    ),
                    response_only=True,
                ),
            ],
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
        403: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
    },
)


# =========================================================
# Motorcycle Model Update
# =========================================================


motorcycle_model_update_view_schema = extend_schema(
    tags=[
        "Motorcycles",
    ],
    operation_id="motorcycle_update",
    summary="Update Motorcycle",
    request=(
        MotorcycleModelCreateUpdateSerializer
    ),
    examples=[
        OpenApiExample(
            name="Update Motorcycle",
            value=(
                examples
                .MOTORCYCLE_MODEL_UPDATE_EXAMPLE
            ),
            request_only=True,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=(
                MotorcycleModelDetailResponseSerializer
            ),
            examples=[
                OpenApiExample(
                    name="Motorcycle Updated",
                    value=(
                        responses
                        .MotorcycleModelUpdateSuccess
                    ),
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
        403: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
    },
)


# =========================================================
# Motorcycle Model Partial Update
# =========================================================


motorcycle_model_partial_update_view_schema = (
    extend_schema(
        tags=[
            "Motorcycles",
        ],
        operation_id=(
            "motorcycle_partial_update"
        ),
        summary=(
            "Partially Update Motorcycle"
        ),
        request=(
            MotorcycleModelCreateUpdateSerializer
        ),
        examples=[
            OpenApiExample(
                name="Partial Update",
                value=(
                    examples
                    .MOTORCYCLE_MODEL_PARTIAL_UPDATE_EXAMPLE
                ),
                request_only=True,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=(
                    MotorcycleModelDetailResponseSerializer
                ),
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
            ),
            401: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
            ),
            403: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
            ),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
            ),
        },
    )
)


# =========================================================
# Motorcycle Model Delete
# =========================================================


motorcycle_model_delete_view_schema = extend_schema(
    tags=[
        "Motorcycles",
    ],
    operation_id="motorcycle_delete",
    summary="Delete Motorcycle",
    request=None,
    responses={
        200: OpenApiResponse(
            response=(
                MotorcycleModelDeleteResponseSerializer
            ),
            examples=[
                OpenApiExample(
                    name="Motorcycle Deleted",
                    value=(
                        responses
                        .MotorcycleModelDeleteSuccess
                    ),
                    response_only=True,
                ),
            ],
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
        403: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
        409: OpenApiResponse(
            response=(
                MotorcycleModelProtectedResponseSerializer
            ),
            examples=[
                OpenApiExample(
                    name="Protected Motorcycle",
                    value=(
                        responses
                        .MotorcycleModelDeleteProtected
                    ),
                    response_only=True,
                ),
            ],
        ),
    },
)