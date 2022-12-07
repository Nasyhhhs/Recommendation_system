import os
import pandas as pd
from typing import List
from catboost import CatBoostClassifier
from fastapi import FastAPI
from schema import PostGet
from datetime import datetime
from datetime import time
from sqlalchemy import create_engine
from loguru import logger
import psycopg2

app = FastAPI()


def batch_load_sql(query: str):
    engine = create_engine(
        "postgresql://robot-startml-ro:pheiph0hahj1Vaif@"
        "postgres.lab.karpov.courses:6432/startml"
    )
    conn = engine.connect().execution_options(
        stream_results=True)
    chunks = []
    for chunk_dataframe in pd.read_sql(query, conn, chunksize=200000):
        chunks.append(chunk_dataframe)
        logger.info(f"Got chunk: {len(chunk_dataframe)}")
    conn.close()
    return pd.concat(chunks, ignore_index=True)


def get_model_path(path: str) -> str:
    # Корректный путь для загрузки модели

    if os.environ.get("IS_LMS") == "1":
        MODEL_PATH = '/workdir/user_input/model'
    else:
        MODEL_PATH = path
    return MODEL_PATH


def load_features():
    # Уникальные записи post_id, user_id
    # Где был совершен лайк

    liked_posts_query = """
        SELECT distinct post_id, user_id
        FROM public.feed_data
        where action='like'"""

    liked_posts = batch_load_sql(liked_posts_query)
    # Фичи по постам на основе tf-idf

    posts_features = pd.read_sql(
        """SELECT * FROM public.nima_texts_features""",

        con="postgresql://robot-startml-ro:pheiph0hahj1Vaif@"
            "postgres.lab.karpov.courses:6432/startml"
    )

    # Фичи по юзерам

    user_features = pd.read_sql(
        """SELECT * FROM public.user_data""",

        con="postgresql://robot-startml-ro:pheiph0hahj1Vaif@"
            "postgres.lab.karpov.courses:6432/startml"
    )
    return [liked_posts, posts_features, user_features]


def age_group(age):
    if age < 18:
        age_group = "less_18"
    elif age >= 18 and age < 25:
        age_group = "18_to_25"
    elif age >= 25 and age < 45:
        age_group = "25_to_45"
    elif age >= 45 and age <= 65:
        age_group = "45_to_65"
    else:
        age_group = "others"
    return age_group


def load_models():
    ### Загрузка Catboost

    model_path = get_model_path("model")
    loaded_model = CatBoostClassifier()
    loaded_model.load_model(model_path)
    return loaded_model


model = load_models()

features = load_features()


def get_recommended_feed(id: int, time: datetime, limit: int):
    features[2]['age_group'] = features[2].age.apply(age_group)
    user_features = features[2].loc[features[2].user_id == id]
    user_features = user_features.drop(['user_id', 'age'], axis=1)

    # Загрузим фичи по постам

    posts = features[1][['post_id', 'text', 'topic']].set_index('post_id')

    posts_features = features[1].drop(['index', 'text'], axis=1)

    add_user_features = dict(zip(user_features.columns, user_features.values[0]))

    user_posts_features = posts_features.assign(**add_user_features)
    user_posts_features = user_posts_features.set_index('post_id')

    # Добафим информацию о дате рекомендаций

    user_posts_features['hour'] = time.hour
    user_posts_features['month'] = time.month
    user_posts_features['day_week'] = time.weekday()

    user_posts_features = user_posts_features[['topic', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11',
                                               '12', 'mean_target', 'gender', 'country', 'city',
                                               'exp_group', 'os', 'source', 'month', 'hour', 'day_week',
                                               'age_group']]

    predicts = model.predict_proba(user_posts_features)[:, 1]
    user_posts_features["predicts"] = predicts

    liked_posts = features[0][features[0].user_id == id].post_id.values
    filtered_ = user_posts_features[~user_posts_features.index.isin(liked_posts)]

    # Рекомендуем топ-5 по вероятности постов
    recommended_posts = filtered_.sort_values('predicts')[-limit:].index

    posts = posts.loc[recommended_posts].reset_index()

    return [PostGet(**{"id": i, "text": posts[posts.post_id == i].text.values[0],
                       "topic": posts[posts.post_id == i].topic.values[0]}) for i in recommended_posts]

    # [PostGet(**{"id": i[0], "text": i[1], "topic": i[2]}) for i in posts.itertuples(index=False)]


@app.get("/post/recommendations/", response_model=List[PostGet])
def recommended_posts(id: int, time: datetime, limit: int = 10) -> List[PostGet]:
    return get_recommended_feed(id, time, limit)