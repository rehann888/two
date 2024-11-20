from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from products.models import Category, Product
from products.serializers import CategorySerializer, ProductSerializer


class CategoryList(APIView):
    def get(self, request):
        cache_key = "store:categories"
        categories = cache.get(cache_key)

        if not categories:
            queryset = Category.objects.all()
            serializer = CategorySerializer(queryset, many=True)
            categories = serializer.data
            cache.set(cache_key, categories, timeout=300)

        return Response(categories)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            cache.delete("store:categories")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetail(APIView):
    def get(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    def put(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            cache.delete("store:categories")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        cache.delete("store:categories")
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductList(APIView):
    def get(self, request):
        category_name = request.query_params.get("category")
        price_min = request.query_params.get("price_min")
        price_max = request.query_params.get("price_max")

        cache_key = f"store:products:{category_name or ''}:{price_min or ''}:{price_max or ''}"
        products = cache.get(cache_key)

        if not products:
            queryset = Product.objects.all()
            if category_name:
                queryset = queryset.filter(category__name__icontains=category_name)
            if price_min:
                queryset = queryset.filter(price__gte=price_min)
            if price_max:
                queryset = queryset.filter(price__lte=price_max)

            serializer = ProductSerializer(queryset, many=True)
            products = serializer.data
            cache.set(cache_key, products, timeout=300)

        return Response(products)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            cache.delete_pattern("store:products*")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetail(APIView):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            cache.delete_pattern("store:products*")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        cache.delete_pattern("store:products*")
        return Response({"message": "Product deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
