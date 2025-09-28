from django.urls import path,include

from rest_framework.routers import DefaultRouter
from .views import CreateCheckoutSession,PlanView,PauseSubscription,ResumeSubscription,StopSubscription,SubscriptionSerializerView,SubcriptionFullStatusDetailView
from .webhooks import stripe_webhook
router =DefaultRouter()
router.register('list',PlanView,basename='plan')

urlpatterns = [
    path('',include(router.urls)),
    path("create-checkout-session/", CreateCheckoutSession.as_view(), name="checkout"),
    path("subscription/<int:subscription_id>/pause/", PauseSubscription.as_view()),
    path("subscription/<int:subscription_id>/stop/", StopSubscription.as_view()),
    path("subscription/<int:subscription_id>/resume/", ResumeSubscription.as_view()),
    path("webhook/",stripe_webhook, name="stripe-webhook"),
    path("subscription/",SubscriptionSerializerView.as_view()),
    path('subscription/status_details/',SubcriptionFullStatusDetailView.as_view()),
    
]
