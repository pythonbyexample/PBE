
Django Tutorial: a Todo List App Part II
----------------------------------------

In part II we'll look at enhancing our App's functionality with AJAX using jQuery library. Most of
the code we'll deal with is not specific to Django. My intent is to give a few examples of using
asynchronous communication with the Django server to make the interface a little more appealing.

If you are not familiar with Javascript, the following code may appear complicated and
intimidating; if you don't need AJAX functionality, feel free to skip this part completely and go
on to other tutorials --- nothing here will be essential to this App's operation.

Interactive Toggle Boxes
========================

Let's make our OnHold and Done links a little spiffier: in this iteration, they will update the
task status behind the scenes without page reload. Add the following Javascript code to the extrahead
block of `change_list.html` template:

.. sourcecode:: html

    <script type="text/javascript" src="http://code.jquery.com/jquery-1.4.2.min.js"></script>
    <script type="text/javascript" src="/media/js/todo.js"></script>
    <script type="text/javascript" charset="utf-8">
        var progress_array = {};
        {% for obj in cl.result_list %}
            progress_array[{{ obj.pk }}] = {{ obj.progress }};
        {% endfor %}
    </script>


The main javascript code should go into `media/js/todo.js`:

.. sourcecode:: javascript

    $(document).ready( function() {

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            function getCookie(name) {
                var cookieValue = null;
                if (document.cookie && document.cookie != '') {
                    var cookies = document.cookie.split(';');
                    for (var i = 0; i < cookies.length; i++) {
                        var cookie = jQuery.trim(cookies[i]);
                        // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
            }
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                // Only send the token to relative URLs i.e. locally.
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });


    // OnHold / Done toggle
    $(".toggle").click(function() {

        $action = $(this).html().indexOf("icon-on") != -1 ? "off" : "on";
        $id = $(this).attr("id");
        $pk = $id.substring(2) + '/';
        $atype = $(this).hasClass("done") ? "done/" : "onhold/";

        $.ajax({
            type: "POST",
            url: "/todo/update_item/" + $pk + $atype + $action + '/',
            success: function(action) {
                $('#' + $id).html("<img class='btn' src='/media/img/admin/icon-"
                    +$action+".gif' />");
            }
        })
    });



    });

I won't go into what happens here --- jQuery deserves a dedicated tutorial, and I don't know it
enough to explain properly; --- if you are interested you should read
`their excellent documentation site <http://docs.jquery.com/Main_Page>`_.


From the point of view of Django the only thing we do here is a `POST` request to
`/todo/update_item/done/on/` (or off). Add the following code to your `urlconf` file and
`views.py`:

This function will handle both `onhold` and `done` toggles. Let's change `toggle_done()` in
`models.py` (you should also update `list_display` in the same file):

.. sourcecode:: python

    btn_tpl = "<div class='%s' id='%s_%s'><img class='btn' src='%simg/admin/icon-%s.gif' /></div>"

    def done_(self):
        onoff = "on" if self.done else "off"
        return self.btn_tpl % ("toggle done", 'd', self.pk, MEDIA_URL, onoff)
    done_.allow_tags = True
    done_.admin_order_field = "done"

Notice that we use `admin_order_field` to tell Django to sort the display column by `done` column
in the database. The icons I'm using are not included in Django --- you'll have to make them
yourself or find free ones from the Web. The interface looks a lot less cluttered now, doesn't it?

.. image:: _static/tl4.png

The code for `OnHold` toggle is exactly the same.

Now let's do something a little tougher: an interactive progress bar that will update the database
when you click on it.

Interactive Progress Bar
========================

We have to go back to `todo.js` and add the following javascript code (in the same `for` loop we
used before):

.. sourcecode:: javascript

    // hover
    $(".progress_btns li").hover(function() {
        var progress = $(this).text();
        $(this).parents(".progress_cont").children(".progress_on").css("width", barWidth(progress));
    });

    // mouseout
    $(".progress_btns li").mouseout(function() {
        var pk = $(this).parents(".progress_btns").attr("id");
        $(this).parents(".progress_cont").children(".progress_on").css("width",
            barWidth(progress_array[pk]));
    });

    // click
    $(".progress_btns li").click(function() {
        $progress = $(this).text();
        $(this).parents(".progress_cont").children(".progress_on").css("width", barWidth($progress));
        $pk = $(this).parents(".progress_btns").attr("id");
        progress_array[$pk] = $progress;
        $.ajax({
            type: "POST",
            url: "/todo/update_item/" + $pk + "/progress/" + $progress + '/',
        })
    });

    // init progress bars
    for (var pk in progress_array) {
        $("#progress_on_"+pk).css("width", barWidth(progress_array[pk]));
    }


Add the `barWidth()` function:

.. sourcecode:: javascript

    function barWidth(progress) {
        progress = parseFloat(progress);
        var width = '';
        switch (progress) {
            case 0   : width = "0px"; break;
            case 10  : width = "14px"; break;
            case 20  : width = "28px"; break;
            case 30  : width = "42px"; break;
            case 40  : width = "56px"; break;
            case 50  : width = "70px"; break;
            case 60  : width = "84px"; break;
            case 70  : width = "98px"; break;
            case 80  : width = "112px"; break;
            case 90  : width = "126px"; break;
            case 100 : width = "140px"; break;
            default  : width =  "0px";
        }
        return width;
    }


Finally, add some styling in extrastyle block in `change_list.html`, or if you prefer to have
them in a separate css file, that's a bit cleaner.

.. sourcecode:: css

    <style type="text/css">
        .btn { cursor: pointer; }
        .progress_cont { background: #ccc; border: 1px solid #ccc; width: 140px;
             height: 10px; text-align: left; margin-left: 2px; margin-top: 0px; }

        .progress_on { background: #333; width: 0px; height: 10px; position: relative;
             z-index: 50; top: -10px; }

        .progress { font-size: 11px; font-family: Arial, Helvetica, sans-serif;
             color: #333; padding-left: 3px; width: 22px; float: left; margin-top: -2px; }

        .progress_btns { position: relative; z-index: 100; width: 140px; height: 10px;}
        .progress_btns ul, #progress_btns li  { padding: 0; margin: 0; }
        .progress_btns li { float: left; width: 13px; height: 10px; display: block;
             font-size: 1px; cursor: pointer; color: #1E1D1C;
        }
    </style>


Switch to `models.py` and add the following function to display the bar:

.. sourcecode:: python

    from django.template import loader

    def progress_(self):
        return loader.render_to_string("progress.html", dict(pk=self.pk))
    progress_.allow_tags = True
    progress_.admin_order_field = "progress"


We'll need to add `progress.html` template to `templates/todo/` with `LI` tags that capture user's
clicks and `progress_on` div that visually shows how much of the task is complete:

.. sourcecode:: html

    <div id="progress_cont_{{ pk }}" class="progress_cont">
        <div id="{{ pk }}" class="progress_btns">
            <ul>
                <li>0</li>
                <li>10</li>
                <li>20</li>
                <li>30</li>
                <li>40</li>
                <li>50</li>
                <li>60</li>
                <li>70</li>
                <li>80</li>
                <li>90</li>
                <li>100</li>
            </ul>
        </div>
        <div id="progress_on_{{ pk }}" class="progress_on">&nbsp;</div>
    </div>

Now we can click on the bar to set progress:

.. image:: _static/tl5.png

I have used `eligeske's star comment code
<http://eligeske.com/jquery/jquery-star-comment-rating/>`_ as inspiration for the progress bar
widget.

If something's not working for you, here are the full sources you can check against:
`todosrc.tar.gz <todosrc.tar.gz>`_.
