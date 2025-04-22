import pandas as pd

orders_items_df = pd.read_csv('DATA\\orders_items.csv', low_memory=False)
orders_df = pd.read_csv('DATA\\orders.csv', low_memory=False)

product_median_freight_df = orders_items_df.groupby('product_id')['freight_value'].median().reset_index()
product_median_freight_df.rename(columns={'freight_value': 'product_median_freight_value'}, inplace=True)

orders_items_df = orders_items_df[['order_id', 'product_id', 'freight_value']].merge(product_median_freight_df, on='product_id', how='inner').reset_index(drop=True)

orders_items_df = orders_items_df.merge(orders_df[['order_id', 'customer_id']], on='order_id', how='inner').reset_index(drop=True)

customer_product_median_freight_df = orders_items_df.groupby(['customer_id', 'product_id'])['freight_value'].median().reset_index()
customer_product_median_freight_df.rename(columns={'freight_value': 'customer_product_median_freight_value'}, inplace=True)

orders_items_df = orders_items_df[['customer_id', 'product_id', 'product_median_freight_value']].merge(customer_product_median_freight_df, on=['customer_id', 'product_id'], how='inner').reset_index(drop=True)

orders_items_df['customer_product_freight_score'] = orders_items_df['customer_product_median_freight_value'] / orders_items_df['product_median_freight_value']

analysis_df = orders_items_df.groupby('customer_id')['customer_product_freight_score'].mean().reset_index()
analysis_df.rename(columns={'customer_product_freight_score': 'customer_freight_score'}, inplace=True)
analysis_df = analysis_df.fillna(0)
analysis_df.to_csv('customers_freight_score.csv', sep=',', index=False)