from collections import defaultdict
from time import time

from django import forms
from django.forms import ModelForm, Textarea
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from django.core.exceptions import *
from django.core.context_processors import csrf
from django.db.models import Q
from django.db import connection, transaction
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib import messages
from django.template import RequestContext

from dbe.ratev.models import *
from dbe.settings import ROOT_URL

from dbe.mcbv.base import TemplateView

_avg_sim = 70.0     # average similarity for similarity calculations

modeldict = dict(
                 artist   = (Artist, Album, AlbumRating),
                 album    = (Album, Track, TrackRating),
                 author   = (Author, Book, BookRating),
                 director = (Director, Film, FilmRating),
                 )


class Stats(TemplateView):
    template_name = "ratev/stats.html"

    def add_context(self):
        # show obj.count()
        return dict(models=(User, Artist, Album, Track, Author, Book, Director, Film))


@login_required
def add(request, ltype, id=None):
    """Add item(s). ltype: track|album|book|film"""
    p, u = request.POST, request.user

    for name, (main, contained, ratecls) in modeldict.items():
        if name == ltype:
            itemcls = cls
        elif contained.__class__.lower() == ltype:
            itemcls   = contained
            ratingcls = ratecls
            cls       = main
            clsname   = cls.__name__.lower()

    noparent = bool(ltype in ["artist", "author", "director"])

    if request.method == "POST":
        add = defaultdict(dict)
        for k, v in request.POST.items():
            if k.startswith("name_"):
                num = k[5:]
                add[num]["name"] = v
            elif k.startswith("rating_"):
                num = k[7:]
                add[num]["rating"] = v

        list_added = []
        for _, item in add.items():
            name = item["name"].strip()
            if name:
                if noparent:
                    items = itemcls.obj.filter(name__iexact=name)
                    if items:
                        list_added.append(items[0])
                        continue
                else:
                    lkupdict = {"name__iexact": name, clsname: id }
                    if itemcls.obj.filter(**lkupdict):
                        continue

                # track can only belong to one album, other items can belong to multiple
                # parents
                if ltype == "track":
                    album = Album.obj.get(pk=int(id))
                    mkdict = {"name": name, "added_by": u, clsname: album}
                    obj = itemcls.obj.create(**mkdict)
                    for artist in album.artist.all():
                        obj.artist.add(artist)
                elif ltype in "album book film".split():
                    obj = itemcls.obj.create(**dict(name=name, added_by=u))
                    getattr(obj, clsname).add(id)
                else:
                    obj = itemcls.obj.create(name=name, added_by=u)
                    list_added.append(obj)

                if "rating" in item.keys():
                    rating = item["rating"].strip()
                    if rating:
                        mkdict = {str(ltype): obj, "rating": int(rating), "user": u}
                        ratecls.obj.create(**mkdict)

        if noparent:
            d = dict(user=u, ltype=ltype, list_added=list_added)
            d.update(csrf(request))
            return render_to_response("ratev/added.html", d)
        else:
            # Added items that belong to a parent, redir to page of parent
            return HttpResponseRedirect("/ratev/%s/%s/" % (clsname, id))
    d = dict(user=request.user, ltype=ltype, id=id, fields=range(15), noparent=noparent)
    d.update(csrf(request))
    return render_to_response("ratev/add.html", d)

@login_required
def listitems(request, ltype="artist", id='1'):
    """List items: artists / bands, tracks, books, films."""
    cls, listcls, ratingcls = modeldict[ltype]
    listlkup = listcls.__name__.lower()

    # update ratings
    if request.method == "POST":
        updated = False
        for k, v in request.POST.items():
            if k.startswith("id_") and v.strip():
                obj = listcls.obj.get(pk=int(k[3:]))
                try    : newrating = int(v.strip())
                except : return HttpResponse("Error parsing score: '%s'" % v)

                # get or create a rating object and update the score if it's different
                lookup_dict = {"user": request.user, listlkup: obj}
                arating = ratecls.obj.get_or_create(**lookup_dict)[0]
                if arating.rating != newrating:
                    arating.update(rating=newrating)
                    obj.update(rated=True)
                    updated = True
        if updated:
            messages.info(request, "Score(s) updated.")

    # make a list of all items that belong to current object
    obj         = cls.obj.get(pk=int(id))
    lookup_dict = {str(ltype): obj}
    results     = listcls.obj.filter(**lookup_dict)
    no_add      = bool(ltype == "album" and obj.added_by != request.user)

    # lookup ratings
    lst = []
    for res in results:
        rating = ''
        lookup_dict = {"user": request.user, listlkup: res}
        try    : rating = ratecls.obj.get(**lookup_dict).rating
        except : pass
        lst.append((res.id, res.name, rating, recommend(request.user, listlkup, res)))

    d = dict(results=lst, id=id, ltype=ltype, itemtype=listlkup, name=obj.name, user=request.user, no_add=no_add)
    d.update(csrf(request))
    return render_to_response("ratev/list.html", d, context_instance=RequestContext(request))

