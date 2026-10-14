"""Guard against accidentally provisioning over an existing Oracle installation."""
import importlib.util
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location('retail_provision',Path(__file__).resolve().parents[2]/'scripts/retail_case_install/provision_oracle.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class Cursor:
    def __init__(self, objects=0, users=0, services=0, container='XEPDB1', service='orcl'):
        self.objects=objects;self.users=users;self.services=services
        self.container=container;self.service=service;self.calls=[]
    def execute(self, sql):
        self.calls.append(sql)
        if 'CON_NAME' in sql:self.answer=(self.container,self.service)
        elif 'dba_objects' in sql:self.answer=(self.objects,)
        elif 'dba_users' in sql:self.answer=(self.users,)
        elif 'dba_services' in sql:self.answer=(self.services,)
        else:self.answer=None
    def fetchone(self):return self.answer


class Connection:
    def __init__(self, **kwargs):self.q=Cursor(**kwargs)
    def cursor(self):return self.q


class ProvisionGuards(unittest.TestCase):
    secret='R'+'A'*32
    def refused(self, connection, create=False):
        with self.assertRaises(RuntimeError):module.provision(connection,self.secret,create)
        self.assertTrue(all(sql.lower().startswith('select ') for sql in connection.q.calls))
    def test_nonempty_schema_is_read_only(self):self.refused(Connection(objects=1),True)
    def test_existing_empty_user_password_is_not_changed(self):self.refused(Connection(users=1),True)
    def test_existing_service_is_not_replaced(self):self.refused(Connection(services=1),True)
    def test_cdb_root_is_not_a_target(self):self.refused(Connection(container='CDB$ROOT'),True)
    def test_wrong_existing_service_is_refused(self):self.refused(Connection(service='other'))
    def test_password_cannot_inject_sql(self):
        c=Connection()
        with self.assertRaises(ValueError):module.provision(c,'x"; drop user RABAEV cascade;--',True)
        self.assertEqual(c.q.calls,[])


if __name__=='__main__':unittest.main()
