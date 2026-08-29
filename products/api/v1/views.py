# from django.shortcuts import get_object_or_404
#
# from rest_framework import status
# from rest_framework.permissions import (
#     AllowAny,
#     IsAuthenticatedOrReadOnly,
# )
# from rest_framework.response import Response
# from rest_framework.views import APIView
#
# from products.models import (
#     Product,
#     ProductImage,
#     AttributeGroup,
#     Attribute,
#     AttributeValue,
#     ProductAttributeValue,
#     ProductVariant,
#     VariantAttributeValue,
#     ProductMotorcycleCompatibility,
# )
# from products.api.v1.openapi.schema import product_list_create_schema, product_retrieve_update_destroy_schema, \
#     product_image_list_create_schema, product_image_retrieve_update_destroy_schema, attribute_group_list_create_schema, \
#     attribute_group_retrieve_update_destroy_schema, attribute_list_create_schema, \
#     attribute_retrieve_update_destroy_schema, attribute_value_list_create_schema, \
#     attribute_value_retrieve_update_destroy_schema, product_variant_list_create_schema, \
#     product_variant_retrieve_update_destroy_schema, product_motorcycle_compatibility_list_create_schema, \
#     product_motorcycle_compatibility_retrieve_update_destroy_schema
#
# from .serializers import (
#     # Product
#     ProductListSerializer,
#     ProductDetailSerializer,
#     ProductCreateUpdateSerializer,
#     # Product Image
#     ProductImageSerializer,
#     ProductImageCreateSerializer,
#     # Attribute Group
#     AttributeGroupSerializer,
#     AttributeGroupCreateUpdateSerializer,
#     # Attribute
#     AttributeSerializer,
#     AttributeCreateUpdateSerializer,
#     # Attribute Value
#     AttributeValueSerializer,
#     AttributeValueCreateUpdateSerializer,
#     # Product Attribute Value
#     ProductAttributeValueSerializer,
#     ProductAttributeValueCreateUpdateSerializer,
#     # Product Variant
#     ProductVariantSerializer,
#     ProductVariantCreateUpdateSerializer,
#     ProductVariantDetailSerializer,
#     # Variant Attribute Value
#     VariantAttributeValueSerializer,
#     VariantAttributeValueCreateUpdateSerializer,
#     # Product Motorcycle Compatibility
#     ProductMotorcycleCompatibilitySerializer,
#     ProductMotorcycleCompatibilityCreateUpdateSerializer,
# )
#
#
# # =========================================================
# # Product Views
# # =========================================================
#
# @product_list_create_schema
# class ProductListCreateAPIView(APIView):
#     """
#     List all products or create a new product.
#
#     GET: Returns a list of all active products.
#     POST: Creates a new product (requires authentication).
#     """
#
#     permission_classes = [IsAuthenticatedOrReadOnly]
#
#     def get(self, request):
#         products = Product.objects.filter(is_active=True).select_related(
#             "brand",
#             "category",
#         ).prefetch_related(
#             "images",
#         )
#
#         serializer = ProductListSerializer(
#             products,
#             many=True,
#         )
#
#         return Response(
#             {
#                 "count": products.count(),
#                 "results": serializer.data,
#             },
#             status=status.HTTP_200_OK,
#         )
#
#     def post(self, request):
#         serializer = ProductCreateUpdateSerializer(
#             data=request.data,
#         )
#
#         if serializer.is_valid():
#             serializer.save()
#
#             return Response(
#                 {
#                     "message": "محصول با موفقیت ایجاد شد.",
#                     "data": serializer.data,
#                 },
#                 status=status.HTTP_201_CREATED,
#             )
#
#         return Response(
#             {
#                 "message": "خطا در ایجاد محصول.",
#                 "errors": serializer.errors,
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )
#
#
# @product_retrieve_update_destroy_schema
# class ProductRetrieveUpdateDestroyAPIView(APIView):
#     """
#     Retrieve, update, or delete a single product.
#
#     GET: Returns a single product by slug.
#     PUT/PATCH: Updates a product (requires authentication).
#     DELETE: Deletes a product (requires authentication).
#     """
#
#     permission_classes = [IsAuthenticatedOrReadOnly]
#
#     def get_object(self, slug):
#         return get_object_or_404(
#             Product.objects.select_related(
#                 "brand",
#                 "category",
#             ).prefetch_related(
#                 "images",
#                 "attribute_values__attribute",
#                 "variants__attribute_values__attribute",
#                 "variants__attribute_values__value",
#                 "motorcycle_compatibilities__motorcycle",
#             ),
#             slug=slug,
#         )
#
#     def get(self, request, slug):
#         product = self.get_object(slug)
#
#         serializer = ProductDetailSerializer(product)
#
#         return Response(
#             serializer.data,
#             status=status.HTTP_200_OK,
#         )
#
#     def put(self, request, slug):
#         product = self.get_object(slug)
#
#         serializer = ProductCreateUpdateSerializer(
#             product,
#             data=request.data,
#         )
#
#         if serializer.is_valid():
#             serializer.save()
#
#             return Response(
#                 {
#                     "message": "محصول با موفقیت بروزرسانی شد.",
#                     "data": serializer.data,
#                 },
#                 status=status.HTTP_200_OK,
#             )
#
#         return Response(
#             {
#                 "message": "خطا در بروزرسانی محصول.",
#                 "errors": serializer.errors,
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )
#
#     def patch(self, request, slug):
#         product = self.get_object(slug)
#
#         serializer = ProductCreateUpdateSerializer(
#             product,
#             data=request.data,
#             partial=True,
#         )
#
#         if serializer.is_valid():
#             serializer.save()
#
#             return Response(
#                 {
#                     "message": "محصول با موفقیت بروزرسانی شد.",
#                     "data": serializer.data,
#                 },
#                 status=status.HTTP_200_OK,
#             )
#
#         return Response(
#             {
#                 "message": "خطا در بروزرسانی محصول.",
#                 "errors": serializer.errors,
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )
#
#     def delete(self, request, slug):
#         product = self.get_object(slug)
#
#         product.delete()
#
#         return Response(
#             {"message": "محصول با موفقیت حذف شد."},
#             status=status.HTTP_200_OK,
#         )
#
#
# # =========================================================
# # Product Image Views
# # =========================================================
#
# @product_image_list_create_schema
# class ProductImageListCreateAPIView(APIView):
#     """
#     List all images for a product or create a new image.
#     """
#
#     permission_classes = [IsAuthenticatedOrReadOnly]
#
#     def get_object(self, product_id):
#         return get_object_or_404(Product, pk=product_id)
#
#     def get(self, request, product_id):
#         product = self.get_object(product_id)
#
#         images = product.images.all()
#
#         serializer = ProductImageSerializer(
#             images,
#             many=True,
#         )
#
#         return Response(
#             serializer.data,
#             status=status.HTTP_200_OK,
#         )
#
#     def post(self, request, product_id):
#         product = self.get_object(product_id)
#
#         serializer = ProductImageCreateSerializer(
#             data=request.data,
#         )
#
#         if serializer.is_valid():
#             serializer.save(product=product)
#
#             return Response(
#                 {
#                     "message": "تصویر محصول با موفقیت ایجاد شد.",
#                     "data": serializer.data,
#                 },
#                 status=status.HTTP_201_CREATED,
#             )
#
#         return Response(
#             {
#                 "message": "خطا در ایجاد تصویر محصول.",
#                 "errors": serializer.errors,
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )
#
# @product_image_retrieve_update_destroy_schema
# class ProductImageRetrieveUpdateDestroyAPIView(APIView):
#     """
#     Retrieve, update, or delete a single product image.
#     """
#
#     permission_classes = [IsAuthenticatedOrReadOnly]
#
#     def get_object(self, pk):
#         return get_object_or_404(ProductImage, pk=pk)
#
#     def get(self, request, pk):
#         image = self.get_object(pk)
#
#         serializer = ProductImageSerializer(image)
#
#         return Response(
#             serializer.data,
#             status=status.HTTP_200_OK,
#         )
#
#     def put(self, request, pk):
#         image = self.get_object(pk)
#
#         serializer = ProductImageCreateSerializer(
#             image,
#             data=request.data,
#         )
#
#         if serializer.is_valid():
#             serializer.save()
#
#             return Response(
#                 {
#                     "message": "تصویر محصول با موفقیت بروزرسانی شد.",
#                     "data": serializer.data,
#                 },
#                 status=status.HTTP_200_OK,
#             )
#
#         return Response(
#             {
#                 "message": "خطا در بروزرسانی تصویر محصول.",
#                 "errors": serializer.errors,
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )
#
#     def patch(self, request, pk):
#         image = self.get_object(pk)
#
#         serializer = ProductImageCreateSerializer(
#             image,
#             data=request.data,
#             partial=True,
#         )
#
#         if serializer.is_valid():
#             serializer.save()
#
#             return Response(
#                 {
#                     "message": "تصویر محصول با موفقیت بروزرسانی شد.",
#                     "data": serializer.data,
#                 },
#                 status=status.HTTP_200_OK,
#             )
#
#         return Response(
#             {
#                 "message": "خطا در بروزرسانی تصویر محصول.",
#                 "errors": serializer.errors,
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )
#
#     def delete(self, request, pk):
#         image = self.get_object(pk)
#
#         image.delete()
#
#         return Response(
#             {"message": "تصویر محصول با موفقیت حذف شد."},
#             status=status.HTTP_200_OK,
#         )
#
#
# # =========================================================
# # Attribute Group Views
# # =========================================================
#
# @attribute_group_list_create_schema
# class AttributeGroupListCreateAPIView(APIView):
#     """
#     List all attribute groups or create a new one.
#     """
#
#     permission_classes = [IsAuthenticatedOrReadOnly]
#
#     def get(self, request):
#         groups = AttributeGroup.objects.filter(is_active=True)
#
#         serializer = AttributeGroupSerializer(
#             groups,
#             many=True,
#         )
#
#         return Response(
#             serializer.data,
#             status=status.HTTP_200_OK,
#         )
#
#     def post(self, request):
#         serializer = AttributeGroupCreateUpdateSerializer(
#             data=request.data,
#         )
#
#         if serializer.is_valid():
#             serializer.save()
#
#             return Response(
#                 {
#                     "message": "گروه ویژگی با موفقیت ایجاد شد.",
#                     "data": serializer.data,
#                 },
#                 status=status.HTTP_201_CREATED,
#             )
#
#         return Response(
#             {
#                 "message": "خطا در ایجاد گروه ویژگی.",
#                 "errors": serializer.errors,
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )
#
# @attribute_group_retrieve_update_destroy_schema
# class AttributeGroupRetrieveUpdateDestroyAPIView(APIView):
#     """
#     Retrieve, update, or delete a single attribute group.
#     """
#
#     permission_classes = [IsAuthenticatedOrReadOnly]
#
#     def get_object(self, pk):
#         return get_object_or_404(AttributeGroup, pk=pk)
#
#     def get(self, request, pk):
#         group = self.get_object(pk)
#
#         serializer = AttributeGroupSerializer(group)
#
#         return Response(
#             serializer.data,
#             status=status.HTTP_200_OK,
#         )
#
#     def put(self, request, pk):
#         group = self.get_object(pk)
#
#         serializer = AttributeGroupCreateUpdateSerializer(
#             group,
#             data=request.data,
#         )
#
#         if serializer.is_valid():
#             serializer.save()
#
#             return Response(
#                 {
#                     "message": "گروه ویژگی با موفقیت بروزرسانی شد.",
#                     "data": serializer.data,
#                 },
#                 status=status.HTTP_200_OK,
#             )
#
#         return Response(
#             {
#                 "message": "خطا در بروزرسانی گروه ویژگی.",
#                 "errors": serializer.errors,
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )
#
#     def patch(self, request, pk):
#         group = self.get_object(pk)
#
#         serializer = AttributeGroupCreateUpdateSerializer(
#             group,
#             data=request.data,
#             partial=True,
#         )
#
#         if serializer.is_valid():
#             serializer.save()
#
#             return Response(
#                 {
#                     "message": "گروه ویژگی با موفقیت بروزرسانی شد.",
#                     "data": serializer.data,
#                 },
#                 status=status.HTTP_200_OK,
#             )
#
#         return Response(
#             {
#                 "message": "خطا در بروزرسانی گروه ویژگی.",
#                 "errors": serializer.errors,
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )
#
#     def delete(self, request, pk):
#         group = self.get_object(pk)
#
#         group.delete()
#
#         return Response(
#             {"message": "گروه ویژگی با موفقیت حذف شد."},
#             status=status.HTTP_200_OK,
#         )
#
#
# # =========================================================
# # Attribute Views
# # =========================================================
#
# @attribute_list_create_schema
# class AttributeListCreateAPIView(APIView):
#     """
#     List all attributes or create a new one.
#     """
#
#     permission_classes = [IsAuthenticatedOrReadOnly]
#
#     def get(self, request):
#         attributes = Attribute.objects.filter(is_active=True).select_related("group")
#
#         serializer = AttributeSerializer(
#             attributes,
#             many=True,
#         )
#
#         return Response(
#             serializer.data,
#             status=status.HTTP_200_OK,
#         )
#
#     def post(self, request):
#         serializer = AttributeCreateUpdateSerializer(
#             data=request.data,
#         )
#
#         if serializer.is_valid():
#             serializer.save()
#
#             return Response(
#                 {
#                     "message": "ویژگی با موفقیت ایجاد شد.",
#                     "data": serializer.data,
#                 },
#                 status=status.HTTP_201_CREATED,
#             )
#
#         return Response(
#             {
#                 "message": "خطا در ایجاد ویژگی.",
#                 "errors": serializer.errors,
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )
#
# @attribute_retrieve_update_destroy_schema
# class AttributeRetrieveUpdateDestroyAPIView(APIView):
#     """
#     Retrieve, update, or delete a single attribute.
#     """
#
#     permission_classes = [IsAuthenticatedOrReadOnly]
#
#     def get_object(self, pk):
#         return get_object_or_404(Attribute, pk=pk)
#
#     def get(self, request, pk):
#         attribute = self.get_object(pk)
#
#         serializer = AttributeSerializer(attribute)
#
#         return Response(
#             serializer.data,
#             status=status.HTTP_200_OK,
#         )
#
#     def put(self, request, pk):
#         attribute = self.get_object(pk)
#
#         serializer = AttributeCreateUpdateSerializer(
#             attribute,
#             data=request.data,
#         )
#
#         if serializer.is_valid():
#             serializer.save()
#
#             return Response(
#                 {
#                     "message": "ویژگی با موفقیت بروزرسانی شد.",
#                     "data": serializer.data,
#                 },
#                 status=status.HTTP_200_OK,
#             )
#
#         return Response(
#             {
#                 "message": "خطا در بروزرسانی ویژگی.",
#                 "errors": serializer.errors,
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )
#
#     def patch(self, request, pk):
#         attribute = self.get_object(pk)
#
#         serializer = AttributeCreateUpdateSerializer(
#             attribute,
#             data=request.data,
#             partial=True,
#         )
#
#         if serializer.is_valid():
#             serializer.save()
#
#             return Response(
#                 {
#                     "message": "ویژگی با موفقیت بروزرسانی شد.",
#                     "data": serializer.data,
#                 },
#                 status=status.HTTP_200_OK,
#             )
#
#         return Response(
#             {
#                 "message": "خطا در بروزرسانی ویژگی.",
#                 "errors": serializer.errors,
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )
#
#     def delete(self, request, pk):
#         attribute = self.get_object(pk)
#
#         attribute.delete()
#
#         return Response(
#             {"message": "ویژگی با موفقیت حذف شد."},
#             status=status.HTTP_200_OK,
#         )
#
#
# # =========================================================
# # Attribute Value Views
# # =========================================================
#
# @attribute_value_list_create_schema
# class AttributeValueListCreateAPIView(APIView):
#     """
#     List all attribute values or create a new one.
#     """
#
#     permission_classes = [IsAuthenticatedOrReadOnly]
#
#     def get(self, request):
#         values = AttributeValue.objects.filter(is_active=True).select_related("attribute")
#
#         serializer = AttributeValueSerializer(
#             values,
#             many=True,
#         )
#
#         return Response(
#             serializer.data,
#             status=status.HTTP_200_OK,
#         )
#
#     def post(self, request):
#         serializer = AttributeValueCreateUpdateSerializer(
#             data=request.data,
#         )
#
#         if serializer.is_valid():
#             serializer.save()
#
#             return Response(
#                 {
#                     "message": "مقدار ویژگی با موفقیت ایجاد شد.",
#                     "data": serializer.data,
#                 },
#                 status=status.HTTP_201_CREATED,
#             )
#
#         return Response(
#             {
#                 "message": "خطا در ایجاد مقدار ویژگی.",
#                 "errors": serializer.errors,
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )
#
# @attribute_value_retrieve_update_destroy_schema
# class AttributeValueRetrieveUpdateDestroyAPIView(APIView):
#     """
#     Retrieve, update, or delete a single attribute value.
#     """
#
#     permission_classes = [IsAuthenticatedOrReadOnly]
#
#     def get_object(self, pk):
#         return get_object_or_404(AttributeValue, pk=pk)
#
#     def get(self, request, pk):
#         value = self.get_object(pk)
#
#         serializer = AttributeValueSerializer(value)
#
#         return Response(
#             serializer.data,
#             status=status.HTTP_200_OK,
#         )
#
#     def put(self, request, pk):
#         value = self.get_object(pk)
#
#         serializer = AttributeValueCreateUpdateSerializer(
#             value,
#             data=request.data,
#         )
#
#         if serializer.is_valid():
#             serializer.save()
#
#             return Response(
#                 {
#                     "message": "مقدار ویژگی با موفقیت بروزرسانی شد.",
#                     "data": serializer.data,
#                 },
#                 status=status.HTTP_200_OK,
#             )
#
#         return Response(
#             {
#                 "message": "خطا در بروزرسانی مقدار ویژگی.",
#                 "errors": serializer.errors,
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )
#
#     def patch(self, request, pk):
#         value = self.get_object(pk)
#
#         serializer = AttributeValueCreateUpdateSerializer(
#             value,
#             data=request.data,
#             partial=True,
#         )
#
#         if serializer.is_valid():
#             serializer.save()
#
#             return Response(
#                 {
#                     "message": "مقدار ویژگی با موفقیت بروزرسانی شد.",
#                     "data": serializer.data,
#                 },
#                 status=status.HTTP_200_OK,
#             )
#
#         return Response(
#             {
#                 "message": "خطا در بروزرسانی مقدار ویژگی.",
#                 "errors": serializer.errors,
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )
#
#     def delete(self, request, pk):
#         value = self.get_object(pk)
#
#         value.delete()
#
#         return Response(
#             {"message": "مقدار ویژگی با موفقیت حذف شد."},
#             status=status.HTTP_200_OK,
#         )
#
#
# # =========================================================
# # Product Variant Views
# # =========================================================
#
# @product_variant_list_create_schema
# class ProductVariantListCreateAPIView(APIView):
#     """
#     List all variants for a product or create a new variant.
#     """
#
#     permission_classes = [IsAuthenticatedOrReadOnly]
#
#     def get_object(self, product_id):
#         return get_object_or_404(Product, pk=product_id)
#
#     def get(self, request, product_id):
#         product = self.get_object(product_id)
#
#         variants = product.variants.all()
#
#         serializer = ProductVariantSerializer(
#             variants,
#             many=True,
#         )
#
#         return Response(
#             serializer.data,
#             status=status.HTTP_200_OK,
#         )
#
#     def post(self, request, product_id):
#         product = self.get_object(product_id)
#
#         serializer = ProductVariantCreateUpdateSerializer(
#             data=request.data,
#         )
#
#         if serializer.is_valid():
#             serializer.save(product=product)
#
#             return Response(
#                 {
#                     "message": "تنوع محصول با موفقیت ایجاد شد.",
#                     "data": serializer.data,
#                 },
#                 status=status.HTTP_201_CREATED,
#             )
#
#         return Response(
#             {
#                 "message": "خطا در ایجاد تنوع محصول.",
#                 "errors": serializer.errors,
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )
#
# @product_variant_retrieve_update_destroy_schema
# class ProductVariantRetrieveUpdateDestroyAPIView(APIView):
#     """
#     Retrieve, update, or delete a single product variant.
#     """
#
#     permission_classes = [IsAuthenticatedOrReadOnly]
#
#     def get_object(self, pk):
#         return get_object_or_404(ProductVariant, pk=pk)
#
#     def get(self, request, pk):
#         variant = self.get_object(pk)
#
#         serializer = ProductVariantDetailSerializer(variant)
#
#         return Response(
#             serializer.data,
#             status=status.HTTP_200_OK,
#         )
#
#     def put(self, request, pk):
#         variant = self.get_object(pk)
#
#         serializer = ProductVariantCreateUpdateSerializer(
#             variant,
#             data=request.data,
#         )
#
#         if serializer.is_valid():
#             serializer.save()
#
#             return Response(
#                 {
#                     "message": "تنوع محصول با موفقیت بروزرسانی شد.",
#                     "data": serializer.data,
#                 },
#                 status=status.HTTP_200_OK,
#             )
#
#         return Response(
#             {
#                 "message": "خطا در بروزرسانی تنوع محصول.",
#                 "errors": serializer.errors,
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )
#
#     def patch(self, request, pk):
#         variant = self.get_object(pk)
#
#         serializer = ProductVariantCreateUpdateSerializer(
#             variant,
#             data=request.data,
#             partial=True,
#         )
#
#         if serializer.is_valid():
#             serializer.save()
#
#             return Response(
#                 {
#                     "message": "تنوع محصول با موفقیت بروزرسانی شد.",
#                     "data": serializer.data,
#                 },
#                 status=status.HTTP_200_OK,
#             )
#
#         return Response(
#             {
#                 "message": "خطا در بروزرسانی تنوع محصول.",
#                 "errors": serializer.errors,
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )
#
#     def delete(self, request, pk):
#         variant = self.get_object(pk)
#
#         variant.delete()
#
#         return Response(
#             {"message": "تنوع محصول با موفقیت حذف شد."},
#             status=status.HTTP_200_OK,
#         )
#
#
# # =========================================================
# # Product Motorcycle Compatibility Views
# # =========================================================
#
# @product_motorcycle_compatibility_list_create_schema
# class ProductMotorcycleCompatibilityListCreateAPIView(APIView):
#     """
#     List all motorcycle compatibilities for a product or create a new one.
#     """
#
#     permission_classes = [IsAuthenticatedOrReadOnly]
#
#     def get_object(self, product_id):
#         return get_object_or_404(Product, pk=product_id)
#
#     def get(self, request, product_id):
#         product = self.get_object(product_id)
#
#         compatibilities = product.motorcycle_compatibilities.all()
#
#         serializer = ProductMotorcycleCompatibilitySerializer(
#             compatibilities,
#             many=True,
#         )
#
#         return Response(
#             serializer.data,
#             status=status.HTTP_200_OK,
#         )
#
#     def post(self, request, product_id):
#         product = self.get_object(product_id)
#
#         serializer = ProductMotorcycleCompatibilityCreateUpdateSerializer(
#             data=request.data,
#         )
#
#         if serializer.is_valid():
#             serializer.save(product=product)
#
#             return Response(
#                 {
#                     "message": "سازگاری موتورسیکلت با موفقیت ایجاد شد.",
#                     "data": serializer.data,
#                 },
#                 status=status.HTTP_201_CREATED,
#             )
#
#         return Response(
#             {
#                 "message": "خطا در ایجاد سازگاری موتورسیکلت.",
#                 "errors": serializer.errors,
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )
#
# @product_motorcycle_compatibility_retrieve_update_destroy_schema
# class ProductMotorcycleCompatibilityRetrieveUpdateDestroyAPIView(APIView):
#     """
#     Retrieve, update, or delete a single motorcycle compatibility.
#     """
#
#     permission_classes = [IsAuthenticatedOrReadOnly]
#
#     def get_object(self, pk):
#         return get_object_or_404(ProductMotorcycleCompatibility, pk=pk)
#
#     def get(self, request, pk):
#         compatibility = self.get_object(pk)
#
#         serializer = ProductMotorcycleCompatibilitySerializer(compatibility)
#
#         return Response(
#             serializer.data,
#             status=status.HTTP_200_OK,
#         )
#
#     def put(self, request, pk):
#         compatibility = self.get_object(pk)
#
#         serializer = ProductMotorcycleCompatibilityCreateUpdateSerializer(
#             compatibility,
#             data=request.data,
#         )
#
#         if serializer.is_valid():
#             serializer.save()
#
#             return Response(
#                 {
#                     "message": "سازگاری موتورسیکلت با موفقیت بروزرسانی شد.",
#                     "data": serializer.data,
#                 },
#                 status=status.HTTP_200_OK,
#             )
#
#         return Response(
#             {
#                 "message": "خطا در بروزرسانی سازگاری موتورسیکلت.",
#                 "errors": serializer.errors,
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )
#
#     def patch(self, request, pk):
#         compatibility = self.get_object(pk)
#
#         serializer = ProductMotorcycleCompatibilityCreateUpdateSerializer(
#             compatibility,
#             data=request.data,
#             partial=True,
#         )
#
#         if serializer.is_valid():
#             serializer.save()
#
#             return Response(
#                 {
#                     "message": "سازگاری موتورسیکلت با موفقیت بروزرسانی شد.",
#                     "data": serializer.data,
#                 },
#                 status=status.HTTP_200_OK,
#             )
#
#         return Response(
#             {
#                 "message": "خطا در بروزرسانی سازگاری موتورسیکلت.",
#                 "errors": serializer.errors,
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )
#
#     def delete(self, request, pk):
#         compatibility = self.get_object(pk)
#
#         compatibility.delete()
#
#         return Response(
#             {"message": "سازگاری موتورسیکلت با موفقیت حذف شد."},
#             status=status.HTTP_200_OK,
#         )


