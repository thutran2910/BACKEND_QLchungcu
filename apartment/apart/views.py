import hashlib
import hmac
from datetime import time
import requests
from django.db.models import Max
from django.shortcuts import render, get_object_or_404
from django.http import Http404, JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from . import paginators
from .models import Flat, Item, Resident, Feedback, Survey, SurveyResult, Bill, FaMember, Cart, Product, CartProduct, \
    Order, OrderProduct
from .serializers import ResidentSerializer, FlatSerializer, ItemSerializer, FeedbackSerializer, SurveySerializer, \
    SurveyResultSerializer, BillSerializer, FaMemberSerializer, CartSerializer, ProductSerializer, \
    CartProductSerializer, OrderSerializer



class BillViewSet(viewsets.ModelViewSet):
    serializer_class = BillSerializer
    #pagination_class = paginators.Paginator
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        resident = self.request.user
        if resident.is_superuser:
            queryset = Bill.objects.all()
        else:
            queryset = Bill.objects.filter(resident=resident)

        payment_status = self.request.query_params.get('payment_status', None)
        if payment_status:
            queryset = queryset.filter(payment_status=payment_status.upper())
        return queryset

    @action(methods=['get'], detail=False, url_path='total-bills')
    def total_bills(self, request, *args, **kwargs):
        resident = self.request.user
        if resident.is_superuser:
            bills = Bill.objects.all()
        else:
            bills = Bill.objects.filter(resident=resident)

        total_bills = bills.count()

        return Response({'total_bills': total_bills}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False, url_path='create-bill')
    def create_bill(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({"error": "Only superusers can create bills"}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['delete'], url_path='delete-bill')
    def delete_bill(self, request, pk=None):
        try:
            bill = self.get_object()
            bill.delete()
            return Response({"message": "Bill deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
        except Bill.DoesNotExist:
            return Response({"error": "Bill not found."}, status=status.HTTP_404_NOT_FOUND)
