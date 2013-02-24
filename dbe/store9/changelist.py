from random import choice
from string import join

from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response

from django import forms, template
from django.contrib.admin import helpers
from django.utils.translation import ungettext, ugettext_lazy
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _
from django.db.models.fields import BLANK_CHOICE_DASH
from django.core.urlresolvers import reverse
from django.contrib.admin.views.main import ERROR_FLAG

from store9.models import Product, Item, CartItem, Order, Contact
from store9.main import ChangeList
import settings

ACTION_CHECKBOX_NAME = "_selected_action"
action_choices = BLANK_CHOICE_DASH + [ ("make_active", u"Make Active"),
                                       ("make_inactive", u"Make Inactive"),
                                       ("add_to_cart", u"Add to Cart")
                                     ]


def make_active(request, queryset):
    """Make item active action."""
    queryset.update(active=True)

def make_inactive(request, queryset):
    """Make item inactive action."""
    queryset.update(active=False)

def add_to_cart(request, queryset):
    """Add all items to cart."""
    from store9.views import add_item
    for item in queryset:
        add_item(request.user, item.pk)
    return HttpResponseRedirect(reverse("store9.views.cart"))

def randseq():
    """Random sequence."""
    length = choice(range(4,12))
    return join([x for x in [choice("ACGT") for y in range(length)]], '')

@login_required
def changelist_view(request):
    """Item listing."""
    # for x in range(125): Item(name='', sequence=randseq(), user=request.user).save()

    # init vars
    model = Item
    actions = [make_active, make_inactive, add_to_cart]
    list_editable = ()
    search_fields = ("name", "sequence")
    search_fields = ()
    list_filter = ["active"]
    list_per_page = 40
    list_select_related = False
    date_hierarchy = None
    filter_horizontal = False
    filter_vertical = True
    list_display = ["action_checkbox", "name", "sequence", "_length", "notes", "_contact",
                    "_owner", "_royalty_rate", "date_added", "sort_order", "active"]
    list_display_links = ["name", "sequence"]

    # Remove action checkboxes if there aren't any actions available.
    if not actions:
        try: list_display.remove("action_checkbox")
        except ValueError: pass

    cl = ChangeList(request, model, list_display, list_display_links, list_filter,
           date_hierarchy, search_fields, list_select_related, list_per_page, list_editable)

    action_failed = False
    selected = request.POST.getlist(ACTION_CHECKBOX_NAME)

    # Actions with no confirmation
    if (actions and request.method == "POST" and
            "index" in request.POST and "_save" not in request.POST):
        if selected:
            response = response_action(request, queryset=cl.get_query_set())
            if response:
                return response
            else:
                action_failed = True
        else:
            msg = _("Items must be selected in order to perform "
                    "actions on them. No items have been changed.")
            messages.info(request, msg)
            action_failed = True

    # Build the action form and populate it with available actions.
    action_form = None
    if actions:
        action_form = helpers.ActionForm(auto_id=None)
        action_form.fields["action"].choices = action_choices

    selection_note_all = ungettext("%(total_count)s selected",
        "All %(total_count)s selected", cl.result_count)

    js = ["js/jquery.min.js", "js/jquery.init.js", "js/inlines.min.js", "js/actions.min.js",
          "js/core.js", "js/admin/RelatedObjectLookups.js"]
    if filter_vertical or filter_horizontal:
        js.extend(["js/SelectBox.js" , "js/SelectFilter2.js"])
    media = forms.Media(js=["%s%s" % (settings.ADMIN_MEDIA_PREFIX, url) for url in js])

    context = {
        "module_name": u"Items",
        "selection_note": _("0 of %(cnt)s selected") % {"cnt": len(cl.result_list)},
        "selection_note_all": selection_note_all % {"total_count": cl.result_count},
        "title": cl.title,
        "is_popup": cl.is_popup,
        "cl": cl,
        "media": media,
        "action_form": action_form,
        "actions_on_top": True,
        "actions_selection_counter": True,
    }
    context_instance = template.RequestContext(request, current_app="Store9")
    return render_to_response("adminapp/c_list.html", context, context_instance=context_instance)


def response_action(request, queryset):
    """ Handle an action. This is called if a request is POSTed to the changelist; it returns an
        HttpResponse if the action was handled, and None otherwise.
    """

    # There can be multiple action forms on the page (at the top
    # and bottom of the change list, for example). Get the action
    # whose button was pushed.
    try:
        action_index = int(request.POST.get('index', 0))
    except ValueError:
        action_index = 0

    # Construct the action form.
    data = request.POST.copy()
    data.pop(ACTION_CHECKBOX_NAME, None)
    data.pop("index", None)

    # Use the action whose button was pushed
    try:
        data.update({"action": data.getlist("action")[action_index]})
    except IndexError:
        # If we didn't get an action from the chosen form that's invalid
        # POST data, so by deleting action it'll fail the validation check
        # below. So no need to do anything here
        pass

    action_form = helpers.ActionForm(data, auto_id=None)
    action_form.fields["action"].choices = action_choices
    actions_dict = { "make_active": (make_active, "make_active", "Make Active"),
                     "make_inactive": (make_inactive, "make_inactive", "Make Inactive"),
                     "add_to_cart": (add_to_cart, "add_to_cart", "Add to Cart"),
                   }

    if action_form.is_valid():
        action = action_form.cleaned_data["action"]
        select_across = action_form.cleaned_data["select_across"]
        func, name, description = actions_dict[action]

        # Get the list of selected PKs. If nothing's selected, we can't perform an action on it,
        # so bail. Except we want to perform the action explicitly on all objects.
        selected = request.POST.getlist(ACTION_CHECKBOX_NAME)
        if not selected and not select_across:
            messages.info(request, _("Items must be selected in order to perform "
                                     "actions on them. No items have been changed."))
            return None

        if not select_across:
            # Perform the action only on the selected objects
            queryset = queryset.filter(pk__in=selected)

        response = func(request, queryset)

        # Actions may return an HttpResponse, which will be used as the response from the POST. If
        # not, we'll be a good little HTTP citizen and redirect back to the changelist page.
        if isinstance(response, HttpResponse):
            return response
        else:
            return HttpResponseRedirect(".")
    else:
        messages.info(request, _("No action selected."))
        return None
