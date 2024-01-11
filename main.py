from recsys import Recsys
import platform
import os
import csv

clr = 'clear'
if platform.system() == 'Windows':
    import msvcrt as getch
    clr = 'cls'
else:
    import getch

CSV = './csv'
USERS = os.path.join(CSV, 'users.csv')
RATINGS = os.path.join(CSV, 'tastes_modified.csv')
ITEMS = os.path.join(CSV, 'items_modified.csv')

recsys = Recsys(ITEMS, RATINGS)

def join():
    uids = []
    if os.path.exists(USERS):
        with open(USERS, mode='r', newline='', encoding='utf-8-sig') as users:
            reader = csv.reader(users, delimiter=',')
            for row in reader:
                uids.append(row[0])

    while True:
        os.system(clr)
        print('회원가입')
        id = input('유저 이름을 입력하세요: ')
        if len(id) == 0:
            return None
        if id not in uids:
            with open(USERS, mode='a', newline='', encoding='utf-8-sig') as users:
                writer = csv.writer(users, delimiter=',')
                writer.writerow([id])
            return id

def login():
    uids = []
    if os.path.exists(USERS):
        with open(USERS, mode='r', newline='', encoding='utf-8-sig') as users:
            reader = csv.reader(users, delimiter=',')
            for row in reader:
                uids.append(row[0])
    while True:
        os.system(clr)
        id = input('유저 이름을 입력해주세요: ')
        if len(id) == 0:
            return None
        if id in uids:
            return id
    
def get_key():
    char = getch.getch()

    if platform.system() == 'Windows':
        char = char.decode('utf-8')

    return char

def start_recsys(uid):
    if recsys.is_first_user(uid):
        avoid_cold_start(uid)
    os.system(clr)
    print('training..')
    recsys.save_ratings()
    recsys.train()
    page = 0
    while True:
        os.system(clr)
        recom_list = recsys.recomm_by_surprise(uid, page)
        for i, recom in enumerate(recom_list):
            print(f'{page * 10 + i}: {recom[1]}')
        print('a: 이전 페이지, d: 다음 페이지, s: 아이템 평가, q: 나가기')
        k = get_key()
        if k == 'a':
            if page > 0:
                page -= 1
        elif k == 'd':
            if len(recsys.item_no_exp(uid)) - 1 >= (page + 1) * 10:
                page += 1
        elif k == 's':
            while True:
                line = input('아이템 번호, 점수 입력: ')
                if len(line) == 0:
                    recsys.save_ratings()
                    break
                data = line.split(', ')
                new_data = {
                    'uid' : [str(uid)],
                    'iid' : [str(recom_list[int(data[0])][0])],
                    'rating' : [float(data[1])],
                    'predicted': [float(recom_list[int(data[0])][2])]
                }
                recsys.append(new_data)
        elif k == 'q':
            break

def avoid_cold_start(uid):
    os.system(clr)
    most_viewed = recsys.most_reviewed()
    for i, items in enumerate(most_viewed):
        print(f'{i}: {items[1]}')
    while True:
        line = input('아이템 번호, 점수 입력: ')
        if len(line) == 0:
            break
        data = line.split(', ')
        new_data = {
            'uid' : [str(uid)],
            'iid' : [str(most_viewed[int(data[0])][0])],
            'rating' : [float(data[1])],
            'predicted': [0]
        }
        recsys.append(new_data)

def cross_validate():
    os.system(clr)
    recsys.cross_validate()
    print('아무 키나 눌러 계속하세요')
    get_key()

def main():
    while True:
        os.system(clr)
        print('1. 회원가입')
        print('2. 로그인')
        print('3. cross_validate')
        print('q. 나가기')
        print('메뉴를 선택하세요')
        k = get_key()
        if k == '1':
            uid = join()
            if uid is not None:
                start_recsys(uid)
        elif k == '2':
            uid = login()
            if uid is not None:
                start_recsys(uid)
        elif k == '3':
            cross_validate()
        elif k == 'q':
            break

if __name__ == "__main__":
    main()