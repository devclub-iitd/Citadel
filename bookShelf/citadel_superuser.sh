#!/bin/bash

emails=(
  devclub.iitd@gmail.com
)

usernames=(
  devclub
)

passwords=(
  devclub
)

for index in ${!usernames[*]}; do 
	echo "from django.contrib.auth import get_user_model; User = get_user_model(); print('User already exists') if User.objects.filter(username='${usernames[$index]}').exists() else User.objects.create_superuser('${usernames[$index]}', '${emails[$index]}', '${passwords[$index]}'); print('User created')" | python manage.py shell 
done

