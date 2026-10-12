from collections import Counter

def validate(rows, contract):
    errors=[]
    for index,row in enumerate(rows):
        for name,kind in contract['fields'].items():
            if name not in row:
                errors.append({'row':index,'field':name,'error':'missing'})
            elif kind=='integer' and (type(row[name]) is not int):
                errors.append({'row':index,'field':name,'error':'type'})
            elif kind=='string' and not isinstance(row[name],str):
                errors.append({'row':index,'field':name,'error':'type'})
    return {'valid':not errors,'errors':errors,'row_count':len(rows)}

def profile(rows, field):
    values=[row.get(field) for row in rows]
    return {'rows':len(values),'nulls':sum(v is None for v in values),'distinct':len(set(map(str,values))),'top':Counter(map(str,values)).most_common(5)}
