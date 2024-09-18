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


class ResidentViewSet(viewsets.ModelViewSet):
    queryset = Resident.objects.all()
    serializer_class = ResidentSerializer

    def get_permissions(self):
        if self.action in ['get_current_user', 'lock_account', 'check_account_status', 'change_password','delete_resident']:
            return [permissions.IsAuthenticated()]
        elif self.action == 'create_new_account':
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Resident.objects.all()
        elif user.is_staff:
            return Resident.objects.filter(id=user.id)
        return Resident.objects.none()

    @action(methods=['get', 'patch'], url_path='current-user', detail=False)
    def get_current_user(self, request):
        user = request.user
        if request.method == 'PATCH':
            for k, v in request.data.items():
                setattr(user, k, v)
            user.save()
        return Response(ResidentSerializer(user, context={'request': request}).data)

    @action(methods=['post'], detail=True, url_path='lock-account')
    def lock_account(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'status': 'account locked'}, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='check-account-status')
    def check_account_status(self, request, pk=None):
        user = self.get_object()
        return Response({'is_active': user.is_active}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False, url_path='change-password')
    def change_password(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not user.check_password(old_password):
            return Response({'error': 'Mật khẩu cũ không chính xác.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({'message': 'Đã thay đổi mật khẩu thành công.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'], url_path='change-avatar', parser_classes=[MultiPartParser, FormParser])
    def change_avatar(self, request):
        user = request.user
        if 'avatar' not in request.data:
            return Response({"error": "Avatar is required"}, status=status.HTTP_400_BAD_REQUEST)

        avatar = request.data['avatar']
        user.avatar = avatar
        user.save()

        return Response({"message": "Avatar updated successfully"}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)



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
<<<<<<< HEAD
=======

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

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = BillSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        resident = self.request.user
        queryset = Bill.objects. filter(resident=resident, payment_status='UNPAID')
        return queryset

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(payment_status='PAID')
        return Response(serializer.data)

@csrf_exempt
def payment_view(request: HttpRequest):
    partnerCode = "MOMO"
    accessKey = "F8BBA842ECF85"
    secretKey = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
    requestId = f"{partnerCode}{int(time.time() * 1000)}"
    orderId = 'MM' + str(int(time.time() * 1000))
    orderInfo = "pay with MoMo"
    redirectUrl = "https://momo.vn/return"
    ipnUrl = "https://callback.url/notify"
    amount = request.headers.get('amount', '')
    requestType = "payWithATM"
    extraData = ""

    # Construct raw signature
    rawSignature = f"accessKey={accessKey}&amount={amount}&extraData={extraData}&ipnUrl={ipnUrl}&orderId={orderId}&orderInfo={orderInfo}&partnerCode={partnerCode}&redirectUrl={redirectUrl}&requestId={requestId}&requestType={requestType}"

    # Generate signature using HMAC-SHA256
    signature = hmac.new(secretKey.encode(), rawSignature.encode(), hashlib.sha256).hexdigest()

    # Create request body as JSON
    data = {
        "partnerCode": partnerCode,
        "accessKey": accessKey,
        "requestId": requestId,
        "amount": amount,
        "orderId": orderId,
        "orderInfo": orderInfo,
        "redirectUrl": redirectUrl,
        "ipnUrl": ipnUrl,
        "extraData": extraData,
        "requestType": requestType,
        "signature": signature,
        "lang": "vi"
    }

    # Send request to MoMo endpoint
    url = 'https://test-payment.momo.vn/v2/gateway/api/create'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=data, headers=headers)

    # Process response
    if response.status_code == 200:
        response_data = response.json()
        pay_url = response_data.get('payUrl')
        return JsonResponse(response_data)
    else:
        return JsonResponse({"error": f"Failed to create payment request. Status code: {response.status_code}"},
                            status=500)
>>>>>>> 863b52477a72dacf079b14944bc84898a6b5cedf




class SurveyViewSet(viewsets.ModelViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        survey = self.get_object()
        serializer = self.serializer_class(survey)
        return Response(serializer.data)



class SurveyResultViewSet(viewsets.ModelViewSet):
    queryset = SurveyResult.objects.all()
    serializer_class = SurveyResultSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return SurveyResult.objects.all()
        elif user.is_staff:
            return SurveyResult.objects.filter(id=user.id)
        return SurveyResult.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(resident=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)



    def retrieve(self, request, pk=None):
        survey_result = self.get_object()
        serializer = self.get_serializer(survey_result)
        return Response(serializer.data)

    def update(self, request, pk=None):
        survey_result = self.get_object()
        if survey_result.resident != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(survey_result, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        survey_result = self.get_object()
        if survey_result.resident != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        survey_result.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)