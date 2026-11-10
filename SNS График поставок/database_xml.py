"""XML transfer for the application schedule database."""
import math
import xml.etree.ElementTree as ET

FIELDS=('frequency','days','minimum','source','companion_limit','updated_at')

def serialize(db):
    root=ET.Element('sns_schedule',version='1')
    settings=ET.SubElement(root,'settings')
    row=db.execute('SELECT companion_limit FROM schedule_settings WHERE id=1').fetchone()
    ET.SubElement(settings,'companion_limit').text=str(row[0] if row else 5)
    records=ET.SubElement(root,'records')
    for chain,key,frequency,days,minimum,source,limit,updated in db.execute('SELECT chain,address_key,frequency,days,minimum,recommended_source,companion_limit,updated_at FROM schedule_recommendations ORDER BY chain,address_key'):
        item=ET.SubElement(records,'record',chain=chain)
        values=(key,frequency,days,minimum,source,limit,updated)
        for name,value in zip(('address_key',)+FIELDS,values):
            child=ET.SubElement(item,name)
            if value is not None:child.text=str(value)
    return ET.tostring(root,encoding='utf-8',xml_declaration=True)

def parse(data,valid_value,chains):
    import json
    if b'<!DOCTYPE' in data.upper() or b'<!ENTITY' in data.upper():raise ValueError('Недопустимые объявления в XML')
    try:root=ET.fromstring(data)
    except ET.ParseError as exc:raise ValueError('Некорректный XML') from exc
    if root.tag!='sns_schedule' or root.get('version')!='1':raise ValueError('Это не XML базы графика поставок')
    settings=root.find('settings');items=root.find('records')
    if settings is None or items is None:raise ValueError('В XML отсутствуют настройки или записи')
    try:setting=int(settings.findtext('companion_limit','5'))
    except ValueError:raise ValueError('Некорректное количество попутчиков')
    if not 0<=setting<=1000:raise ValueError('Некорректное количество попутчиков')
    if len(items)>100000:raise ValueError('Слишком много записей')
    result=[];seen=set()
    for item in items:
        if item.tag!='record':raise ValueError('Некорректная запись')
        chain=item.get('chain');key=item.findtext('address_key','')
        if chain not in chains or not key or len(key)>4000 or (chain,key) in seen:raise ValueError('Некорректный или повторяющийся адрес')
        seen.add((chain,key))
        try:
            frequency=int(item.findtext('frequency',''))
            days=json.loads(item.findtext('days',''))
            text=item.findtext('minimum','');minimum=float(text) if text else None
            limittext=item.findtext('companion_limit','');limit=int(limittext) if limittext else None
        except (ValueError,TypeError,json.JSONDecodeError) as exc:raise ValueError('Некорректные данные рекомендации') from exc
        frequency,days,minimum=valid_value({'frequency':frequency,'days':days,'minimum':minimum})
        source=item.findtext('source','');updated=item.findtext('updated_at','')
        if len(source)>300 or len(updated)>40 or (limit is not None and not 0<=limit<=1000):raise ValueError('Некорректные данные рекомендации')
        result.append((chain,key,frequency,days,minimum,source,limit,updated))
    return setting,result
