from .exceptions import ItopError
from .parallel import tmap


class Schema(object):
    def __init__(self, itop, name):
        self.itop = itop
        self.name = name

    def to_oql(self, query):
        """
        Convert a query object to OQL WHERE clause.
        :param query: Specifies selection filter.
        :return: oql string with WHERE clause specified by filter.
        """
        if 'id' in query:
            return query['id']

        oql = "SELECT %s " % self.name
        if len(query):
            oql += "WHERE " + " AND ".join(['%s LIKE "%s"' % (k, query[k]) for k in query])
        return oql

    def find(self, query=None, projection=None):
        """
        Selects objects in a schema.
        :param query: Optional. Specifies selection filter. To return all objects in a schema,
            omit this parameter or pass an empty object ({}).
        :param projection: Optional. Specifies the fields to return in the objects that match the query filter.
            To return all fields in the matching objects, omit this parameter.
        :return:
        """
        query = query if query else {}
        if not isinstance(query, dict):
            raise TypeError("Query must be a dict")

        projection = projection if projection else []
        if not isinstance(projection, list):
            raise TypeError("Projection must be a list")

        if len(projection):
            output_fields = ", ".join(projection)
        else:
            output_fields = "*+"

        key = self.to_oql(query)

        data = {
            'operation': 'core/get',
            'comment': 'Get ' + self.name,
            'class': self.name,
            'key': key,
            'output_fields': output_fields
        }

        response = self.itop.request(data)

        if projection:
            output = [{k: v for k, v in obj.items() if k in projection} for obj in response]
        else:
            output = response

        if isinstance(output, list) and len(output) == 1:
            output = output[0]

        if isinstance(output, dict) and len(output) == 1:
            _, output = list(output.items())[0]

        return output

    def insert(self, objs, workers=10):
        """
        Inserts a object or objects into a schema.
        :param objs: A object or list of objects to insert into the schema.
        :param workers: Optional. If set to greater than 1, creates objects in parallel requests. default is serial(1).
        :return: inserted objects.
        """

        if not (isinstance(objs, dict) or isinstance(objs, list)):
            raise TypeError("Query must be a object or list of objects")
        objs = objs if isinstance(objs, list) else [objs]

        # reserved words starts with '_' so remove this;
        # remove empty fields
        clean = lambda k: k[1:] if k[0] == '_' else k
        objs = [{clean(k): v for k, v in obj.items() if v} for obj in objs]

        if self.itop.data_model:
            objs = [self.lookup(obj) for obj in objs]

        datas = [
            {
                'operation': 'core/create',
                'comment': 'Create' + self.name,
                'class': self.name,
                'output_fields': "*",
                'fields': obj
            } for obj in objs
        ]

        output = tmap(self.itop.request, datas, workers=workers)
        output = [item for result in output for item in result]

        if isinstance(output, list) and len(output) == 1:
            output = output[0]

        if isinstance(output, dict) and len(output) == 1:
            _, output = list(output.items())[0]

        return output

    def update(self, query, update, upsert=False, multi=False):
        """
        Modifies an existing object or objects in a schema. The method can modify specific fields of an existing
        object or objects or replace an existing object entirely, depending on the update parameter.

        By default, the update() method updates a single object. Set the Multi Parameter to update all objects that
        match the query criteria.

        Update() method can insert a object when query criteria not returns data if upsert property is True.

        :param query: The selection criteria for the update.
        :param update: The modifications to apply.
        :param upsert: Optional. If set to true, creates a new object when no object matches the query criteria.
            The default value is false, which does not insert a new object when no match is found.
        :param multi: Optional. If set to true, updates multiple objs that meet the query criteria.
            If set to false, updates one object. The default value is false.
        :return: List of Elements
        """
        query = query if query else {}
        if not isinstance(query, dict):
            raise TypeError("Query must be a dict")

        update = update if update else {}
        if not isinstance(update, dict):
            raise TypeError("Query must be a dict")

        key = self.to_oql(query)

        if self.itop.data_model:
            update = self.lookup(update)

        update_data = {
            'operation': 'core/update',
            'comment': 'Update ' + self.name,
            'class': self.name,
            'output_fields': "*",
            'fields': update,
            'key': key
        }

        try:
            return self.itop.request(update_data)
        except ItopError as e:
            if 'Several items' in str(e):
                if multi:
                    objs = self.find(query)
                    output = tmap(lambda obj: self.update(obj, update, upsert, multi), objs)
                    output = [item for result in output for item in result]

                    if isinstance(output, list) and len(output) == 1:
                        output = output[0]

                    if isinstance(output, dict) and len(output) == 1:
                        _, output = list(output.items())[0]

                    return output
                raise e

            if 'No item found for query' in str(e):
                if upsert:
                    return self.insert({**query, **update})
                return {}
            raise e

    def remove(self, query):
        """

        :param query: Specifies deletion criteria. To delete all objects in a schema, pass an empty object ({}).
        :return:
        """

        query = query if query else {}
        if not isinstance(query, dict):
            raise TypeError("Query must be a dict")

        key = self.to_oql(query)

        data = {
            'operation': 'core/delete',
            'comment': 'Delete ' + self.name,
            'class': self.name,
            'key': key
        }
        output = self.itop.request(data)

        if isinstance(output, list) and len(output) == 1:
            output = output[0]

        if isinstance(output, dict) and len(output) == 1:
            _, output = list(output.items())[0]

        return output

    def sync(self, objs, keys=None, workers=10):
        """

        :param objs: A object or list of objects to insert into the schema
        :param keys:  Specifies a filter key list from object.
        :param workers: Optional. If set to greater than 1, creates objects in parallel requests. If is 1 is serial.
            default is 10.
        :return:
        """

        if not keys:
            keys = ['name']

        if not (isinstance(objs, list)):
           objs = [objs]

        def step(obj):
            query = dict([(field, obj[field]) for field in obj if field in keys])
            return self.update(query, obj, upsert=True, multi=False)

        results = tmap(step, objs, workers=workers)
        output = [item for result in results if result for item in result]

        if isinstance(output, list) and len(output) == 1:
            output = output[0]

        if isinstance(output, dict) and len(output) == 1:
            _, output = list(output.items())[0]

        return output

    def lookup(self, obj):
        """

        Quando existir um campo externo no corpo do objeto, convertê-lo para uma chave externa.
        Isso é necessário pois a API do iTop não inclui/atualiza itens contendo um campo externo,
        somente com chave externa

        :param obj:
        :return:
        """

        schema_lookups = self.itop.data_model.lookupExternalField(self.name)
        obj_lookups = [field for field in obj if field in schema_lookups]
        for field in obj_lookups:
            old_value = obj[field]
            external_key, lookup_class, lookup_field = schema_lookups[field]
            if old_value:
                value = self.itop.schema(lookup_class).find({lookup_field: old_value}, ['id'])
                if value == [] or value == '':
                    raise ValueError(
                        'Lookup field Error. ' +
                        'From: field "%s", value "%s", key "%s", schema "%s" To: field "%s" on schema "%s"' %
                        (field, old_value, external_key, self.name, lookup_field, lookup_class))
            else:
                value = None
            obj[external_key] = value
            del obj[field]

        schema_external_keys = list(set([v[0] for _, v in schema_lookups.items()]))
        obj_external_keys = [field for field in obj if field in schema_external_keys]
        for field in obj_external_keys:
            if not obj[field]:
                del obj[field]

        schema_LinkedSets = self.itop.data_model.lookupLinkedSet(self.name)
        obj_linked_sets = [field for field in obj if field in schema_LinkedSets]
        for field_obj_linked_sets in obj_linked_sets:
            for i, _ in enumerate(obj[field_obj_linked_sets]):
                child_obj = obj[field_obj_linked_sets][i]
                linked_class, ext_key_to_me, ext_key_to_remote = schema_LinkedSets[field_obj_linked_sets]
                linked_sets_lookups = self.itop.data_model.lookupExternalField(linked_class)
                obj_linked_set_lookups = [field for field in child_obj if field in linked_sets_lookups]
                for field in obj_linked_set_lookups:
                    old_value = child_obj[field]
                    external_key, lookup_class, lookup_field = linked_sets_lookups[field]
                    if old_value:
                        value = self.itop.schema(lookup_class).find({lookup_field: old_value}, ['id'])
                        if value == [] or value == '':
                            raise ValueError(
                                'Lookup field Error. ' +
                                'From: field "%s", value "%s", key "%s", schema "%s" To: field "%s" on schema "%s"' %
                                (field, old_value, external_key, self.name, lookup_field, lookup_class))
                    else:
                        value = None
                    obj[field_obj_linked_sets][i][external_key] = value
                    del obj[field_obj_linked_sets][i][field]

        return obj