from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import (
    Product,
    ProductImage,
    AttributeGroup,
    Attribute,
    AttributeValue,
    ProductVariant,
    ProductMotorcycleCompatibility,
)

from .serializers import (
    # Product
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateUpdateSerializer,
    # Product Image
    ProductImageSerializer,
    ProductImageCreateSerializer,
    # Attribute Group
    AttributeGroupSerializer,
    AttributeGroupCreateUpdateSerializer,
    # Attribute
    AttributeSerializer,
    AttributeCreateUpdateSerializer,
    # Attribute Value
    AttributeValueSerializer,
    AttributeValueCreateUpdateSerializer,
    # Product Variant
    ProductVariantSerializer,
    ProductVariantCreateUpdateSerializer,
    ProductVariantDetailSerializer,
    # Product Motorcycle Compatibility
    ProductMotorcycleCompatibilitySerializer,
    ProductMotorcycleCompatibilityCreateUpdateSerializer,
)

from .openapi.schema import (
    # Product
    product_list_schema,
    product_create_schema,
    product_retrieve_schema,
    product_update_schema,
    product_partial_update_schema,
    product_delete_schema,
    # Product Image
    product_image_list_schema,
    product_image_create_schema,
    product_image_retrieve_schema,
    product_image_update_schema,
    product_image_partial_update_schema,
    product_image_delete_schema,
    # Attribute Group
    attribute_group_list_schema,
    attribute_group_create_schema,
    attribute_group_retrieve_schema,
    attribute_group_update_schema,
    attribute_group_partial_update_schema,
    attribute_group_delete_schema,
    # Attribute
    attribute_list_schema,
    attribute_create_schema,
    attribute_retrieve_schema,
    attribute_update_schema,
    attribute_partial_update_schema,
    attribute_delete_schema,
    # Attribute Value
    attribute_value_list_schema,
    attribute_value_create_schema,
    attribute_value_retrieve_schema,
    attribute_value_update_schema,
    attribute_value_partial_update_schema,
    attribute_value_delete_schema,
    # Product Variant
    product_variant_list_schema,
    product_variant_create_schema,
    product_variant_retrieve_schema,
    product_variant_update_schema,
    product_variant_partial_update_schema,
    product_variant_delete_schema,
    # Motorcycle Compatibility
    product_motorcycle_compatibility_list_schema,
    product_motorcycle_compatibility_create_schema,
    product_motorcycle_compatibility_retrieve_schema,
    product_motorcycle_compatibility_update_schema,
    product_motorcycle_compatibility_partial_update_schema,
    product_motorcycle_compatibility_delete_schema,
)

