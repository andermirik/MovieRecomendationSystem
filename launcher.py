import csv
import statistics

USERS = ['762131', '256987', '566784']
COEFF_GANRES = 1.0
COEFF_TYPE = 0.5
COEFF_DURATION = 0.1

users_file = open("USER_UID.txt", "r")
content = users_file.read().replace("\n","").replace(" ", "")
USERS = content.split(",")
users_file.close()
print(USERS)
raw_content = {}
with open('content.csv', newline='', encoding='utf-8') as csvfile:
     reader = csv.DictReader(csvfile)
     for row in reader:
         raw_content[row['content_uid']] = row


raw_users = {}
with open('watch_history.csv', newline='', encoding='utf-8') as csvfile:
     reader = csv.DictReader(csvfile)
     for row in reader:
         if row['user_uid'] in USERS:
             if row['user_uid'] not in raw_users:
                 raw_users[row['user_uid']] = []
             raw_users[row['user_uid']].append(row)

mini_content = {}
for k, v in raw_content.items():
    if v['type'] != 'episode':
        mini_content[k] = v


def corr(i, j):
    first = set(raw_content[i]['genres'].lower().split(','))
    second = set(raw_content[j]['genres'].lower().split(','))
    common = first & second
    _1 = len(common) * COEFF_GANRES
    _2 = COEFF_TYPE if raw_content[i]['type'] == raw_content[j]['type'] else 0
    _3 = 0
    if raw_content[i]['duration_seconds'] and raw_content[j]['duration_seconds']:
        first_duration = float(raw_content[i]['duration_seconds'])
        second_duration = float(raw_content[j]['duration_seconds'])
        if first_duration > 0 and second_duration > 0:
            _3 = COEFF_DURATION * min(first_duration, second_duration) / max(first_duration, second_duration)

    return _1 + _2 + _3


matrix = {}
all_films = sorted(list(mini_content.keys()))
for i in range(len(all_films)):
    first_film_id = all_films[i]
    for j in range(i + 1, len(all_films)):
        second_film_id = all_films[j]
        matrix[(first_film_id, second_film_id)] = matrix[(second_film_id, first_film_id)] = corr(first_film_id, second_film_id)

with open('recommendations.csv', 'w', newline='') as csvfile:
    fieldnames = ['user_id', 'recommendations']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for user in USERS:
        print(f'start user {user}')
        mini_watch = {}
        for watched in raw_users[user]:
            film = watched['content_uid']
            if raw_content[film]['type'] == 'episode':
                film = raw_content[film]['serial_id']

            if film not in raw_content:
                continue

            if film in mini_watch:
                mini_watch[film]['durations'].append(int(watched['second']) / int(raw_content[watched['content_uid']]['duration_seconds']))
            else:
                mini_watch[film] = raw_content[film]
                mini_watch[film]['durations'] = [int(watched['second']) / int(raw_content[watched['content_uid']]['duration_seconds'])]

        all_watched = set(mini_watch.keys())
        all_not_watched = set(mini_content.keys()) - all_watched

        recommends = {}
        for not_watched in all_not_watched:
            recommends[not_watched] = 0
            for watched in all_watched:
                recommends[not_watched] += matrix[(not_watched, watched)] * statistics.mean(mini_watch[watched]['durations'])

        recommends = dict(sorted(recommends.items(), reverse=True, key = lambda x:x[1]))
        print(user)
        first_keys = list(recommends.keys())[:50]
        print()
        print(first_keys)
        print()
        for k in first_keys:
            print(k, recommends[k], mini_content[k])


        writer.writerow({'user_id': user, 'recommendations': ','.join(first_keys)})
