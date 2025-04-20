import pandas as pd
import numpy as np
import joblib
import datetime as dt

def _create_feaures(csv_file):
    # Оба файла должны иметь одинаковую структуру:
    main_csv_path: str = 'APP.csv'
    
    base_dataset = pd.read_csv(main_csv_path)
    new_data = pd.read_csv(csv_file)

    df = pd.concat([base_dataset, new_data])

    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    df["order_delivered_customer_date"] = pd.to_datetime(df["order_delivered_customer_date"])

    df['delivery_time'] = (df['order_delivered_customer_date'] - df['order_purchase_timestamp']).dt.days
    
    # Агрегация по клиенту с дополнительными признаками
    data = df.groupby("customer_unique_id").agg(
        mean_delivery_time=('delivery_time', 'mean'),
        n_categories=('product_category_name', 'nunique'),
        n_orders=('order_id', 'nunique'),
        avg_price=('price', 'mean'),
        avg_freight=('freight_value', 'mean'),
        avg_review=('review_score', 'mean'),
        most_common_category=('product_category_name', lambda x: x.mode()[0]),
        most_common_city=('customer_city', lambda x: x.mode()[0])
    )

    return data[data.index.isin(new_data['customer_unique_id'].unique())]


def churn_prediction(input):
    dataset: pd.DataFrame = _create_feaures(input)
    loaded_model = joblib.load('app_model.joblib')
    preds = loaded_model.predict(dataset)
    result_preds = pd.DataFrame(data = {'customer_unique_id': dataset.index,
                                        'predictions':preds})
    return result_preds