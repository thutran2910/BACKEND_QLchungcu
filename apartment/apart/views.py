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
