import json
import sqlite3
import uuid

import psycopg2

VERBOSE = False

def add_db_functions(*args, **kwargs):
    db_name = kwargs["db_name"]
    
    if "unique_indices" in kwargs:
        unique_indices = kwargs["unique_indices"]
    else:
        unique_indices = set()
    
    if "single_foreign" in kwargs:
        single_foreign = kwargs["single_foreign"]
    else:
        single_foreign = set()
        
    if "plural_foreign" in kwargs:
        plural_foreign = kwargs["plural_foreign"]
    else:
        plural_foreign = set()
    
    if "serial_set" in kwargs:
        serial_set = kwargs["serial_set"]
    else:
        serial_set = set()
    
    def decorator(cls):
        if "id" not in cls.__annotations__:
            raise Exception(f"{cls} does not have an id attribute!")
        
        var_list = list(cls.__annotations__.keys())
        var_list.remove('cur')
        if VERBOSE:
            print(var_list)
        
        @staticmethod
        def from_sql_tuple(sql_row):
            json_dict = {}
            for i, key in enumerate(var_list):
                json_dict[key] = sql_row[i]
            
            return cls.from_json_dict(json_dict)
        
        @staticmethod
        def set_cursor(cur: sqlite3.Cursor | psycopg2.extensions.cursor):
            if isinstance(cur, sqlite3.Cursor) or isinstance(cur, psycopg2.extensions.cursor):
                cls.cur = cur
            else:
                raise Exception(f"Unrecognized type {type(cur)} for a database cursor!")
        
        cls.set_cursor = set_cursor
        
        @staticmethod
        def all():
            cls.cur.execute(f"SELECT * FROM {db_name}")
            
            result = []
            for sql_line in cls.cur.fetchall():
                result.append(from_sql_tuple(sql_line))
            
            return result
        
        @staticmethod
        def exists(id: str | uuid.UUID):
            if isinstance(id, uuid.UUID):
                id = str(id)
            
            cls.cur.execute(f"SELECT * FROM {db_name} WHERE id=%s", (id,))
            return cls.cur.fetchone() is not None
        
        def delete(self):
            if exists(self.id):
                if VERBOSE:
                    print(cls.cur.mogrify(f"DELETE FROM {db_name} WHERE id = %s", (str(self.id),)))
                cls.cur.execute(f"DELETE FROM {db_name} WHERE id = %s", (str(self.id),))
        
        def save(self):
            x = self.to_json_dict()
            # x["updated_at"] = time.strftime("20%y-%m-%d %H:%M:%S%z", time.localtime())
            
            if exists(self.id):
                # (name1, name2 item3, ...)
                set_list = []
                # The actual values that will go in the final tuple
                attr_list = []
                for (key, val) in x.items():
                    if key == "id":
                        continue
                    if val is None:
                        continue
                    if key in serial_set:
                        continue
                    set_list.append(f"{key}=%s")
                    
                    if isinstance(val, str):
                        attr_list.append(val)
                    else:
                        attr_list.append(json.dumps(val))
                
                attr_list.append(str(self.id))
                command = f"UPDATE {db_name} SET " + ','.join(set_list) + f" WHERE id=%s;"
                cls.cur.execute(command, tuple(attr_list))
            else:
                # x["created_at"] = x["updated_at"]
                # (name1, name2 item3, ...)
                set_list = []
                # The actual values that will go in the final tuple
                attr_list = []
                
                for (key, val) in x.items():
                    # psycopg2 doesn't properly turn None into NULL
                    if val is None:
                        continue
                    if key in serial_set:
                        continue
                    
                    set_list.append(key)
                    
                    if key == "id":
                        attr_list.append(str(val))
                    elif isinstance(val, str):
                        attr_list.append(val)
                    else:
                        attr_list.append(json.dumps(val))
                
                question_tuple = ",".join(["%s" for _ in attr_list])
                command = f"INSERT INTO {db_name} (" + ','.join(set_list) + f") VALUES ({question_tuple});"
                if VERBOSE:
                    print(cls.cur.mogrify(command, tuple(attr_list)))
                cls.cur.execute(command, tuple(attr_list))
        
        @staticmethod
        def get_by_id(id: str | uuid.UUID):
            if isinstance(id, uuid.UUID):
                id = str(id)
            
            cls.cur.execute(f"SELECT * FROM {db_name} WHERE id=%s", (id,))

            sql_tuple = cls.cur.fetchone()
            if sql_tuple is None:
                raise Exception(cls.cur.mogrify(f"SELECT * FROM {db_name} WHERE id=%s", (id,)))
            return from_sql_tuple(sql_tuple)
        
        cls._db_name = db_name
        cls.all = all
        cls.exists = exists
        cls.save = save
        if not hasattr(cls, 'delete'):
            cls.delete = delete
        cls.get_by_id = get_by_id
        cls.from_sql_tuple = from_sql_tuple
        
        for unique_index in unique_indices:
            key = f"get_by_{'_'.join(unique_index)}"
            
            def get_by(*args):
                if len(args) != len(unique_index):
                    raise Exception(f"{key} takes exactly {len(unique_index)} argument ({len(args)} given)!")
                
                converted_args = [str(arg) for arg in args]
                
                where_clause = ' AND '.join([f"{index}=%s" for index in unique_index])
                
                command = f"SELECT * FROM {db_name} WHERE {where_clause} LIMIT 1"
                cls.cur.execute(command, converted_args)
                
                return from_sql_tuple(cls.cur.fetchone())
            
            def exists_by(*args):
                if len(args) != len(unique_index):
                    raise Exception(
                        f"exists_by_{'_'.join(unique_index)} takes exactly {len(unique_index)} argument ({len(args)} given)!")
                
                converted_args = [str(arg) for arg in args]
                
                where_clause = ' AND '.join([f"{index}=%s" for index in unique_index])
                
                command = f"SELECT * FROM {db_name} WHERE {where_clause} LIMIT 1"
                cls.cur.execute(command, converted_args)
                
                return cls.cur.fetchone() is not None
            
            setattr(cls, key, get_by)
            setattr(cls, f"exists_by_{'_'.join(unique_index)}", exists_by)
        
        # Defines the get_item functions for the class
        for (key_name, other_cls) in single_foreign:
            def get_item_by_name(key_name):
                def get_item(self):
                    command = f"SELECT {other_cls._db_name}.* FROM {db_name} JOIN {other_cls._db_name} ON {db_name}.{key_name}_id = {other_cls._db_name}.id WHERE {db_name}.id = %s"
                    
                    cls.cur.execute(command, (str(self.id),))
                    return other_cls.from_sql_tuple(cls.cur.fetchone())
                
                return get_item
            
            setattr(cls, f"get_{key_name}", get_item_by_name(key_name))

        
        for (key_name, item_name, other_cls) in plural_foreign:
            def get_items_by_name(key_name, other_cls):
                
                def get_item(self):
                    command = f"SELECT distinct on ({other_cls._db_name}.id) {other_cls._db_name}.* FROM {db_name} JOIN {other_cls._db_name} ON {db_name}.{key_name} = {other_cls._db_name}.id WHERE {other_cls._db_name}.id = %s;"
                    if VERBOSE:
                        print(cls.cur.mogrify(command, (str(getattr(self, key_name)),)))
                    cls.cur.execute(command, (str(getattr(self, key_name)),))
                    return other_cls.from_sql_tuple(cls.cur.fetchone())
                return get_item

            def get_items_using_where(key_name, other_cls):
                def get_items(id):
                    if isinstance(id, uuid.UUID):
                        id = str(id)
                    command = f"SELECT * FROM {db_name} WHERE {key_name} = %s"
                    cls.cur.execute(command, (id,))
                    if VERBOSE:
                        print(cls.cur.mogrify(command, (id,)))
                    return [cls.from_sql_tuple(sql_tuple) for sql_tuple in cls.cur.fetchall()]
                return get_items

            setattr(cls, f"get_{item_name}", get_items_by_name(key_name, other_cls))
            setattr(cls, f"all_where_{key_name}", get_items_using_where(key_name, other_cls))

        
        return cls
    
    return decorator
