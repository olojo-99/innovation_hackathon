import pandas as pd
df = pd.read_csv("/Users/benolojo/Projects/BofA/innovation_summit_hackathon/Fraud Detection Transactions Dataset/hackathon_fraud_payment.csv")
# count rows that are part of any duplicated Transaction_ID (counts all occurrences)
print(df['Transaction_ID'].duplicated(keep=False).sum())