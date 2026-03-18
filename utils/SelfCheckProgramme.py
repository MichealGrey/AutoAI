import pandas as pd

import os
 
def find_by_prefix(directory, prefix):
    
    matches = []
    for root, dirs, files in os.walk(directory):
        for name in files:
            if name.startswith(prefix):
                matches.append(name[:14])

    return matches
directory_path = r'D:\\OutBound\\HistroyFiles\\PDF\\202504'  
prefix = '20250409'  # 替换为你想要查找的前缀
result = find_by_prefix(directory_path, prefix)
data = {'OutBoundList':result}

print(result)

filterTimeStart,filterTimeEnd = '2025-04-09 00:00:00','2025-04-10 00:00:00'

df = pd.read_excel('D:\\OutBound\\OutBoundList\\CheckFiles\\出入库明细表20250421172229.xlsx')
stockdf = pd.read_excel(r'D:\\OutBound\\UserFiles\\库位设置表.xlsx')
print(df)
mask = (df['日期'] > filterTimeStart) & (df['日期'] <= filterTimeEnd)
filtered_df = df.loc[mask]
print(filtered_df)
selected_columns = ['图号', '工程', '累进', '货架','数量','仓库','日期']
print(filtered_df[selected_columns])
    
OutBoundres = pd.merge(filtered_df[selected_columns],stockdf,on = '仓库',how='inner')

OutBoundres['timestamp'] = pd.to_datetime(OutBoundres['日期']).dt.strftime('%Y%m%d%H%M%S')
print(OutBoundres)
Leaveres = OutBoundres[~OutBoundres['timestamp'].isin(result)]
Leaveres.to_excel('D:\\OutBound\\OutBoundList\\CheckFiles\\Errorlist.xlsx',index=False)
