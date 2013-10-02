from DatabaseClient import DatabaseClient
client = DatabaseClient(hostname=None)
client('drop btable dan_kiva;')
client('create btable dan_kiva from data/kiva.csv;')
client('import samples data/kiva_flat_table_model_500.pkl.gz into dan_kiva iterations 500;')
print client('select * from dan_kiva limit 5;')



fields_of_interest = [
    'due_diligence_type',
    'delinquency_rate',
    'partner_status',
    'partner_rating',
    'delinquent',
    'default_rate',
    'loan_amount',
    'gender_ratio',
    ]
fields_str = ', '.join(fields_of_interest)

cmds = []
cmds.append('estimate dependence probabilities from dan_kiva save to dankiva_fz;')
# cmds.append('estimate dependence probabilities from dan_kiva referencing activity;')
#
return_values = []
for cmd in cmds:
    print '>>> %s' % cmd
    return_value = client.execute(cmd, pretty=False)
    return_values.append(return_value)

filename = 'dan_kiva'
dir = '/home/sgeadmin/'
client.gen_feature_z('dan_kiva', filename=filename, dir=dir)
hostname = 'sgeadmin@ec2-184-73-61-8.compute-1.amazonaws.com'
print
print 'scp %s:%s/%s.png .' % (hostname, dir, filename)
print
print 'bqldemomachine729'