# =========================================================
# Product Views
# =========================================================


class ProductListCreateAPIView(APIView):
    """
    List all products or create a new product.

    GET:
        Returns a list of all active products.

    POST:
        Creates a new product.
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    @product_list_schema
    def get(self, request):
        products = (
            Product.objects.filter(is_active=True)
            .select_related(
                "brand",
                "category",
            )
            .prefetch_related(
                "images",
            )
        )

        serializer = ProductListSerializer(
            products,
            many=True,
        )

        return Response(
            {
                "count": products.count(),
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @product_create_schema
    def post(self, request):
        serializer = ProductCreateUpdateSerializer(
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "محصول با موفقیت ایجاد شد.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "message": "خطا در ایجاد محصول.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# =========================================================
# Product Detail Views
# =========================================================


class ProductRetrieveUpdateDestroyAPIView(APIView):
    """
    Retrieve, update, or delete a single product.
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, slug):
        return get_object_or_404(
            Product.objects.select_related(
                "brand",
                "category",
            ).prefetch_related(
                "images",
                "attribute_values__attribute",
                "variants__attribute_values__attribute",
                "variants__attribute_values__value",
                "motorcycle_compatibilities__motorcycle",
            ),
            slug=slug,
        )

    @product_retrieve_schema
    def get(self, request, slug):
        product = self.get_object(slug)

        serializer = ProductDetailSerializer(product)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @product_update_schema
    def put(self, request, slug):
        product = self.get_object(slug)

        serializer = ProductCreateUpdateSerializer(
            product,
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "محصول با موفقیت بروزرسانی شد.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "message": "خطا در بروزرسانی محصول.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @product_partial_update_schema
    def patch(self, request, slug):
        product = self.get_object(slug)

        serializer = ProductCreateUpdateSerializer(
            product,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "محصول با موفقیت بروزرسانی شد.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "message": "خطا در بروزرسانی محصول.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @product_delete_schema
    def delete(self, request, slug):
        product = self.get_object(slug)

        product.delete()

        return Response(
            {"message": "محصول با موفقیت حذف شد."},
            status=status.HTTP_200_OK,
        )


# =========================================================
# Product Image Views
# =========================================================


class ProductImageListCreateAPIView(APIView):
    """
    List all images for a product or create a new image.
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, product_id):
        return get_object_or_404(
            Product,
            pk=product_id,
        )

    @product_image_list_schema
    def get(self, request, product_id):
        product = self.get_object(product_id)

        images = product.images.all()

        serializer = ProductImageSerializer(
            images,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @product_image_create_schema
    def post(self, request, product_id):
        product = self.get_object(product_id)

        serializer = ProductImageCreateSerializer(
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save(
                product=product,
            )

            return Response(
                {
                    "message": "تصویر محصول با موفقیت ایجاد شد.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "message": "خطا در ایجاد تصویر محصول.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# =========================================================
# Product Image Detail
# =========================================================


class ProductImageRetrieveUpdateDestroyAPIView(APIView):
    """
    Retrieve, update, or delete a single product image.
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(
            ProductImage,
            pk=pk,
        )

    @product_image_retrieve_schema
    def get(self, request, pk):
        image = self.get_object(pk)

        serializer = ProductImageSerializer(image)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @product_image_update_schema
    def put(self, request, pk):
        image = self.get_object(pk)

        serializer = ProductImageCreateSerializer(
            image,
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "تصویر محصول با موفقیت بروزرسانی شد.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "message": "خطا در بروزرسانی تصویر محصول.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @product_image_partial_update_schema
    def patch(self, request, pk):
        image = self.get_object(pk)

        serializer = ProductImageCreateSerializer(
            image,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "تصویر محصول با موفقیت بروزرسانی شد.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "message": "خطا در بروزرسانی تصویر محصول.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @product_image_delete_schema
    def delete(self, request, pk):
        image = self.get_object(pk)

        image.delete()

        return Response(
            {"message": "تصویر محصول با موفقیت حذف شد."},
            status=status.HTTP_200_OK,
        )


# =========================================================
# Attribute Group Views
# =========================================================


class AttributeGroupListCreateAPIView(APIView):
    """
    List all attribute groups or create a new one.
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    @attribute_group_list_schema
    def get(self, request):
        groups = AttributeGroup.objects.filter(
            is_active=True,
        )

        serializer = AttributeGroupSerializer(
            groups,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @attribute_group_create_schema
    def post(self, request):
        serializer = AttributeGroupCreateUpdateSerializer(
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "گروه ویژگی با موفقیت ایجاد شد.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "message": "خطا در ایجاد گروه ویژگی.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# =========================================================
# Attribute Group Detail
# =========================================================


class AttributeGroupRetrieveUpdateDestroyAPIView(APIView):
    """
    Retrieve, update, or delete a single attribute group.
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(
            AttributeGroup,
            pk=pk,
        )

    @attribute_group_retrieve_schema
    def get(self, request, pk):
        group = self.get_object(pk)

        serializer = AttributeGroupSerializer(group)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @attribute_group_update_schema
    def put(self, request, pk):
        group = self.get_object(pk)

        serializer = AttributeGroupCreateUpdateSerializer(
            group,
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "گروه ویژگی با موفقیت بروزرسانی شد.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "message": "خطا در بروزرسانی گروه ویژگی.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @attribute_group_partial_update_schema
    def patch(self, request, pk):
        group = self.get_object(pk)

        serializer = AttributeGroupCreateUpdateSerializer(
            group,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "گروه ویژگی با موفقیت بروزرسانی شد.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "message": "خطا در بروزرسانی گروه ویژگی.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @attribute_group_delete_schema
    def delete(self, request, pk):
        group = self.get_object(pk)

        group.delete()

        return Response(
            {"message": "گروه ویژگی با موفقیت حذف شد."},
            status=status.HTTP_200_OK,
        )


# =========================================================
# Attribute Views
# =========================================================


class AttributeListCreateAPIView(APIView):
    """
    List all attributes or create a new one.
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    @attribute_list_schema
    def get(self, request):
        attributes = Attribute.objects.filter(is_active=True).select_related("group")

        serializer = AttributeSerializer(
            attributes,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @attribute_create_schema
    def post(self, request):
        serializer = AttributeCreateUpdateSerializer(
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "ویژگی با موفقیت ایجاد شد.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "message": "خطا در ایجاد ویژگی.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# =========================================================
# Attribute Detail
# =========================================================


class AttributeRetrieveUpdateDestroyAPIView(APIView):
    """
    Retrieve, update, or delete a single attribute.
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(
            Attribute,
            pk=pk,
        )

    @attribute_retrieve_schema
    def get(self, request, pk):
        attribute = self.get_object(pk)

        serializer = AttributeSerializer(attribute)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @attribute_update_schema
    def put(self, request, pk):
        attribute = self.get_object(pk)

        serializer = AttributeCreateUpdateSerializer(
            attribute,
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "ویژگی با موفقیت بروزرسانی شد.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "message": "خطا در بروزرسانی ویژگی.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @attribute_partial_update_schema
    def patch(self, request, pk):
        attribute = self.get_object(pk)

        serializer = AttributeCreateUpdateSerializer(
            attribute,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "ویژگی با موفقیت بروزرسانی شد.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "message": "خطا در بروزرسانی ویژگی.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @attribute_delete_schema
    def delete(self, request, pk):
        attribute = self.get_object(pk)

        attribute.delete()

        return Response(
            {"message": "ویژگی با موفقیت حذف شد."},
            status=status.HTTP_200_OK,
        )


# =========================================================
# Attribute Value Views
# =========================================================


class AttributeValueListCreateAPIView(APIView):
    """
    List all attribute values or create a new one.
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    @attribute_value_list_schema
    def get(self, request):
        values = AttributeValue.objects.filter(is_active=True).select_related(
            "attribute"
        )

        serializer = AttributeValueSerializer(
            values,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @attribute_value_create_schema
    def post(self, request):
        serializer = AttributeValueCreateUpdateSerializer(
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "مقدار ویژگی با موفقیت ایجاد شد.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "message": "خطا در ایجاد مقدار ویژگی.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# =========================================================
# Attribute Value Detail
# =========================================================


class AttributeValueRetrieveUpdateDestroyAPIView(APIView):
    """
    Retrieve, update, or delete a single attribute value.
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(
            AttributeValue,
            pk=pk,
        )

    @attribute_value_retrieve_schema
    def get(self, request, pk):
        value = self.get_object(pk)

        serializer = AttributeValueSerializer(value)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @attribute_value_update_schema
    def put(self, request, pk):
        value = self.get_object(pk)

        serializer = AttributeValueCreateUpdateSerializer(
            value,
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "مقدار ویژگی با موفقیت بروزرسانی شد.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "message": "خطا در بروزرسانی مقدار ویژگی.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @attribute_value_partial_update_schema
    def patch(self, request, pk):
        value = self.get_object(pk)

        serializer = AttributeValueCreateUpdateSerializer(
            value,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "مقدار ویژگی با موفقیت بروزرسانی شد.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "message": "خطا در بروزرسانی مقدار ویژگی.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @attribute_value_delete_schema
    def delete(self, request, pk):
        value = self.get_object(pk)

        value.delete()

        return Response(
            {"message": "مقدار ویژگی با موفقیت حذف شد."},
            status=status.HTTP_200_OK,
        )


# =========================================================
# Product Variant Views
# =========================================================


class ProductVariantListCreateAPIView(APIView):
    """
    List all variants for a product or create a new variant.
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, product_id):
        return get_object_or_404(
            Product,
            pk=product_id,
        )

    @product_variant_list_schema
    def get(self, request, product_id):
        product = self.get_object(product_id)

        variants = product.variants.all()

        serializer = ProductVariantSerializer(
            variants,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @product_variant_create_schema
    def post(self, request, product_id):
        product = self.get_object(product_id)

        serializer = ProductVariantCreateUpdateSerializer(
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save(
                product=product,
            )

            return Response(
                {
                    "message": "تنوع محصول با موفقیت ایجاد شد.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "message": "خطا در ایجاد تنوع محصول.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# =========================================================
# Product Variant Detail
# =========================================================


class ProductVariantRetrieveUpdateDestroyAPIView(APIView):
    """
    Retrieve, update, or delete a single product variant.
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(
            ProductVariant,
            pk=pk,
        )

    @product_variant_retrieve_schema
    def get(self, request, pk):
        variant = self.get_object(pk)

        serializer = ProductVariantDetailSerializer(variant)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @product_variant_update_schema
    def put(self, request, pk):
        variant = self.get_object(pk)

        serializer = ProductVariantCreateUpdateSerializer(
            variant,
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "تنوع محصول با موفقیت بروزرسانی شد.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "message": "خطا در بروزرسانی تنوع محصول.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @product_variant_partial_update_schema
    def patch(self, request, pk):
        variant = self.get_object(pk)

        serializer = ProductVariantCreateUpdateSerializer(
            variant,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "تنوع محصول با موفقیت بروزرسانی شد.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "message": "خطا در بروزرسانی تنوع محصول.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @product_variant_delete_schema
    def delete(self, request, pk):
        variant = self.get_object(pk)

        variant.delete()

        return Response(
            {"message": "تنوع محصول با موفقیت حذف شد."},
            status=status.HTTP_200_OK,
        )


# =========================================================
# Product Motorcycle Compatibility Views
# =========================================================


class ProductMotorcycleCompatibilityListCreateAPIView(APIView):
    """
    List all motorcycle compatibilities for a product
    or create a new compatibility.
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, product_id):
        return get_object_or_404(
            Product,
            pk=product_id,
        )

    @product_motorcycle_compatibility_list_schema
    def get(self, request, product_id):
        product = self.get_object(product_id)

        compatibilities = product.motorcycle_compatibilities.all()

        serializer = ProductMotorcycleCompatibilitySerializer(
            compatibilities,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @product_motorcycle_compatibility_create_schema
    def post(self, request, product_id):
        product = self.get_object(product_id)

        serializer = ProductMotorcycleCompatibilityCreateUpdateSerializer(
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save(
                product=product,
            )

            return Response(
                {
                    "message": "سازگاری موتورسیکلت با موفقیت ایجاد شد.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "message": "خطا در ایجاد سازگاری موتورسیکلت.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# =========================================================
# Motorcycle Compatibility Detail
# =========================================================


class ProductMotorcycleCompatibilityRetrieveUpdateDestroyAPIView(APIView):
    """
    Retrieve, update, or delete a single motorcycle compatibility.
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(
            ProductMotorcycleCompatibility,
            pk=pk,
        )

    @product_motorcycle_compatibility_retrieve_schema
    def get(self, request, pk):
        compatibility = self.get_object(pk)

        serializer = ProductMotorcycleCompatibilitySerializer(
            compatibility,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @product_motorcycle_compatibility_update_schema
    def put(self, request, pk):
        compatibility = self.get_object(pk)

        serializer = ProductMotorcycleCompatibilityCreateUpdateSerializer(
            compatibility,
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "سازگاری موتورسیکلت با موفقیت بروزرسانی شد.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "message": "خطا در بروزرسانی سازگاری موتورسیکلت.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @product_motorcycle_compatibility_partial_update_schema
    def patch(self, request, pk):
        compatibility = self.get_object(pk)

        serializer = ProductMotorcycleCompatibilityCreateUpdateSerializer(
            compatibility,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "سازگاری موتورسیکلت با موفقیت بروزرسانی شد.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "message": "خطا در بروزرسانی سازگاری موتورسیکلت.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @product_motorcycle_compatibility_delete_schema
    def delete(self, request, pk):
        compatibility = self.get_object(pk)

        compatibility.delete()

        return Response(
            {"message": "سازگاری موتورسیکلت با موفقیت حذف شد."},
            status=status.HTTP_200_OK,
        )
