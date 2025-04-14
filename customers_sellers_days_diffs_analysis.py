import pandas as pd

customers_df = pd.read_csv('SOURCE\\customers.csv', low_memory=False)
orders_df = pd.read_csv('SOURCE\\orders.csv', low_memory=False)
orders_items_df = pd.read_csv('SOURCE\\orders_items.csv', low_memory=False)
sellers_df = pd.read_csv('SOURCE\\sellers.csv', low_memory=False)

delivered_orders = orders_df[orders_df['order_status'] == 'delivered']

merged_df = (
    delivered_orders
    .merge(orders_items_df, on='order_id', how='inner')
    .merge(customers_df[['customer_id', 'customer_unique_id']], on='customer_id', how='inner')
    .merge(sellers_df[['seller_id']], on='seller_id', how='inner')
)

merged_df = merged_df[['seller_id', 'customer_unique_id', 'order_purchase_timestamp']]
merged_df['order_purchase_timestamp'] = pd.to_datetime(merged_df['order_purchase_timestamp'])
merged_df['order_purchase_timestamp'] = merged_df['order_purchase_timestamp'].dt.date
merged_df = merged_df.sort_values(by=['seller_id', 'customer_unique_id', 'order_purchase_timestamp'])
merged_df = merged_df.drop_duplicates()

merged_df['days_between_purchases'] = (
       merged_df.groupby(['seller_id', 'customer_unique_id'])['order_purchase_timestamp']
       .diff()
       .apply(lambda x: x.days if pd.notnull(x) else None)
   )

merged_df['orders_num'] = (
    merged_df.groupby(['seller_id', 'customer_unique_id'])['order_purchase_timestamp']
    .transform('count')
)

analysis_df = merged_df.rename(columns={'order_purchase_timestamp': 'delivered_purchase_date'})
analysis_df['days_between_purchases'] = analysis_df['days_between_purchases'].fillna(0)

analysis_df.reset_index(drop=True, inplace=True)
analysis_df.to_csv('customers_sellers_days_diffs.csv', sep=',', index=False)