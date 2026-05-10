from rest_framework.views import APIView
from .serializers import UserSerializer, ListingSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, BasePermission, SAFE_METHODS
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from .models import Listing


class HomeView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        content = {'message': f'Welcome to the JWT Authentication page using React Js and Django {request.user}!'}
        return Response({"ok": True, "data": content})


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):

        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"ok": True, "data": {"message": "Logged out"}}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(
                {
                    "ok": False,
                    "error": {
                        "code": "invalid_refresh_token",
                        "message": "Refresh token is invalid.",
                        "details": {},
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"ok": True, "data": serializer.data}, status=status.HTTP_201_CREATED)


class ListingPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = "page_size"
    max_page_size = 50


class IsListingOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and obj.created_by_id == request.user.id


class ListingListCreateView(ListCreateAPIView):
    serializer_class = ListingSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Listing.objects.select_related("created_by").all()
    pagination_class = ListingPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        city = self.request.query_params.get("city")
        search = self.request.query_params.get("search")
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")
        ordering = self.request.query_params.get("ordering")

        if city:
            queryset = queryset.filter(city__icontains=city)
        if search:
            queryset = queryset.filter(title__icontains=search)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        ordering_map = {
            "price_asc": "price",
            "price_desc": "-price",
            "date_asc": "created_at",
            "date_desc": "-created_at",
        }
        queryset = queryset.order_by(ordering_map.get(ordering, "-created_at"))
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(
            {
                "ok": True,
                "data": serializer.data,
            }
        )

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data = {"ok": True, "data": response.data}
        return response


class ListingDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ListingSerializer
    queryset = Listing.objects.select_related("created_by").all()
    permission_classes = (IsListingOwnerOrReadOnly,)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        response.data = {"ok": True, "data": response.data}
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        response.data = {"ok": True, "data": response.data}
        return response

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"ok": True, "data": {"message": "Listing deleted"}}, status=status.HTTP_200_OK)
