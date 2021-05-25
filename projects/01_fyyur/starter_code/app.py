# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
  Flask,
  render_template,
  request,
  Response,
  flash,
  redirect,
  url_for,
  jsonify)
from flask_moment import Moment
# from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#  added
from flask_migrate import Migrate
import sys  # added
from models import db, Show, Venue, Artist  # added
from config import DatabaseURI
# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
# app.config.from_object('config')
app.config.from_object('config.DatabaseURI')
app.config['SECRET_KEY'] = 'any secret string'
db.init_app(app)  # added

migrate = Migrate(app, db)

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value

    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')

# Venues
# ----------------------------------------------------------------


@app.route('/venues')
def venues():
    # get all the venues
    data = Venue.query.all()
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search = request.form.get('search_term', '')
    # query to get all the venues that match your search
    query = Venue.query.filter(Venue.name.ilike('%'+search+'%'))
    count = query.count()
    venues = query.all()

    data = []
    for venue in venues:
        data.append({
            "id": venue.id,
            "name": venue.name
        })

    response = {
      "count": count,
      "data": data
    }

    return render_template(
      'pages/search_venues.html',
      results=response,
      search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    venue = Venue.query.get(venue_id)  # get the data with the given venue_id
    # query to get data of past shows the given venue_id
    query_past_shows = db.session.query(Show, Artist)\
        .join(Artist, Artist.id == Show.artist_id)\
        .filter(Show.venue_id == venue.id)\
        .filter(Show.start_time < datetime.today())

    # query to get data of upcoming shows the given venue_id
    query_upcoming_shows = db.session.query(Show, Artist)\
        .join(Artist, Artist.id == Show.artist_id)\
        .filter(Show.venue_id == venue.id)\
        .filter(Show.start_time > datetime.today())

    past_shows = query_past_shows.all()
    upcoming_shows = query_upcoming_shows.all()

    # count the past shows
    past_shows_count = query_past_shows.count()
    # count the past upcoming shows
    upcoming_shows_count = query_upcoming_shows.count()

    return render_template(
      'pages/show_venue.html',
      venue=venue,
      past_shows=past_shows,
      upcoming_shows=upcoming_shows,
      past_shows_count=past_shows_count,
      upcoming_shows_count=upcoming_shows_count)


#  Create Venue
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    try:
        venue = Venue()
        # Associates the form data with the Venue object to create
        form = VenueForm(request.form, obj=venue)
        # pass the form data to object Venue to create
        form.populate_obj(venue)
        db.session.add(venue)
        db.session.commit()

        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except():
        flash('An error occurred. Venue ' + request.form['name']
              + ' could not be listed.')
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error = False
    try:
        # get the object with the given venue_id
        venue = Venue.query.get(venue_id)
        # delete the record with the given venue_id
        db.session.delete(venue)
        db.session.commit()
        flash('Venue was successfully deleted!')
    except():
        db.session.rollback()
        error = True
    finally:
        db.session.close()

    if error:
        abort(500)
    else:
        return jsonify({'Url': 'index'})


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # Fetches all records from model Artist
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search = request.form.get('search_term', '')
    # query to get all the artists that match your search
    query = Artist.query.filter(Artist.name.ilike('%'+search+'%'))
    count = query.count()
    artists = query.all()

    data = []
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })

    response = {
        "count": count,
        "data": data
    }

    return render_template(
      'pages/search_artists.html',
      results=response,
      search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # get the data with the given artist_id
    datab = Artist.query.get(artist_id)

    # query to get data of past shows the given artist_id
    query_past_shows = db.session.query(Show, Venue)\
        .join(Venue, Venue.id == Show.venue_id)\
        .filter(Show.artist_id == artist_id)\
        .filter(Show.start_time < datetime.today())

    # query to get data of upcoming shows the given artist_id
    query_upcoming_shows = db.session.query(Show, Venue)\
        .join(Venue, Venue.id == Show.venue_id)\
        .filter(Show.artist_id == artist_id)\
        .filter(Show.start_time > datetime.today())

    past_shows = query_past_shows.all()
    upcoming_shows = query_upcoming_shows.all()

    # count the past shows
    past_shows_count = query_past_shows.count()
    # count the past upcoming shows
    upcoming_shows_count = query_upcoming_shows.count()

    return render_template(
      'pages/show_artist.html',
      artist=datab,
      past_shows=past_shows,
      upcoming_shows=upcoming_shows,
      past_shows_count=past_shows_count,
      upcoming_shows_count=upcoming_shows_count)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # get the data from the given artist_id
    artist = Artist.query.get(artist_id)
    # populate form with artist object properties
    form = ArtistForm(obj=artist)
    form.genres.data = artist.genres
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # get the object with the artist_id to update
    artist_upd = Artist.query.get(artist_id)
    # Associates the values from the form submitted with
    # the object artist_id to update.
    form = ArtistForm(request.form, obj=artist_upd)

    try:
        # pass the values from the form submitted to object artist_id to update
        form.populate_obj(artist_upd)
        db.session.add(artist_upd)
        db.session.commit()
    except():
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # get the object from the given venue_id
    venue = Venue.query.get(venue_id)
    # populate form with venue object properties
    form = VenueForm(obj=venue)
    form.genres.data = venue.genres
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # get the object with the venue_id to update
    venue_upd = Venue.query.get(venue_id)
    # Associates the values from the form submitted with
    # the object venue_id to update.
    form = VenueForm(request.form, obj=venue_upd)

    try:
        # pass the values from the form submitted to object venue_id to update
        form.populate_obj(venue_upd)
        db.session.add(venue_upd)
        db.session.commit()
    except():
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    try:
        artist = Artist()
        # Associates the form data with the object the new Artist to create
        form = ArtistForm(request.form, obj=artist)
        # populate the form data to object Artist to create
        form.populate_obj(artist)
        db.session.add(artist)
        db.session.commit()

        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')

    except():
        flash('An error occurred. Artist ' + request.form['name']
              + ' could not be listed.')
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # Fetches all records from model Show
    shows = Show.query.all()

    data = []
    for show in shows:
        # Fetches the record from venue associated to show
        venue = Venue.query.get(show.venue_id)
        # Fetches the record from artist associated to show
        artist = Artist.query.get(show.artist_id)

        data.append({
          "venue_id": show.venue_id,
          "venue_name": venue.name,
          "artist_id": show.artist_id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": show.start_time
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting
    # new show listing form
    try:
        show = Show()
        # Associates the form data with the Show object to create
        form = ShowForm(request.form, obj=show)
        # populate the form data to object Show to create
        form.populate_obj(show)
        db.session.add(show)
        db.session.commit()

        # on successful db insert, flash success
        flash('Show was successfully listed!')

    except():
        flash('An error occurred. Show could not be listed.')
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<int:venue_id>/create_show', methods=['GET'])
def create_shows_venue_form(venue_id):
    form = ShowForm()
    # Fetches the record with given venue_id
    venue = Venue.query.get(venue_id)
    return render_template('forms/new_show_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/create_show', methods=['POST'])
def create_shows_venue_submission(venue_id):
    try:
        # get data from the form
        artist_id = request.form.get('artist_id', '')
        start_time = request.form.get('start_time', '')

        # Associate the data with the new show object to create
        show = Show(artist_id=artist_id,
                    venue_id=venue_id, start_time=start_time)
        db.session.add(show)
        db.session.commit()

        # on successful db insert, flash success
        flash('Show was successfully listed!')

    except():
        flash('An error occurred. Show could not be listed.')
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))


@app.route('/venue/artists/<search_value>/search', methods=['POST'])
def search_venue_artists(search_value):
    # query to get all the artists that match your search
    query = Artist.query.filter(Artist.name.ilike('%'+search_value+'%'))
    count = query.count()
    artists = query.all()

    data = []
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })

    response = {
      "count": count,
      "data": data
    }

    return jsonify(response)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


@app.errorhandler(400)
def server_error(error):
    return render_template('errors/400.html'), 400


@app.errorhandler(405)
def server_error(error):
    return render_template('errors/405.html'), 405


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
          '%(asctime)s %(levelname)s: %(message)s \
          [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
