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

from ratev.ratev.models import *
from ratev.settings import ROOT_URL

_avg_sim = 70.0     # average similarity for similarity calculations

@login_required
def stats(request):
    """Show statistics: users, artists, albums, tracks, authors, books, directors, films."""
    return HttpResponse(""" <table>
    <tr><td>users: <td>%s</td></tr>
    <tr><td>artists: <td>%s</td></tr>
    <tr><td>albums: <td>%s</td></tr>
    <tr><td>tracks: <td>%s</td></tr>
    <tr><td>authors: <td>%s</td></tr>
    <tr><td>books: <td>%s</td></tr>
    <tr><td>directors: <td>%s</td></tr>
    <tr><td>films: <td>%s</td></tr>
    </table> """ % (User.objects.count(), Artist.objects.count(),
           Album.objects.count(), Track.objects.count(), Author.objects.count(),
           Book.objects.count(), Director.objects.count(), Film.objects.count(), ))

@login_required
def add(request, ltype, id=None):
    """Add item(s). ltype: track|album|book|film"""
    p, u = request.POST, request.user
    noparent = False
    if ltype == "film": cls = Director; itemcls = Film; ratecls = FilmRating
    elif ltype == "book": cls = Author; itemcls = Book; ratecls = BookRating
    elif ltype == "album": cls = Artist; itemcls = Album; ratecls = AlbumRating
    elif ltype == "track": cls = Album; itemcls = Track; ratecls = TrackRating
    elif ltype == "artist": itemcls = Artist
    elif ltype == "author": itemcls = Author
    elif ltype == "director": itemcls = Director
    if ltype in "artist author director".split():
        noparent = True     # to keep things simple we only rate items not authors

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
                    items = itemcls.objects.filter(name__iexact=name)
                    if items:
                        list_added.append(items[0])
                        print "skipping", name
                        continue
                else:
                    lkupdict = {"name__iexact": name, cls.__name__.lower(): id, }
                    if itemcls.objects.filter(**lkupdict):
                        print "skipping", name
                        continue

                # track can only belong to one album, other items can belong to multiple
                # parents
                if ltype == "track":
                    album = Album.objects.get(pk=int(id))
                    mkdict = {"name": name, "added_by": u, cls.__name__.lower(): album, }
                    obj = itemcls.objects.create(**mkdict)
                    for artist in album.artist.all():
                        obj.artist.add(artist)
                elif ltype in "album book film".split():
                    mkdict = {"name": name, "added_by": u}
                    obj = itemcls.objects.create(**mkdict)
                    getattr(obj, cls.__name__.lower()).add(id)
                else:
                    obj = itemcls.objects.create(name=name, added_by=u)
                    list_added.append(obj)

                if "rating" in item.keys():
                    rating = item["rating"].strip()
                    if rating:
                        mkdict = {str(ltype): obj, "rating": int(rating), "user": u}
                        ratecls.objects.create(**mkdict)

        if noparent:
            # return HttpResponseRedirect("/ratev/")
            d = {"user": request.user, "ltype": ltype, "list_added": list_added}
            d.update(csrf(request))
            return render_to_response("ratev/added.html", d)
        else:
            # Added items that belong to a parent, redir to page of parent
            return HttpResponseRedirect("/ratev/%s/%s/" % (cls.__name__.lower(), id))
    d = {"user": request.user, "ltype": ltype, "id": id, "fields": range(15),
      "noparent": noparent}
    d.update(csrf(request))
    return render_to_response("ratev/add.html", d)

@login_required
def listitems(request, ltype="artist", id='1'):
    """List items: artists / bands, tracks, books, films."""
    no_add = False      # don't show add item link
    if ltype == "artist":
        cls = Artist; listcls = Album; listlkup = "album"; ratecls = AlbumRating
    elif ltype == "album":
        cls = Album; listcls = Track; listlkup = "track"; ratecls = TrackRating
    elif ltype == "author":
        cls = Author;  listcls = Book; listlkup = "book"; ratecls = BookRating
    elif ltype == "director":
        cls = Director; listcls = Film; listlkup = "film"; ratecls = FilmRating

    # update ratings
    if request.method == "POST":
        updated = False
        for k, v in request.POST.items():
            if k.startswith("id_") and v.strip():
                obj = listcls.objects.get(pk=int(k[3:]))
                try: newrating = int(v.strip())
                except: return HttpResponse("Error parsing score: '%s'" % v)

                # get or create a rating object and update the score if it's different
                lookup_dict = {"user": request.user, listlkup: obj}
                arating = ratecls.objects.get_or_create(**lookup_dict)[0]
                if arating.rating != newrating:
                    arating.rating = newrating
                    arating.save()
                    if not obj.rated:
                        obj.rated = True
                        obj.save()
                    updated = True
        if updated:
            messages.info(request, "Score(s) updated.")

    # make a list of all items that belong to current object
    obj = cls.objects.get(pk=int(id))
    lookup_dict = {str(ltype): obj}
    results = listcls.objects.filter(**lookup_dict)
    if ltype == "album" and obj.added_by != request.user:
        no_add = True

    # lookup ratings
    lst = []
    for res in results:
        rating = ''
        lookup_dict = {"user": request.user, listlkup: res}
        try: rating = ratecls.objects.get(**lookup_dict).rating
        except: pass
        lst.append((res.id, res.name, rating, recommend(request.user, listlkup, res)))

    d = {"results": lst, "id": id, "ltype": ltype, "itemtype": listlkup, "name": obj.name,
        "user": request.user, "no_add": no_add}
    d.update(csrf(request))
    return render_to_response("ratev/list.html", d, context_instance=RequestContext(request))

