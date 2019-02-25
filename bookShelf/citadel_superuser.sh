#!/bin/bash

emails=(
  devclub.iitd@gmail.com
)

usernames=(
  devclub
)

passwords=(
  $CITADEL_ADMIN_PASS
)

for index in ${!usernames[*]}; do 
	echo "from django.contrib.auth import get_user_model; User = get_user_model(); print('User already exists') if User.objects.filter(username='${usernames[$index]}').exists() else User.objects.create_superuser('${usernames[$index]}', '${emails[$index]}', '${passwords[$index]}');" | python manage.py shell 
done

