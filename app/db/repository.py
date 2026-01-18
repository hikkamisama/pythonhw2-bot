import datetime

async def create_users_table(con):
    await con.execute('''CREATE TABLE IF NOT EXISTS   users(
                                                userid INTEGER PRIMARY KEY,
                                                height INTEGER,
                                                weight INTEGER,
                                                age INTEGER,
                                                city TEXT,
                                                calorie_goal INTEGER,
                                                water_norm INTEGER,
                                                activity_goal INTEGER
                                                );
                                                '''
                )
    await con.commit()

async def create_history_table(con):
    await con.execute('''CREATE TABLE IF NOT EXISTS   history(
                                                userid TEXT,
                                                timestamp INTEGER,
                                                event_type TEXT NOT NULL CHECK(event_type IN ('water', 'food', 'activity_minutes', 'activity_calories')),
                                                event_int INTEGER
                                                );
                                                '''
                )
    await con.commit()

async def read_history(con):
    ans = await con.execute(f'''SELECT * FROM history''')
    res = await ans.fetchall()
    return res

async def read_users(con):
    ans = await con.execute(f'''SELECT * FROM users''')
    res = await ans.fetchall()
    return res

async def delete_user_history(con):
    await con.execute(f'''DELETE FROM users;''')
    await con.commit()

async def delete_query_history(con):
    await con.execute(f'''DELETE FROM history;''')
    await con.commit()

async def set_profile(con, userid, height, weight, age, city, calorie_goal, water_norm, activity_goal):
    await con.execute(
        """
        INSERT INTO users (
            userid, height, weight, age, city,
            calorie_goal, water_norm, activity_goal
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(userid) DO UPDATE SET
            height = excluded.height,
            weight = excluded.weight,
            age = excluded.age,
            city = excluded.city,
            calorie_goal = excluded.calorie_goal,
            water_norm = excluded.water_norm,
            activity_goal = excluded.activity_goal
        """,
        (
            userid,
            height,
            weight,
            age,
            city,
            calorie_goal,
            water_norm,
            activity_goal
        )
    )

async def get_profile(con, userid):
    query_ans = await con.execute(f'''
            SELECT * FROM users WHERE userid = ?
            ''',
            (userid,)
            )
    ans = await query_ans.fetchone()
    if ans is None:
        return None
    return {
        'userid': ans[0],
        'height': ans[1],
        'weight': ans[2],
        'age': ans[3],
        'city': ans[4],
        'calorie_goal': ans[5],
        'water_norm': ans[6],
        'activity_goal': ans[7]
    }

async def log_history(con, userid, request_timestamp, event_type, event_int):
    await con.execute(f'''
            INSERT INTO history (userid, timestamp, event_type, event_int)
            VALUES (?, ?, ?, ?)  
            ''', 
            (
                userid,
                request_timestamp,
                event_type,
                event_int
            )
        )
    await con.commit()

async def check_progress(con, userid):
    start = datetime.datetime.now(datetime.timezone.utc).date()
    end = start + datetime.timedelta(days=1)
    ans_current = await con.execute('''
        SELECT
            SUM(event_int) filter (WHERE event_type = 'water') as water_intake,
            SUM(event_int) filter (WHERE event_type = 'food') as food_intake,
            SUM(event_int) filter (WHERE event_type = 'activity_minutes') as activity_minutes,   
            SUM(event_int) filter (WHERE event_type = 'activity_calories') as activity_calories                                 
        FROM history
        WHERE userid = ? AND timestamp >= ? AND timestamp <= ?;''',
        (
            userid,
            start,
            end
        )
    )
    current = await ans_current.fetchone()

    ans_goals = await con.execute('''
        SELECT
            water_norm,
            calorie_goal,
            activity_goal                               
        FROM users
        WHERE userid = ?;''',
        (userid,)
    )
    goals = await ans_goals.fetchone()

    water, food, minutes, calories = (current or (None,)*4)
    water_norm, calorie_norm, activity_goal = (goals or (None,)*3)
    return {
        'water_intake': water or 0,
        'food_intake': food or 0,
        'activity_minutes': minutes or 0,
        'activity_calories': calories or 0,
        'water_norm': water_norm or 0,
        'calorie_goal': calorie_norm or 0,
        'activity_goal': activity_goal or 0
    }
