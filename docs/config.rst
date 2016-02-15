.. _config:

Configuration
=============

There are a number of options to configure how Wazimap behaves. Options are
always set in ``settings.py`` in the ``WAZIMAP`` dict.

``name``
  The full name of the website. Default: ``Wazimap Example``

``url``
  The site's base url, including scheme, WITHOUT and ending slash.
  Default: ``http://wazimap.example``

``twitter``
  Twitter handle. Default: ``@Wazimap``

``ga_tracking_id``
  Google Analytics tracking id.

``cache_secs``
  How many seconds should cacheable Wazimap pages be cached for? Default: ``60 * 60``

``embed_cache_secs``:
  How many seconds should Wazimap embed pages be cached for? Default: ``24 * 60 * 60``

``geodata``
  The dotted-path of the class to use for geo data helper routines.
  Default: ``wazimap.geo.GeoData``

``levels``
  Geography levels. This must be a dict similar to the following: ::
   
      {
        'country': {
          'name': 'country',      # optional, defaults to the level code
          'plural': 'countries',  # plural version of the name
          'children': ['province'],
        },
        ...
      }

  Default: ::

       'country': {
           'plural': 'countries',
           'children': [],
       }

``comparative_levels``
  Ordered list of levels to compare a place with; should generally be only 2-3 levels.
  Default: ``[]``

``geometry_data``
  Map from geometry names to local static files with geometry data. This is used
  to both draw maps in webpages and for geolocation.
  Wazimap uses Django's static files finder to find these files, so the
  files must be stored in your application's `static` directory.
  
  For maps, topojson is preferred because it's smaller. But for geolocation,
  because it's done server side, it requires geojson (shapely doesn't understand
  topojson). Ideally you should have both `.geojson` and `.topojson` files
  and specify the `.topojson` version here. Wazimap will look for geojson equivalents
  of topojson files.
 
  If a level isn't specified here, Wazimap will try to find a file under the key ``''``.

  Default: ::

      {
        '': 'geo/all.geojson',
      }

``embed_url``
  The full url, including scheme (but no ending slash) where embeds are hosted.
  This is generally not sude. The default is the same as ``url``.