@login_required
def make_recommendations(request):
    """Create recommendations for all users."""
    start = time()
    debug = []
    cursor = connection.cursor()
    for u in User.objects.all():
        Recommendations.objects.filter(user=u).delete()     # delete stale recommendations
        # find ratings by users who are similar enough (75+) to the user we're looping over
        q = """SELECT sim.similarity, r.rating FROM ratev_similarity as sim,
          ratev_%srating as r WHERE (sim.user1_id=%%s OR sim.user2_id=%%s) AND
          (r.user_id=sim.user1_id OR r.user_id=sim.user2_id) AND r.user_id != %%s AND
          r.%s_id=%%s AND sim.similarity >= 70"""
        for itype in "album track book film".split():
            itemcls = eval(itype.capitalize())      # e.g. Album
            for item in itemcls.objects.all():
                item_rate_cls = eval(itype.capitalize() + "Rating")     # e.g. AlbumRating

                # proceed only if user does not have rating for this item
                lookup_dict = {"user": u, itype: item}
                if not item_rate_cls.objects.filter(**lookup_dict):
                    cursor.execute(q % (itype, itype), [u.pk, u.pk, u.pk, item.id])
                    rows = cursor.fetchall()
                    if rows:
                        # calculate an average rating
                        sum = 0
                        for sim, rating in rows:
                            sum += sim * rating
                        rec_rating = int(round(sum / (len(rows)*_avg_sim)))

                        # save recommendation to the DB
                        if rec_rating > 70:
                            obj = Recommendations.objects.create(user=u, itype=itype,
                              itemid=item.id, rating=rec_rating)
    debug.append("%ss total." % int(time()-start))
    return HttpResponse("%s<br /> <h2>Recommendations Update Done</h2>" % join(debug, "<br />"))

def recommendations(request):
    """My recommendations listing for current user."""
    u = request.user
    recs = Recommendations.objects.filter(user=u)
    rec_dict = defaultdict(list)
    for rec in recs:
        cls = eval(rec.itype.capitalize())
        item = cls.objects.get(pk=rec.itemid)
        rec_dict[rec.itype].append((rec.rating, item))
    for lst in rec_dict.values():
        lst.sort(reverse=True)
    newlst = []
    for itype, lst in rec_dict.items():
        for rating, item in lst:
            newlst.append((itype, rating, item))

    # paginate results
    paginator = Paginator(newlst, 70)
    try: page = int(request.GET.get("page", '1'))
    except ValueError: page = 1

    try: r = paginator.page(page)
    except: r = paginator.page(paginator.num_pages)
    return render_to_response("recommendations.html", {"recommendations": r, "user": u})

def recommend(u, itype, item):
    """Return recommendation score for specified user and item."""
    cursor = connection.cursor()
    q = """SELECT sim.similarity, r.rating FROM ratev_similarity as sim,
      ratev_%srating as r WHERE (sim.user1_id=%%s OR sim.user2_id=%%s) AND
      (r.user_id=sim.user1_id OR r.user_id=sim.user2_id) AND r.user_id != %%s AND
      r.%s_id=%%s""" % (itype, itype)
    cursor.execute(q, [u.pk, u.pk, u.pk, item.id])
    rows = cursor.fetchall()
    sum = 0
    for sim, rating in rows:
        sum += sim * rating

    if not rows: rec_rating = ''
    else: rec_rating = int(round(sum / (len(rows)*_avg_sim)))
    return rows, rec_rating

@login_required
def search(request):
    """Search items."""
    get = request.GET
    results = []
    if request.method == "GET" and 'q' in get:
        q = get.get('q').strip()
        if q:
            stype = get.get("stype", "artist")

            cls = Artist
            if stype == "author": cls = Author
            elif stype == "director": cls = Director
            elif stype == "film": cls = Film
            r = cls.objects.filter(name__icontains=q)

            # paginate results
            paginator = Paginator(r, 20)
            try: page = int(get.get("page", '1'))
            except ValueError: page = 1

            try: r = paginator.page(page)
            except: r = paginator.page(paginator.num_pages)

            return render_to_response("ratev/search.html", {"results": r, 'q': q,
                'stype': stype, "user": request.user})
    return render_to_response("ratev/search.html", {"user": request.user})
