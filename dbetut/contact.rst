Contact form
============


.. raw:: html

    <form action="/mailform/mailform/" method="POST">
    From: <input type="text" name="from" size="40" /> <br />

    Subject: <select name="type">
        <option> </option>
        <option>DBE question</option>
        <option>Larks Guide question</option>
        <option>Django / Python consulting inquiry</option>
    </select> <br />

    <textarea name="body" rows="20" cols="79" ></textarea> <br />
    <input type="submit" value="Send" />
    </form>
