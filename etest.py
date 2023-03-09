import cx_Oracle
import pandas as pd
import datetime as dt
from prettytable import PrettyTable
from db_credentials import user, password, password2
dsn_tns = cx_Oracle.makedsn('idxt.itradenetwork.com', '1521', service_name='idxt') 
conn = cx_Oracle.connect(user=user, password=password2, dsn=dsn_tns) 
query1 = """select t.package_id,t.data_feed_name,t.supplier_id as DISTRIBUTOR_EDI_ID,max(t.ts),to_char(min(t.invoice_date),'MM/DD/YYYY') as Start1,to_char(max(t.invoice_date),'MM/DD/YYYY') as End1,count(*),sum(count(invoice_id)) over (order by package_id rows between unbounded preceding and current row) as total_rows,t.transaction_currency
    from icust_owner.t_compass_canada_invoice_flat t
        where t.package_id > (
            select max(e.last_package_id)
                from icust_owner.T_EXTRACT_PROCESS_STATS e
                    where e.process_name like 'COMPASS%'
                    and e.state_code = 'END')
    group by package_id, data_feed_name, t.supplier_id ,t.transaction_currency
    order by t.package_id
"""

query2 = """select cu.package_id,cu.data_feed_name,cu.distributor_edi_id,cu.vendor_remit_to_dc_id,cu.vendor_ship_from_dc_id,to_char(min(cu.invoice_date),'MM/DD/YYYY') as min_date,to_char(max(cu.invoice_date),'MM/DD/YYYY') as max_date,count(invoice_id) as Lines,sum(count(invoice_id)) over ( order by package_id rows between unbounded preceding and current row) as total_rows,cu.transaction_currency as curr,max(ts)
    from icust_owner.t_compass_invoice_flat cu
    where cu.package_id > (
        select max(ce.last_package_id)      
            from icust_owner.t_Compass_Process ce
                where ce.state_code = 'END')
    group by package_id, data_feed_name, cu.distributor_edi_id, cu.vendor_remit_to_dc_id, cu.vendor_ship_from_dc_id, cu.transaction_currency
    order by cu.package_id
    """

def Check_packages(query):
    cur=conn.cursor()
    cur.execute(query)
    rows=cur.fetchall()
    
    column_names = [desc[0] for desc in cur.description]
    x=PrettyTable(column_names)
    for row in rows:
        x.add_row(row)
    print(x)
    cur.close()
    

def deletion_compass_USA(abc):
    cur=conn.cursor()
    cur.execute(abc)
    cur.close()

    
    
while True:
    user_input = input("press 'q' to exit\nPress 1 to check IDXT COMPASS CANADA and USA packages")
    if user_input.lower()=="q":
        break
    elif user_input =="1":
        print("\n----------COMPASS CANADA ONLY------------")
        Check_packages(query1)
        print("\n----------COMPASS USA_BATCH ONLY------------")
        Check_packages(query2)
    elif user_input =='2':
        id_values = input("Enter Package ID to delete from the table, Enter comma-separated package Ids if there are multiple packages\nPackage ID(s): ")
        if id_values:
            Check_packages(f"Select count(*) as total_invoice_lines from icust_owner.t_compass_invoice_flat where package_id in ({id_v})")    
            
            
    else:
        print("aa")

 

conn.close()
