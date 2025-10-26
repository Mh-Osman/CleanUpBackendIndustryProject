from django.urls import path,include

from rest_framework.routers import DefaultRouter
from .views import PlanView,PauseSubscription,ResumeSubscription,StopSubscription,SubscriptionSerializerView,SubcriptionFullStatusDetailView,InvoiceView,CalculationsForInvoiceView,SubscriptionListCreateView,ServiceLineItemView
# from .webhooks import stripe_webhook

router =DefaultRouter()
router.register('list',PlanView,basename='plan')
# <<<<<<< HEAD
router.register('invoice/list',InvoiceView)
#router.register('subscriptions-create',SubscriptionListCreateView,basename='subscription-list-create')

router.register('invoice/list',InvoiceView,basename='invoice')
router.register('subscriptions-create',SubscriptionListCreateView,basename='subscription-create')
router.register('service-line-items',ServiceLineItemView,basename='service-line-items')
#>>>>>>> origin/new-testing

urlpatterns = [
    path('',include(router.urls)),
    # path("create-checkout-session/", CreateCheckoutSession.as_view(), name="checkout"),
    # path('subscriptions-create/',SubscriptionListCreateView, name='subscription-list-create'),
    path("subscription/<int:subscription_id>/pause/", PauseSubscription.as_view()),
    path("subscription/<int:subscription_id>/stop/", StopSubscription.as_view()),
    path("subscription/<int:subscription_id>/resume/", ResumeSubscription.as_view()),
    # path("webhook/",stripe_webhook, name="stripe-webhook"),
    path("subscription/",SubscriptionSerializerView.as_view()),
    path('subscription/status_details/',SubcriptionFullStatusDetailView.as_view()),
    path('calculations/',CalculationsForInvoiceView.as_view()),
    
    
    
]
