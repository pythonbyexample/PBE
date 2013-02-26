from django.conf.urls.defaults import *
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from dbe.store9.views import *

urlpatterns = patterns("dbe.store9.views",
    (r"^profile/$"                 , login_required(ProfileView.as_view()), {}, "sprofile"),
    (r"^addresses/$"               , login_required(AddressBookView.as_view()), {}, "addresses"),

    (r"^additem/(?P<dpk>(\w+))/$"  , login_required(AddToCartView.as_view()), {}, "additem"),
    (r"^cart/$"                    , login_required(CartView.as_view()), {}, "cart"),
    (r"^checkout/$"                , login_required(CheckoutView.as_view()), {}, "checkout"),
    (r"^your_order/$"              , login_required(YourOrderView.as_view()), {}, "your_order"),

    (r"^item/new/$"                , login_required(AddItemsView.as_view()), {}, "many_new_items"),
    (r"^item/(?P<mfpk>(\w+))/$"    , login_required(ItemView.as_view()), {}, "view_item"),
    (r"^item/$"                    , login_required(ItemsView.as_view()), {}, "items"),
    (r"^$"                         , IndexView.as_view(), {}, "sindex"),
)

# the default django-registration url spans 2 lines in email, which is not reliable so add a custom url
# urlpatterns += patterns('',
   # url(r"^pwd/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$",
       # auth_views.password_reset_confirm, name="auth_password_reset_confirm"),
# )

# urlpatterns += patterns('', (r"^account/", include("registration.urls")),)
