# Oracle JSON arrays: замена элемента и ссылки

JSON_ARRAY_T.put(i, value) по умолчанию вставляет новый элемент и сдвигает остальные. Для изменения существующего элемента использовать put(i, value, true). Для независимой копии использовать clone; обычный get может сохранять ссылочную семантику. [Oracle 19c JSON guide](https://docs.oracle.com/en/database/oracle/oracle-database/19/adjsn/overview-of-pl-sql-object-types-for-json.html).

В059 replacement source-binding list нельзя расширять при добавлении release_quantity: дублирование reservation ID даёт повторное освобождение и конфликт версии. Ошибка в dev попытке откатилась всей root transaction, после явного overwrite full multi-target/partial-target cases прошли. Это правило для будущего кода, не повод менять все raw SQL источники или повторять всю приёмку.