@login_required
def make_recommendations(request):
    """Create recommendations for all users."""
    start  = time()
    debug  = []
    cursor = connection.cursor()

    for u in User.objects.all():
        Recommendations.obj.filter(user=u).delete()     # delete stale recommendations
        # find ratings by users who are similar enough (75+) to the user we're looping over
        q = """SELECT sim.similarity, r.rating FROM ratev_similarity as sim,
          ratev_%srating as r WHERE (sim.user1_id=%%s OR sim.user2_id=%%s) AND
          (r.user_id=sim.user1_id OR r.user_id=sim.user2_id) AND r.user_id != %%s AND
          r.%s_id=%%s AND sim.similarity >= 70"""

        for _, itemcls, ratingcls in modeldict.values():
            for item in itemcls.obj.all():
                itype = itemcls.__name__.lower()
                # proceed only if user does not have rating for this item
                lookup_dict = {"user": u, itype: item}
                if not ratingcls.objects.filter(**lookup_dict):
                    cursor.execute(q % (itype, itype), [u.pk, u.pk, u.pk, item.id])
                    rows = cursor.fetchall()
                    if rows:
                        # calculate an average rating
                        total      = sum(sim*rating for sim, rating in rows)
                        rec_rating = int(round(total / (len(rows)*_avg_sim)))

                        # save recommendation to the DB
                        if rec_rating > 70:
                            obj = Recommendations.obj.create(user=u, itype=itype, itemid=item.id, rating=rec_rating)
    debug.append("%ss total." % int(time()-start))
    return HttpResponse("%s<br /> <h2>Recommendations Update Done</h2>" % join(debug, "<br />"))


class RecommendationsView(ListView):
    list_model    = Recommendations
    paginate_by   = 70
    template_name = "recommendations.html"

    def get_list_queryset(self):
        recs     = Recommendations.obj.filter(user=self.user)
        rec_dict = defaultdict(list)

        for rec in recs:
            cls  = rec.itype.__class__
            item = cls.obj.get(pk=rec.itemid)
            rec_dict[rec.itype].append((rec.rating, item))

        newlst = []
        for itype, lst in rec_dict.items():
            for rating, item in lst:
                newlst.append((itype, rating, item))
        return newlst


def recommend(u, itype, item):
    """Return recommendation score for specified user and item."""
    cursor = connection.cursor()
    q = """SELECT sim.similarity, r.rating FROM ratev_similarity as sim,
      ratev_%srating as r WHERE (sim.user1_id=%%s OR sim.user2_id=%%s) AND
      (r.user_id=sim.user1_id OR r.user_id=sim.user2_id) AND r.user_id != %%s AND
      r.%s_id=%%s""" % (itype, itype)

    cursor.execute(q, [u.pk, u.pk, u.pk, item.id])
    rows       = cursor.fetchall()
    total      = sum(sim*rating for sim, rating in rows)
    rec_rating = int(round(total / (len(rows)*_avg_sim))) if rows else ''
    return rows, rec_rating


class SearchView(PaginatedSearch):
    template_name = "ratev/search.html"
    paginate_by   = 20

    def get_list_queryset(self):
        return self.cls.obj.filter(name__icontains=self.data.q)

    def form_valid(self, form):
        self.data = form.cleaned_data
        self.cls  = modeldict[self.data.stype][0]


def ratev_context(request):
    return dict(user=request.user)
