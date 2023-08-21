post-install-process:
	python manage.py loaddata event_type_codes.json
	python manage.py add_apps

makemigrations:
	python manage.py makemigrations authapp
	python manage.py makemigrations docx_generator
	python manage.py makemigrations mainapp
	python manage.py makemigrations metricsapp
	python manage.py makemigrations registry_br
	python manage.py makemigrations registry_id
	python manage.py makemigrations registry_lrp
	python manage.py makemigrations registry_lrp_dop
	python manage.py makemigrations registry_rtn_ts
	python manage.py makemigrations registry_zp
	python manage.py makemigrations searchapp
	python manage.py makemigrations statisticapp
	python manage.py makemigrations registry_state_support

migrate: makemigrations
	python manage.py migrate

runserver:
	python manage.py runserver

collectstatic:
	python manage.py collectstatic

createsuperuser:
	python manage.py createsuperuser --no-input

del-migrations-win:
	del /S /Q authapp\migrations\*.py
	type nul > authapp\migrations\__init__.py
	del /S /Q mainapp\migrations\*.py
	type nul > mainapp\migrations\__init__.py
	del /S /Q api\migrations\*.py
	type nul > api\migrations\__init__.py
	del /S /Q docx_generator\migrations\*.py
	type nul > docx_generator\migrations\__init__.py
	del /S /Q metricsapp\migrations\*.py
	type nul > metricsapp\migrations\__init__.py
	del /S /Q registry_br\migrations\*.py
	type nul > registry_br\migrations\__init__.py
	del /S /Q registry_id\migrations\*.py
	type nul > registry_id\migrations\__init__.py
	del /S /Q registry_lrp\migrations\*.py
	type nul > registry_lrp\migrations\__init__.py
	del /S /Q registry_lrp_dop\migrations\*.py
	type nul > registry_lrp_dop\migrations\__init__.py
	del /S /Q registry_rtn_ts\migrations\*.py
	type nul > registry_rtn_ts\migrations\__init__.py
	del /S /Q registry_zp\migrations\*.py
	type nul > registry_zp\migrations\__init__.py
	del /S /Q searchapp\migrations\*.py
	type nul > searchapp\migrations\__init__.py
	del /S /Q statisticapp\migrations\*.py
	type nul > statisticapp\migrations\__init__.py

check-code:
	isort api/ app/ authapp/ mainapp/ statisticapp/
	flake8 --extend-ignore E501,F401 api/ app/ authapp/ mainapp/ statisticapp/