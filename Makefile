serve:
	PYTHONPATH=./app DJANGO_SETTINGS_MODULE=web.settings django-admin runserver 0.0.0.0:8000

clean_slate:
	# This is useful for local development and will blow everything away.
	rm app/db.sqlite3 ; rm app/mast_toolkit/migrations/* -rf ; python app/manage.py makemigrations mast_toolkit; python app/manage.py migrate ; python dev/make_data.py